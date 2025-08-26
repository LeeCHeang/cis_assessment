import datetime
import os
import csv
import uuid
from typing import List, Dict, Any
from audit_task import AuditTask
import logging

from .console_reporter import ConsoleReporter
from .summary_reporter import SummaryReporter
from .detailed_reporter import DetailedReporter
from .csv_reporter import CSVReporter, LegacyReporter
from .report_formatters import Colors


class ReportGenerator:
    def __init__(self, tasks: List[AuditTask], log_level: str = 'INFO'):
        self.tasks = tasks
        self.log_level = log_level
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.audit_id = str(uuid.uuid4())[:8]  # Short 8-character ID
        self.session_id = f"{self.timestamp}_{self.audit_id}"
        
        self.console_reporter = ConsoleReporter(tasks, log_level)
        self.summary_reporter = SummaryReporter(tasks, self.session_id)
        self.detailed_reporter = DetailedReporter(tasks, self.session_id)
        self.csv_reporter = CSVReporter(tasks, self.session_id)
        self.legacy_reporter = LegacyReporter(tasks, self.session_id)
        
        # Calculate summary statistics for backward compatibility
        self.pass_count = self.console_reporter.pass_count
        self.fail_count = self.console_reporter.fail_count
        self.error_count = self.console_reporter.error_count
    
    @staticmethod
    def show_session_files(session_id: str):
        import glob
        
        related_files = []
        patterns = [f"reports/**/*{session_id}*"]
        
        for pattern in patterns:
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path):  # Only files, not directories
                    related_files.append(file_path)
        
        if related_files:
            print(f"\n Files for Session: {session_id}")
            print("=" * 50)
            for file_path in sorted(related_files):
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                folder = os.path.dirname(file_path).replace("reports\\", "").replace("reports/", "")
                print(f" {filename}")
                print(f"    {folder}")
                print(f"    {file_size:,} bytes")
                print()
        else:
            print(f" No files found for session: {session_id}")
    
    @staticmethod
    def list_audit_sessions():
        import glob
        import re
        
        session_ids = set()
        session_pattern = r'(\d{8}_\d{6}_[a-f0-9]{8})'
        
        # Search in reports directory
        for pattern in ["reports/**/*.txt", "reports/**/*.csv"]:
            for file_path in glob.glob(pattern, recursive=True):
                filename = os.path.basename(file_path)
                matches = re.findall(session_pattern, filename)
                session_ids.update(matches)
        
        sorted_sessions = sorted(list(session_ids))
        
        if sorted_sessions:
            print(f"\n Available Audit Sessions ({len(sorted_sessions)}):")
            print("-" * 40)
            for i, session_id in enumerate(sorted_sessions, 1):
                print(f"{i:2d}. {session_id}")
            print("-" * 40)
            print(f" Latest session: {sorted_sessions[-1]}")
            print(" Use session ID to identify related reports across all folders")
        else:
            print(" No audit sessions found in reports directory")
        
        return sorted_sessions
    
    def generate_console_summary(self, show_all: bool = False):
        self.console_reporter.generate_summary(show_all)
    
    def generate_organized_reports(self):
        self.summary_reporter.generate_summary_report()
        self.detailed_reporter.gen_detailed_reports()
    
    def generate_csv_report(self):
        self.csv_reporter.generate_csv_report()
    
    def generate_legacy_summary_file(self, show_all: bool = False):
        self.legacy_reporter.generate_legacy_summary_file(show_all)
    
    # Legacy methods for backward compatibility
    def _get_task_status(self, task: AuditTask) -> str:
        return self.console_reporter.task_formatter.get_task_status(task)
    
    def _count_by_status(self, status: str) -> int:
        return self.console_reporter._count_by_status(status)
    
    def _should_show_in_console(self, status: str, show_all: bool) -> bool:
        return self.console_reporter._should_show_in_console(status, show_all)


def gsummary_report(tasks: List[AuditTask], log_level: str = 'INFO', show_all: bool = False):
    generator = ReportGenerator(tasks, log_level)
    generator.generate_console_summary(show_all)
    generator.generate_legacy_summary_file(show_all)


def gcsv_report(tasks: List[AuditTask]):
    generator = ReportGenerator(tasks)
    generator.generate_csv_report()


def gorganized_reports(tasks: List[AuditTask], log_level: str = 'INFO'):
    generator = ReportGenerator(tasks, log_level)
    generator.generate_organized_reports()


# old function
def format_tree_file(node: Dict[str, Any], log_level: str, prefix: str = "", is_last: bool = True) -> str:
    from .report_formatters import TreeFormatter
    formatter = TreeFormatter(log_level)
    return formatter.format_for_file(node, prefix, is_last)


def detail_report_show(node: Dict[str, Any], log_level: str, prefix: str = "", is_last: bool = True):
    from .report_formatters import TreeFormatter
    formatter = TreeFormatter(log_level)
    formatter.format_for_console(node, prefix, is_last)