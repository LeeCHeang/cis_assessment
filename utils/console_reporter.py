import datetime
from typing import List
from audit_task import AuditTask
from .report_formatters import Colors, TaskFormatter


class ConsoleReporter:
    
    def __init__(self, tasks: List[AuditTask], log_level: str = 'INFO'):
        self.tasks = tasks
        self.log_level = log_level
        # Don't initialize task_formatter here yet, since we need show_all parameter
        
        self.pass_count = self._count_by_status("PASS")
        self.fail_count = self._count_by_status("FAIL") 
        self.error_count = self._count_by_status("ERROR")
    
    def _count_by_status(self, status: str) -> int:
        # Create a temporary formatter just for counting
        temp_formatter = TaskFormatter(self.log_level, False)
        return len([
            t for t in self.tasks 
            if temp_formatter.get_task_status(t) == status
        ])
    
    def _should_show_in_console(self, status: str, show_all: bool) -> bool:
        return (self.log_level == 'DEBUG' or show_all or status in ["FAIL", "ERROR"])
    
    def generate_summary(self, show_all: bool = False):
        # Initialize task_formatter with the show_all parameter
        self.task_formatter = TaskFormatter(self.log_level, show_all)
        self._print_summary_header()
        self._print_console_details(show_all)
    
    def _print_summary_header(self):
        print("\n" + Colors.BOLD + "="*25 + " AUDIT SUMMARY " + "="*25 + Colors.ENDC)
        print(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Checks Run: {len(self.tasks)}")
        
        results_line = (f"RESULTS: {Colors.OKGREEN}{self.pass_count} Passed{Colors.ENDC}, "
                       f"{Colors.FAIL}{self.fail_count} Failed{Colors.ENDC}, "
                       f"{Colors.WARNING}{self.error_count} Errored{Colors.ENDC}.")
        print(Colors.BOLD + results_line + Colors.ENDC)
        print(f"{Colors.BOLD}="*67 + Colors.ENDC)
    
    def _print_console_details(self, show_all: bool):
        if self.log_level == 'DEBUG':
            print(f"\nDETAILS FOR ALL CHECKS (DEBUG MODE):\n")
        elif show_all:
            print(f"\nDETAILS FOR ALL CHECKS:\n")
        else:
            print(f"\nDETAILS FOR FAILED AND ERRORED CHECKS:\n")

        for task in self.tasks:
            status = self.task_formatter.get_task_status(task)
            if self._should_show_in_console(status, show_all):
                self.task_formatter.format_task_for_console(task)
