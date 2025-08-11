import datetime
import os
from typing import List
from audit_task import AuditTask
from .report_formatters import TaskFormatter


class DetailedReporter:
    
    def __init__(self, tasks: List[AuditTask], session_id: str):
        self.tasks = tasks
        self.session_id = session_id
        parts = session_id.split('_')
        self.timestamp = f"{parts[0]}_{parts[1]}"  # YYYYMMDD_HHMMSS
        self.audit_id = parts[2] if len(parts) > 2 else "unknown"
        self.task_formatter = TaskFormatter()
    
    def gen_detailed_reports(self):
        details_base_dir = "reports/details"
        os.makedirs(details_base_dir, exist_ok=True)
        
        passed_tasks = [t for t in self.tasks if self.task_formatter.get_task_status(t) == "PASS"]
        failed_tasks = [t for t in self.tasks if self.task_formatter.get_task_status(t) == "FAIL"]
        error_tasks = [t for t in self.tasks if self.task_formatter.get_task_status(t) == "ERROR"]
        
        self.details_index(details_base_dir, passed_tasks, failed_tasks, error_tasks)
        
        if passed_tasks:
            self.status_report("PASS", passed_tasks, details_base_dir)
        if failed_tasks:
            self.status_report("FAIL", failed_tasks, details_base_dir)
        if error_tasks:
            self.status_report("ERROR", error_tasks, details_base_dir)
    
    def details_index(self, base_dir: str, passed_tasks: List[AuditTask], failed_tasks: List[AuditTask], error_tasks: List[AuditTask]):
        index_filename = f"audit_details_index_{self.session_id}.txt"
        index_path = os.path.join(base_dir, index_filename)
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("="*25 + " DETAILED AUDIT EVIDENCE INDEX " + "="*25 + "\n")
                f.write(f"Audit Session ID: {self.session_id}\n")
                f.write(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Checks Run: {len(self.tasks)}\n")
                f.write("="*78 + "\n\n")
                
                f.write("EVIDENCE REPORTS BY STATUS:\n")
                f.write("-" * 40 + "\n\n")
                
                if passed_tasks:
                    f.write(f"   PASS Folder: {len(passed_tasks)} checks\n")
                    f.write(f"   File: audit_pass_{self.session_id}_{len(passed_tasks)}_checks.txt\n")
                    f.write(f"   Status: All checks passed successfully\n\n")
                
                if failed_tasks:
                    f.write(f"   FAIL Folder: {len(failed_tasks)} checks\n")
                    f.write(f"   File: audit_fail_{self.session_id}_{len(failed_tasks)}_checks.txt\n")
                    f.write(f"   Status: Checks that failed validation\n\n")
                
                if error_tasks:
                    f.write(f"  ERROR Folder: {len(error_tasks)} checks\n")
                    f.write(f"   File: audit_error_{self.session_id}_{len(error_tasks)}_checks.txt\n")
                    f.write(f"   Status: Checks that encountered errors\n\n")
                
                f.write("NAVIGATION GUIDE:\n")
                f.write("-" * 20 + "\n")
                f.write("• Open the folder corresponding to the status you want to investigate\n")
                f.write("• Each folder contains a detailed report with full evidence for that status\n")
                f.write("• Check numbering starts fresh in each folder for easier navigation\n\n")
                
                # Quick summary by domain
                f.write("QUICK SUMMARY BY DOMAIN:\n")
                f.write("-" * 30 + "\n")
                domains = {}
                for task in self.tasks:
                    domain = task.domain or "General"
                    if domain not in domains:
                        domains[domain] = {"PASS": 0, "FAIL": 0, "ERROR": 0}
                    status = self.task_formatter.get_task_status(task)
                    if status in domains[domain]:
                        domains[domain][status] += 1
                
                for domain, results in domains.items():
                    total = sum(results.values())
                    f.write(f"{domain}: {results['PASS']} Pass, {results['FAIL']} Fail, {results['ERROR']} Error (Total: {total})\n")
            
            print(f"Details index created at '{index_path}'")
            
        except Exception as e:
            print(f"ERROR: Could not create details index. Reason: {e}")
    
    def status_report(self, status: str, tasks: List[AuditTask], base_dir: str):
        status_dir = os.path.join(base_dir, status)
        os.makedirs(status_dir, exist_ok=True)
        
        status_filename = f"audit_{status.lower()}_{self.session_id}_{len(tasks)}_checks.txt"
        status_path = os.path.join(status_dir, status_filename)
        
        try:
            with open(status_path, 'w', encoding='utf-8') as f:
                self._write_status_evidence_header(f, status, len(tasks))
                
                # Write each task's evidence
                for i, task in enumerate(tasks, 1):
                    f.write(f"\n{'='*80}\n")
                    f.write(f"CHECK #{i} of {len(tasks)}\n")
                    f.write(f"{'='*80}\n\n")
                    self.task_formatter.format_task_for_file(task, f)
                    
            print(f"{status} checks detailed report saved to '{status_path}' ({len(tasks)} checks)")
            
        except Exception as e:
            print(f"ERROR: Could not write {status} detailed report. Reason: {e}")
    
    def _write_status_evidence_header(self, f, status: str, count: int):
        f.write("="*25 + f" {status} AUDIT EVIDENCE " + "="*25 + "\n")
        f.write(f"Audit Session ID: {self.session_id}\n")
        f.write(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Total {status} Checks: {count}\n")
        f.write("="*73 + "\n")
