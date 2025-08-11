import sys
import os

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.report_generator import ReportGenerator


def main():
    if len(sys.argv) < 2:
        print("CIS AUDITOR - SESSION UTILITY")
        print("=" * 30)
        print("Usage:")
        print("  python utils/session_util.py list               # List all sessions")
        print("  python utils/session_util.py show <session_id>  # Show files for session")
        print()
        print("Available commands:")
        print("  list    - Show all available audit sessions")
        print("  show    - Show all files for a specific session")
        return

    command = sys.argv[1].lower()
    
    if command == "list":
        ReportGenerator.list_audit_sessions()
    elif command == "show":
        if len(sys.argv) < 3:
            print("Error: Please provide a session ID")
            print("Usage: python utils/session_util.py show <session_id>")
            return
        session_id = sys.argv[2]
        ReportGenerator.show_session_files(session_id)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, show")


if __name__ == "__main__":
    main()
