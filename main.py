import sys
from handlers.cli_handler import CLIHandler


def main():
    cli_handler = CLIHandler()
    cli_handler.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nAudit interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unhandled error occurred: {e}", file=sys.stderr)
        sys.exit(1)