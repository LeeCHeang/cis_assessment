import argparse
import getpass
import sys
import logging
from handlers.log_handler import setup_logger
from utils.csv_parser import CISBenchmarkParser
from handlers.audit_handler import AuditHandler
from utils.remote_utils import RemoteExecutor
from utils.execution_utils import set_remote_executor, cls_remo_runner
from utils.report_generator import gsummary_report, gcsv_report, gorganized_reports


class CLIHandler:
    def __init__(self):
        self.logger = None
        self.args = None
    
    def flag_argument(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Run a CIS security audit from a CSV benchmark file."
        )
        
        # Main Flag arguments
        parser.add_argument('benchmark_file', help="The path to the CIS benchmark CSV file.")
        parser.add_argument('--profile', help="Run only checks for a specific profile.")
        parser.add_argument('--level', help="Run only checks for a specific level.")
        parser.add_argument('--domain', help="Run only checks for a specific domain.")
        parser.add_argument('--id', help="Run only a single check by its ID.")
        parser.add_argument('--format', choices=['txt', 'csv'], default='txt', help="The output format for the report (default: txt).")
        parser.add_argument('--loglevel', choices=['DEBUG', 'INFO'], default='INFO', help="Set the logging verbosity (default: INFO).")
        parser.add_argument('-A', '--show-all', action='store_true', help="Show details for all checks in console output, including PASS results (default: only show FAIL/ERROR).")

        # SSH arguments
        ssh_group = parser.add_argument_group('SSH Options', 'Arguments for remote auditing')
        ssh_group.add_argument('--ssh-host', help='The remote host IP address or hostname.')
        ssh_group.add_argument('-u', '--username', help='The SSH username for the remote host.')
        ssh_group.add_argument('--port', type=int, default=22, help='The SSH port (default: 22).')
        auth_group = ssh_group.add_mutually_exclusive_group()
        auth_group.add_argument('-p', '--ask-pass', action='store_true', help='Prompt for SSH password interactively.')
        auth_group.add_argument('-P', '--password', help='Provide the SSH password directly on the command line (less secure).')
        auth_group.add_argument('-i', '--identity-file', help='Path to the SSH private key file for authentication.')
        
        return parser
    
    def parse_arguments(self, args=None):
        parser = self.flag_argument()
        self.args = parser.parse_args(args)
        return self.args
    
    def setup_logging(self):
        self.logger = setup_logger(self.args.loglevel)
        return self.logger
    
    def validate_remote_args(self):
        if self.args.ssh_host and not self.args.username:
            print("Error: --username is required for SSH connections.", file=sys.stderr)
            sys.exit(1)
    
    def get_ssh_password(self) -> str:
        password = self.args.password
        if self.args.ask_pass:
            password = getpass.getpass(f"Enter password for {self.args.username}@{self.args.ssh_host}: ")
        return password
    
    def parse_tasks(self):
        try:
            csv_parser = CISBenchmarkParser(self.args.benchmark_file)
            tasks_to_run = csv_parser.filter_csv(
                level=self.args.level,
                profile=self.args.profile,
                domain=self.args.domain,
                task_id=self.args.id
            )
            return tasks_to_run
        except Exception as e:
            self.logger.critical(f"Failed to parse benchmark file. Error: {e}")
            return None
    
    def generate_reports(self, completed_tasks):
        gorganized_reports(completed_tasks, log_level=self.args.loglevel)
        
        gsummary_report(completed_tasks, log_level=self.args.loglevel, show_all=self.args.show_all)
        
        if self.args.format == 'csv':
            gcsv_report(completed_tasks)
    
    def run_remote_audit(self):
        self.validate_remote_args()
        password = self.get_ssh_password()
        
        self.logger.info(f"Starting REMOTE audit on host: {self.args.ssh_host}")

        # Parse and filter tasks
        tasks_to_run = self.parse_tasks()
        if tasks_to_run is None:
            return

        # Set up remote execution
        executor = RemoteExecutor(
            self.args.ssh_host, 
            self.args.port, 
            self.args.username, 
            password=password, 
            key_path=self.args.identity_file
        )
        
        if not executor.connect():
            self.logger.critical("Failed to connect to remote host. Exiting.")
            executor.disconnect()
            return 
        
        try:
            set_remote_executor(executor)
            
            audit_handler = AuditHandler()
            completed_tasks = audit_handler.run_audit(tasks_to_run, log_level=self.args.loglevel)
            
        finally:
            # Always clean up
            cls_remo_runner()
            executor.disconnect()
            
        self.generate_reports(completed_tasks)
        self.logger.info("Remote CIS Auditor run finished.")
    
    def run_local_audit(self):
        self.logger.info(f"Starting CIS Auditor with file: '{self.args.benchmark_file}'")
        
        tasks_to_run = self.parse_tasks()
        if tasks_to_run is None:
            return

        audit_handler = AuditHandler()
        completed_tasks = audit_handler.run_audit(tasks_to_run, log_level=self.args.loglevel)
        
        self.generate_reports(completed_tasks)
        self.logger.info("CIS Auditor run finished.")
    
    def run(self, args=None):
        self.parse_arguments(args)
        self.setup_logging()
        
        if self.args.ssh_host:
            self.run_remote_audit()
        else:
            self.run_local_audit()
