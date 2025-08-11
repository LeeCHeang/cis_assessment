# CIS Auditor v3.3 - Remote Edition

A comprehensive CIS (Center for Internet Security) audit tool that supports both local and remote system auditing via SSH.

## Features

- **Local Auditing**: Run CIS benchmark checks on the local system
- **Remote Auditing**: Execute CIS checks on remote Linux systems via SSH
- **Multiple Authentication**: Support for password and SSH key authentication
- **Flexible Reporting**: Generate reports in TXT or CSV format
- **Targeted Auditing**: Filter checks by level, profile, domain, or specific ID
- **Detailed Logging**: Configurable logging levels (INFO/DEBUG)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have the CIS benchmark CSV file in the `benchmarks/` directory

## Running an Audit

### Local Audit
To run the auditor on the local system (requires sudo for root permissions):

```bash
sudo python3 main.py benchmarks/cis_benchmark.csv
```

### Remote Audit
To run the auditor on a remote system via SSH:

#### Basic Remote Audit with Password
```bash
python main.py benchmarks/cis_benchmark.csv --ssh-host 192.168.1.100 -u admin --ask-pass
```

#### Remote Audit with SSH Key
```bash
python main.py benchmarks/cis_benchmark.csv --ssh-host 192.168.1.100 -u admin -i ~/.ssh/id_rsa
```

#### Remote Audit with Filters
```bash
python main.py benchmarks/cis_benchmark.csv --ssh-host 192.168.1.100 -u admin --ask-pass --level L1 --profile Server
```

## Command Line Options

### Required Arguments
- `benchmark_file`: Path to the CIS benchmark CSV file

### SSH Options (for remote auditing)
- `--ssh-host`: Remote host IP address or hostname
- `-u, --username`: SSH username for the remote host
- `--port`: SSH port (default: 22)

### Authentication Options (choose one)
- `--ask-pass`: Prompt for SSH password interactively (recommended)
- `-P, --password`: Provide SSH password on command line (less secure)
- `-i, --identity-file`: Path to SSH private key file

### Filtering Options
- `--profile`: Run only checks for a specific profile
- `--level`: Run only checks for a specific level (L1, L2)
- `--domain`: Run only checks for a specific domain
- `--id`: Run only a single check by its ID

### Output Options
- `--format`: Output format - `txt` or `csv` (default: txt)
- `--loglevel`: Logging verbosity - `INFO` or `DEBUG` (default: INFO)

## Testing Remote Connection

Before running a full audit, test your remote connection:

```bash
python test_remote_connection.py 192.168.1.100 -u admin --ask-pass
```

## Examples

See `remote_audit_examples.py` for comprehensive usage examples.

## Security Considerations

- Always use `--ask-pass` instead of `-P` for better security
- SSH key authentication is more secure than password authentication
- Results are generated locally on your Windows machine
- SSH connections are established over encrypted channels
- The remote user should have appropriate permissions to run system checks

## File Structure

