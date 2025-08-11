import re
import logging
from audit_task import AuditTask
from functools import singledispatch
from typing import Tuple
from utils.color_utils import Colors

def data_format(task: AuditTask):
    if not isinstance(task.actual_output, dict):
        return "", -1, 0, [], "AND"
    
    output_dict = task.actual_output
    stdout = output_dict.get("stdout", "")
    exit_code = output_dict.get("exit_code", -1)

    # this part haven't been tested yet
    success_code_param = task.parameters.get("success_code", 0) if isinstance(task.parameters, dict) else 0
    if isinstance(success_code_param, list):
        success_code_param = success_code_param[0] if success_code_param and success_code_param[0] != '' else 0
    try:
        expected_exit_code = int(success_code_param)
    except (ValueError, TypeError):
        expected_exit_code = 0

    
    expected_value = task.expected_value or ""
    
    if ";;" in expected_value:
        # AND logic 
        # expected_conditions = [cond.strip() for cond in expected_value.split(';;') if cond.strip()]
        expected_conditions = [cond.strip() for cond in expected_value.split(';;')]
        logic_type = "AND"
    elif "||" in expected_value:
        # OR logic 
        # expected_conditions = [cond.strip() for cond in expected_value.split('||') if cond.strip()]
        expected_conditions = [cond.strip() for cond in expected_value.split('||')]
        logic_type = "OR"
    else:
        expected_conditions = [expected_value.strip()] if expected_value.strip() else []
        logic_type = "SINGLE"
    # print(expected_conditions) 
    return stdout, exit_code, expected_exit_code, expected_conditions, logic_type

# def algorithm_exact(task: AuditTask) -> bool:
#     stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
#     return exit_code == expected_exit_code and any(condition.lower().strip() == stdout.lower().strip() for condition in expected_conditions)

def algorithm_exact(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, expected_conditions, logic_type = data_format(task)

    # it linked with success_code, but haven't been tested yet 
    # if exit_code != expected_exit_code:
    #     return False
    
    if logic_type == "OR":
        return any(condition.lower() == stdout.lower().strip() for condition in expected_conditions)
    else:
        return any(condition.lower() == stdout.lower().strip() for condition in expected_conditions)

def algorithm_null(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, _ , _= data_format(task)
    return not bool(stdout)

def algorithm_not_null(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, _ , _ = data_format(task)
    return bool(stdout)

# def algorithm_contain(task: AuditTask) -> bool:
#     stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
#     # Normalize whitespace for better matching
#     normalized_stdout = ' '.join(stdout.lower().split())
#     # print(f"Normalized stdout: {normalized_stdout}")  # Debugging output
#     # print(f"Expected conditions: {expected_conditions}")  # Debugging output
#     for condition in expected_conditions:
#         normalized_condition = ' '.join(condition.lower().split())
#         if normalized_condition not in normalized_stdout:
#             return False
#     return True  # All conditions must be present

# def algorithm_contain_all_lines(task: AuditTask) -> bool:
#     stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
#     stdout_lines = [line.strip().lower() for line in stdout.split('\n') if line.strip()]
    
#     for condition in expected_conditions:
#         condition_lines = [line.strip().lower() for line in condition.split('\n') if line.strip()]
#         for expected_line in condition_lines:
#             if not any(expected_line in stdout_line for stdout_line in stdout_lines):
#                 return False
#     return True

# def algorithm_does_not_contain(task: AuditTask) -> bool:
#     stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
#     # return all(condition.lower() not in stdout.lower() for condition in expected_conditions)
#     normalized_stdout = ' '.join(stdout.lower().split())
#     # print(f"Normalized stdout: {normalized_stdout}")  # Debugging output
#     # print(f"Expected conditions: {expected_conditions}")  # Debugging output
#     for condition in expected_conditions:
#         normalized_condition = ' '.join(condition.lower().split())
#         if normalized_condition in normalized_stdout:
#             return False
#     return True  # All conditions must be present

def algorithm_contain(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, expected_conditions, logic_type = data_format(task)
    normalized_stdout = ' '.join(stdout.lower().split())
    # check each of the expected conditions 
    if logic_type == "OR":
        for condition in expected_conditions:
            normalized_condition = ' '.join(condition.lower().split())
            if normalized_condition in normalized_stdout:
                return True
        return False
    else:
        for condition in expected_conditions:
            normalized_condition = ' '.join(condition.lower().split())
            if normalized_condition not in normalized_stdout:
                return False
        return True

def algorithm_does_not_contain(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, expected_conditions, logic_type = data_format(task)
    # Normalize whitespace for better matching
    normalized_stdout = ' '.join(stdout.lower().split())
    # check each of the expected conditions 
    if logic_type == "OR":
        for condition in expected_conditions:
            normalized_condition = ' '.join(condition.lower().split())
            if normalized_condition in normalized_stdout:
                return False
        return True
    else:
        for condition in expected_conditions:
            normalized_condition = ' '.join(condition.lower().split())
            if normalized_condition in normalized_stdout:
                return False
        return True 


ALGORITHM_GROUPS = {
    'Exact': algorithm_exact,
    'Contain': algorithm_contain,
    # new algorithms but have not been tested yet
    # 'Contain All Lines': algorithm_contain_all_lines,
    'Does Not Contain': algorithm_does_not_contain,
    'Null': algorithm_null,
    'Not Null': algorithm_not_null,
}


def simple_check(task: AuditTask) -> dict:
    status_str = "FAIL"  # Default status
    reason_str = "Condition not met." # Default reason
    raw_output = task.actual_output
    error_str = raw_output.get('stderr', "Unknown Error output. Cuz output is empty")

    if not isinstance(raw_output, dict) or "exit_code" not in raw_output:
        status_str = "ERROR"
        error_str = raw_output.get('stderr')
        reason_str = "Evidence not Found. Expected dict with 'exit_code'."
    elif raw_output.get("exit_code") == 127:
        status_str = "ERROR"
        reason_str = f"Command not found. Stderr: {raw_output.get('stderr')}"
    else:
        algorithm_func = ALGORITHM_GROUPS.get(task.algorithm)
        if not algorithm_func:
            status_str = "ERROR"
            reason_str = f"Unknown algorithm specified: '{task.algorithm}'"
        else:
            if algorithm_func(task):
                status_str = "PASS"
                # reason_str = "Check passed successfully."
                reason_str = f"Check passed successfully for algorithm '{task.algorithm}' with expected value '{task.expected_value}'."
            else:
                status_str = "FAIL"
                reason_str = f"Check failed for algorithm '{task.algorithm}' with expected value '{task.expected_value}'."
    
    return {
        "type": "action_node",
        "title": task.title,
        "overall_status": status_str,
        "details": {"reason": reason_str,"error":error_str, "evidence": raw_output}
    }

def complex_check(node: dict) -> dict:
    if "logic" in node:
        logic = node.get("logic", "AND").upper()
        is_passed, has_error = (logic == "AND"), False
        child_results = []
        # parsing json parameters
        for sub_node in node.get("steps", []):
            sub_result_obj = complex_check(sub_node)
            child_results.append(sub_result_obj)
            sub_verdict = sub_result_obj.get("overall_status")
            if sub_verdict == "ERROR": has_error = True
            if sub_verdict == "PASS" and str(sub_node.get('pass_stop_check', 'false')).lower() == 'true':
                is_passed = True; break
            if logic == "AND" and sub_verdict != "PASS": is_passed = False
            if logic == "OR" and sub_verdict == "PASS": is_passed = True; break
        final_status = "ERROR" if has_error else ("PASS" if is_passed else "FAIL")
        return {"type": "logic_node", "logic": logic, "overall_status": final_status, "steps_results": child_results}
    else:
        sub_task = AuditTask(
            algorithm=node.get('algorithm'), expected_value=node.get('expected_value'),
            actual_output=node.get('raw_evidence'), parameters=node.get('params'),
            title=node.get('title', 'Untitled Step'),
            id='', level='', profile=[], domain='', check_type='', target=''
        )
        return simple_check(sub_task)

def process_with_algorithm(task: AuditTask) -> dict:
    if isinstance(task.actual_output, dict) and "error" in task.actual_output:
        return {"overall_status": "ERROR", "type": "action_node", "title": task.title, "details": task.actual_output}
    if isinstance(task.actual_output, dict) and task.actual_output.get("is_unified_logic_payload"):
        payload = task.actual_output
        evidence_tree = payload.get("evidence_tree", [])
        top_level_logic = payload.get("logic", "AND")
        if not top_level_logic: top_level_logic = "AND"
        if not evidence_tree: return {"overall_status": "ERROR", "type": "action_node", "title": task.title, "details": "Logic tree empty."}
        root_node = {"logic": top_level_logic, "steps": evidence_tree}
        return complex_check(root_node)
    else:
        return simple_check(task)