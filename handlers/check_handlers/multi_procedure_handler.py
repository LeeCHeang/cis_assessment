import importlib
import logging

# from utils.decorators import debug_wrapper

def call_sub_handler(handler_name):
    try:
        if not handler_name: return None
        module_name = f"handlers.check_handlers.{handler_name}_handler"
        module = importlib.import_module(module_name)
        return getattr(module, 'handle')
    except (ImportError, AttributeError) as e:
        logging.error(f"Could not load sub-handler for '{handler_name}': {e}")
        return None

def collect_evidence(steps_array):
    evidence_tree = []
    for node in steps_array:
        if "logic" in node:
            processed_steps, error = collect_evidence(node.get("steps", []))
            if error:
                return None, error
            evidence_tree.append({"logic": node["logic"], "steps": processed_steps})
        else:
            action_node = node.copy()
            sub_handler_name = action_node.get('type_handler')
            
            if not sub_handler_name:
                step_title = action_node.get('title', 'Untitled Step')
                error_message = f"Configuration Error: Missing 'type_handler' key in step titled: '{step_title}'"
                return None, {"error": error_message}

            sub_handle_func = call_sub_handler(sub_handler_name)
            if not sub_handle_func:
                step_title = action_node.get('title', 'Untitled Step')
                error_message = f"Configuration Error: The specified 'type_handler' ('{sub_handler_name}') does not exist for step: '{step_title}'"
                return None, {"error": error_message}

            try:
                raw_evidence = sub_handle_func(action_node.get('target'), action_node.get('parameters'))
            except Exception as e:
                raw_evidence = {"stderr": f"Exception during execution of '{sub_handler_name}': {e}", "exit_code": -1}
            
            action_node['raw_evidence'] = raw_evidence
            evidence_tree.append(action_node)

    return evidence_tree, None
# @debug_wrapper
def handle(target: str, params: dict) -> dict:
    if not isinstance(params, dict) or "steps" not in params:
        return {"error": "Parameters for multi_procedure must contain a 'steps' array."}
    
    evidence_tree, error = collect_evidence(params.get("steps", []))
    if error:
        return error

    return {
        "is_unified_logic_payload": True,
        "logic": params.get("logic"),
        "evidence_tree": evidence_tree
    }