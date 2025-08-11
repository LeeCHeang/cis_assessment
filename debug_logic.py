
import argparse
# from handlers.log_handler import setup_logger
from utils.csv_parser import CISBenchmarkParser
from handlers.audit_handler import AuditHandler
# Import both report generators
from utils.report_generator import gsummary_report, gcsv_report

def main():
    # logger = setup_logger()
    
    parser = argparse.ArgumentParser(description="Run a CIS security audit from a CSV benchmark file.")
    parser.add_argument('benchmark_file', help="The path to the CIS benchmark CSV file.")
    parser.add_argument(
        '--format', 
        choices=['txt', 'csv'], 
        default='txt', 
        help="The output format for the report (default: txt)."
    )
    parser.add_argument(
        '--loglevel',
        choices=['DEBUG', 'INFO'],
        default='INFO',
        help="Set the logging verbosity (default: INFO)."
    )
    args = parser.parse_args()
    
    # Setup logger with the level from the command line
    # logger = setup_logger(args.loglevel)
    
    # logger.info(f"Starting CIS Auditor with file: '{args.benchmark_file}'")
    try:
        csv_parser = CISBenchmarkParser(args.benchmark_file)
        tasks_to_run = csv_parser.parse_csv()
    except Exception as e:
        # logger.critical(f"Failed to parse benchmark file. Error: {e}")
        return

    audit_handler = AuditHandler()
    completed_tasks = audit_handler.run_audit(tasks_to_run)
    
    # Generate the standard text summary every time
    gsummary_report(completed_tasks)
    
    # Generate the detailed report based on the chosen format
    # if args.format == 'csv':
    #     generate_csv_report(completed_tasks)
    # # could add 'elif args.format == 'excel':' here in the future
    
    # logger.info("Application finished.")


if __name__ == "__main__":
    main()