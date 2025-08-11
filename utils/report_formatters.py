from typing import Dict, Any
from utils.color_utils import Colors


class TreeFormatter:
    def __init__(self, log_level: str = 'INFO', show_all: bool = False):
        self.log_level = log_level
        self.show_all = show_all
    
    def format_for_console(self, node: Dict[str, Any], prefix: str = "", is_last: bool = True):
        connector = "   '-- " if is_last else "   |-- "
        status = node.get("overall_status", "ERROR")
        status_color = Colors.OKGREEN if status == "PASS" else (Colors.FAIL if status == "FAIL" else Colors.WARNING)

        if node.get("type") == "logic_node":
            logic = node.get("logic")
            print(f"{prefix}{connector}[{status_color}**{Colors.ENDC}] LOGIC GROUP ({logic})")
        else:
            title = node.get("title", "Untitled Step")
            print(f"{prefix}{connector}[{status_color}*{status}*{Colors.ENDC}] STEP: {title}")
        
        child_prefix = prefix + ("    " if is_last else "   |")
        self._print_action_details(node, child_prefix)
        
        # Process child steps
        steps_results = node.get("steps_results", [])
        for i, step in enumerate(steps_results):
            self.format_for_console(step, child_prefix, i == len(steps_results) - 1)
    
    def _print_action_details(self, node: Dict[str, Any], prefix: str):
        if node.get("type") == "action_node":
            details = node.get("details", {})
            reason = details.get("reason")
            error = details.get("error")
            evidence = details.get("evidence")

            if error:
                print(f"{prefix}     '-- Reason: {error}")
                # Show details for DEBUG mode, or when show_all is True for any status
                if self.log_level == 'DEBUG' or self.show_all:
                    print(f"{prefix}          '-- Details_Output: {evidence}")
            elif reason:
                print(f"{prefix}     '-- Reason: {reason}")
                # Show details for DEBUG mode, or when show_all is True for any status
                if self.log_level == 'DEBUG' or self.show_all:
                    print(f"{prefix}          '-- Details_Output: {evidence}")
            else:
                print(f"{prefix}       '-- Details: {details}")
    
    def format_for_file(self, node: Dict[str, Any], prefix: str = "", is_last: bool = True) -> str:
        result = ""
        connector = "   '-- " if is_last else "   |-- "
        status = node.get("overall_status", "ERROR")

        if node.get("type") == "logic_node":
            logic = node.get("logic")
            result += f"{prefix}{connector}[**] LOGIC GROUP ({logic})\n"
        else:
            title = node.get("title", "Untitled Step")
            result += f"{prefix}{connector}[*{status}*] STEP: {title}\n"
        
        child_prefix = prefix + ("    " if is_last else "   |")
        result += self._format_action_details_for_file(node, child_prefix)
        
        # Process child steps
        steps_results = node.get("steps_results", [])
        for i, step in enumerate(steps_results):
            result += self.format_for_file(step, child_prefix, i == len(steps_results) - 1)
        
        return result
    
    def _format_action_details_for_file(self, node: Dict[str, Any], prefix: str) -> str:
        result = ""
        if node.get("type") == "action_node":
            details = node.get("details", {})
            reason = details.get("reason")
            error = details.get("error")
            evidence = details.get("evidence")

            if error:
                result += f"{prefix}     '-- Reason: {error}\n"
                result += f"{prefix}          '-- Details_Output: {evidence}\n"  # Always show in evidence
            elif reason:
                result += f"{prefix}     '-- Reason: {reason}\n"
                result += f"{prefix}          '-- Details_Output: {evidence}\n"  # Always show in evidence
            else:
                result += f"{prefix}       '-- Details: {details}\n"
        
        return result


class TaskFormatter:
    def __init__(self, log_level: str = 'INFO', show_all: bool = False):
        self.log_level = log_level
        self.show_all = show_all
        self.tree_formatter = TreeFormatter(log_level, show_all)
    
    def get_task_status(self, task) -> str:
        if isinstance(task.final_result, dict):
            return task.final_result.get("overall_status", "ERROR")
        return task.final_result
    
    def format_task_for_console(self, task):
        status = self.get_task_status(task)
        status_color = Colors.OKGREEN if status == "PASS" else (Colors.FAIL if status == "FAIL" else Colors.WARNING)
        print(f"[{status_color}{status}{Colors.ENDC}] - ID: {task.id} - {task.title}")
        
        if isinstance(task.final_result, dict) and task.final_result.get("type") in ["logic_node", "action_node"]:
            self.tree_formatter.format_for_console(task.final_result)
        elif isinstance(task.final_result, dict):
            print(f"  '-- Details: {task.final_result.get('details', 'No details available.')}")
        else:
            print(f"  '-- Details: {task.actual_output}")
    
    def format_task_for_file(self, task, file_handle):
        status = self.get_task_status(task)
        
        # Write task metadata
        file_handle.write(f"[{status}] - ID: {task.id}\n")
        file_handle.write(f"Title: {task.title}\n")
        file_handle.write(f"Level: {task.level} | Profile: {task.profile} | Domain: {task.domain}\n")
        file_handle.write(f"Check Type: {task.check_type}\n")
        
        if task.target:
            file_handle.write(f"Target: {task.target}\n")
        if task.expected_value:
            file_handle.write(f"Expected: {task.expected_value}\n")
        
        # Write evidence
        file_handle.write("\nEVIDENCE:\n")
        if isinstance(task.final_result, dict) and task.final_result.get("type") in ["logic_node", "action_node"]:
            tree_output = self.tree_formatter.format_for_file(task.final_result)
            file_handle.write(tree_output)
        elif isinstance(task.final_result, dict):
            file_handle.write(f"  Details: {task.final_result.get('details', 'No details available.')}\n")
            if task.actual_output:
                file_handle.write(f"  Raw Output: {task.actual_output}\n")
        else:
            file_handle.write(f"  Result: {task.final_result}\n")
            if task.actual_output:
                file_handle.write(f"  Raw Output: {task.actual_output}\n")
        
        file_handle.write("\n" + "-" * 80 + "\n\n")
