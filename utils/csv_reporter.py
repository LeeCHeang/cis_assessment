import datetime
import os
import csv
from typing import List
from audit_task import AuditTask
from .report_formatters import TaskFormatter


class CSVReporter:
    
    def __init__(self, tasks: List[AuditTask], session_id: str):
        self.tasks = tasks
        self.session_id = session_id
        parts = session_id.split('_')
        self.timestamp = f"{parts[0]}_{parts[1]}"  # YYYYMMDD_HHMMSS
        self.audit_id = parts[2] if len(parts) > 2 else "unknown"
        self.task_formatter = TaskFormatter()
    
    def generate_csv_report(self):
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_filename = f"audit_report_{self.session_id}.csv"
        report_path = os.path.join(report_dir, report_filename)
        headers = ['ID', 'Title', 'Result', 'Details']
        
        try:
            with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for task in self.tasks:
                    status = self.task_formatter.get_task_status(task)
                    details = str(task.actual_output)
                    if isinstance(task.final_result, dict):
                        details = str(task.final_result)
                        
                    writer.writerow({
                        'ID': task.id,
                        'Title': task.title,
                        'Result': status,
                        'Details': details
                    })
            print(f"Detailed CSV report saved to '{report_path}'")
        except Exception as e:
            print(f"ERROR: Could not write CSV report. Reason: {e}")


class LegacyReporter:
    def __init__(self, tasks: List[AuditTask], session_id: str):
        self.tasks = tasks
        self.session_id = session_id
        # Extract timestamp and audit ID from session_id
        parts = session_id.split('_')
        self.timestamp = f"{parts[0]}_{parts[1]}"  # YYYYMMDD_HHMMSS
        self.audit_id = parts[2] if len(parts) > 2 else "unknown"
        self.task_formatter = TaskFormatter()
        
        # Calculate summary statistics
        self.pass_count = len([t for t in tasks if self.task_formatter.get_task_status(t) == "PASS"])
        self.fail_count = len([t for t in tasks if self.task_formatter.get_task_status(t) == "FAIL"])
        self.error_count = len([t for t in tasks if self.task_formatter.get_task_status(t) == "ERROR"])
    
    def generate_legacy_summary_file(self, show_all: bool = False):
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        file_report_path = os.path.join(report_dir, "audit_summary_report.txt")
        
        try:
            with open(file_report_path, 'w', encoding='utf-8') as f:
                f.write("="*25 + " AUDIT SUMMARY " + "="*25 + "\n")
                f.write(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Checks Run: {len(self.tasks)}\n")
                f.write(f"RESULTS: {self.pass_count} Passed, {self.fail_count} Failed, {self.error_count} Errored.\n")
                f.write("="*67 + "\n\n")
                
                f.write("DETAILS FOR ALL CHECKS:\n\n")  # Always show all in file
                
                for task in self.tasks:
                    status = self.task_formatter.get_task_status(task)
                    f.write(f"[{status}] - ID: {task.id} - {task.title}\n")
                    if isinstance(task.final_result, dict) and task.final_result.get("type") in ["logic_node", "action_node"]:
                        tree_output = self.task_formatter.tree_formatter.format_for_file(task.final_result)
                        f.write(tree_output)
                    elif isinstance(task.final_result, dict):
                        f.write(f"  '-- Details: {task.final_result.get('details', 'No details available.')}\n")
                    else:
                        f.write(f"  '-- Details: {task.actual_output}\n")
                    f.write("\n")
        except Exception as e:
            print(f"ERROR: Could not write summary report. Reason: {e}")
