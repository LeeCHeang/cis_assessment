#!/usr/bin/env python3
"""
Test script to verify the --show-all functionality works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_task import AuditTask
from utils.console_reporter import ConsoleReporter

def create_test_task(task_id, title, status="PASS", evidence="Sample command output"):
    """Create a test task with mock data."""
    task = AuditTask(
        id=task_id,
        level="L1",
        profile=["Server"],
        domain="System Settings",
        title=title,
        check_type="command_output",
        target="echo 'test'",
        parameters={},
        algorithm="Exact",
        expected_value="test"
    )
    
    # Mock result with details
    task.final_result = {
        "type": "action_node",
        "overall_status": status,
        "details": {
            "reason": f"Check {status.lower()}ed successfully" if status == "PASS" else f"Check failed: expected 'test' but got 'wrong'",
            "evidence": evidence,
            "error": None if status == "PASS" else f"Mismatch detected"
        }
    }
    
    return task

def test_show_all_functionality():
    """Test the show_all functionality."""
    print("Testing --show-all functionality\n")
    
    # Create test tasks
    tasks = [
        create_test_task("1.1.1", "Test Check 1 (PASS)", "PASS", "test\nexpected output found"),
        create_test_task("1.1.2", "Test Check 2 (FAIL)", "FAIL", "wrong\noutput mismatch"),
        create_test_task("1.1.3", "Test Check 3 (PASS)", "PASS", "test\nanother successful check")
    ]
    
    print("=" * 60)
    print("Testing without --show-all (should only show FAIL details):")
    print("=" * 60)
    
    reporter1 = ConsoleReporter(tasks, 'INFO')
    reporter1.generate_summary(show_all=False)
    
    print("\n" + "=" * 60)
    print("Testing with --show-all (should show ALL details including PASS):")
    print("=" * 60)
    
    reporter2 = ConsoleReporter(tasks, 'INFO')
    reporter2.generate_summary(show_all=True)

if __name__ == "__main__":
    test_show_all_functionality()
