import datetime
import os
from typing import List
from audit_task import AuditTask
from .report_formatters import TaskFormatter


class SummaryReporter:
    
    def __init__(self, tasks: List[AuditTask], session_id: str):
        self.tasks = tasks
        self.session_id = session_id
        # Extract timestamp and audit ID from session_id
        parts = session_id.split('_')
        self.timestamp = f"{parts[0]}_{parts[1]}"  # YYYYMMDD_HHMMSS
        self.audit_id = parts[2] if len(parts) > 2 else "unknown"
        self.task_formatter = TaskFormatter()
        
        # Calculate summary statistics
        self.pass_count = self._count_by_status("PASS")
        self.fail_count = self._count_by_status("FAIL") 
        self.error_count = self._count_by_status("ERROR")
    
    def _count_by_status(self, status: str) -> int:
        return len([
            t for t in self.tasks 
            if self.task_formatter.get_task_status(t) == status
        ])
    
    def generate_summary_report(self):
        summary_dir = "reports/summary"
        os.makedirs(summary_dir, exist_ok=True)
        
        summary_filename = f"audit_summary_{self.session_id}.txt"
        summary_path = os.path.join(summary_dir, summary_filename)
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                self._write_summary_header(f)
                self._write_category_summary(f)
                self._write_failed_summary(f)
                self._write_error_summary(f)
            
            print(f"Summary report saved to '{summary_path}'")
        except Exception as e:
            print(f"ERROR: Could not write summary report. Reason: {e}")
    
    def _write_summary_header(self, f):
        f.write("="*25 + " AUDIT SUMMARY " + "="*25 + "\n")
        f.write(f"Audit Session ID: {self.session_id}\n")
        f.write(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Checks Run: {len(self.tasks)}\n")
        f.write(f"RESULTS: {self.pass_count} Passed, {self.fail_count} Failed, {self.error_count} Errored.\n")
        f.write("="*67 + "\n\n")
    
    def _write_category_summary(self, f):
        categories = {}
        for task in self.tasks:
            domain = task.domain or "General"
            if domain not in categories:
                categories[domain] = {"PASS": 0, "FAIL": 0, "ERROR": 0}
            
            status = self.task_formatter.get_task_status(task)
            if status in categories[domain]:
                categories[domain][status] += 1
        
        f.write("RESULTS BY CATEGORY:\n")
        for category, results in categories.items():
            total = sum(results.values())
            f.write(f"  {category}: {results['PASS']} Pass, {results['FAIL']} Fail, {results['ERROR']} Error (Total: {total})\n")
    
    def _write_failed_summary(self, f):
        f.write(f"\nFAILED CHECKS SUMMARY:\n")
        for task in self.tasks:
            if self.task_formatter.get_task_status(task) == "FAIL":
                f.write(f"  - {task.id}: {task.title}\n")
    
    def _write_error_summary(self, f):
        if self.error_count > 0:
            f.write(f"\nERRORED CHECKS SUMMARY:\n")
            for task in self.tasks:
                if self.task_formatter.get_task_status(task) == "ERROR":
                    f.write(f"  - {task.id}: {task.title}\n")
