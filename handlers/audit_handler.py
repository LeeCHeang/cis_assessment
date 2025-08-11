# In cis_auditor_v3/handlers/audit_handler.py
import logging
import importlib
from typing import List
from audit_task import AuditTask
# We must import the Judge function here to be used by the handler
from handlers.output_handler import process_with_algorithm
from utils.color_utils import Colors

class AuditHandler:
    def __init__(self):
        self.logger = logging.getLogger()

    def run_audit(self, tasks: List[AuditTask], log_level: str = 'INFO') -> List[AuditTask]:
        self.logger.info(f"Starting audit with {len(tasks)} tasks.")
        
        for task in tasks:
            task.status = "RUNNING"
            self.logger.info(f"Executing check: [{task.id}] {task.title}")
            
            try:
                if not task.check_type:
                    raise ValueError("Task has no 'check_type' defined. Please check CSV headers and data.")
                
                handler_module_name = f"handlers.check_handlers.{task.check_type}_handler"
                
                handler_module = importlib.import_module(handler_module_name)
                execute_func = getattr(handler_module, 'handle')

                raw_value = execute_func(task.target, task.parameters)
                task.actual_output = raw_value

                task.final_result = process_with_algorithm(task)

            except Exception as e:
                task.final_result = {"overall_status": "ERROR", "type":"action_node", "details": {"error":f"Audit Handler Error: {e}"}}
            
            task.status = "COMPLETED"


            # case_color = Colors.OKGREEN if simple_status == "PASS" else Colors.FAIL if simple_status == "FAIL" else Colors.WARNING

            final_result_obj = task.final_result
            if isinstance(final_result_obj, dict):
                simple_status = final_result_obj.get("overall_status", "ERROR")
            elif isinstance(final_result_obj, str):
                simple_status = final_result_obj
           
            # Use the correct log level based on the final status.
            if simple_status == "ERROR":
                self.logger.error(f"Finished check: [{task.id}] - Result: [ERROR]")
            else:
                self.logger.info(f"Finished check: [{task.id}] - Result: [{simple_status}]")


        self.logger.info("AUDIT RUN HAS BEEN COMPLETED.")
        return tasks