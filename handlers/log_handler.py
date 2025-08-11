import logging
import datetime
import os
import re
from utils.color_utils import draw_color_manager

class ColorFormatter(logging.Formatter):
    
    def __init__(self):
        super().__init__()
        self.color_manager = draw_color_manager()

        self.FORMATS = {
            logging.DEBUG: f"{self.color_manager.GREEN}%(asctime)s {self.color_manager.BOLD_RED}|{self.color_manager.RESET} {self.color_manager.YELLOW}%(levelname)s{self.color_manager.RESET} {self.color_manager.BOLD_RED}|{self.color_manager.RESET} %(message)s",
            logging.INFO: f"{self.color_manager.GREEN}%(asctime)s {self.color_manager.BOLD_RED}|{self.color_manager.RESET} {self.color_manager.BOLD_LBLUE}%(levelname)s{self.color_manager.RESET} {self.color_manager.BOLD_RED}|{self.color_manager.RESET} %(message)s",
            logging.WARNING: f"{self.color_manager.GREEN}%(asctime)s {self.color_manager.BOLD_RED}|{self.color_manager.RESET} {self.color_manager.ORANGE}%(levelname)s{self.color_manager.RESET} {self.color_manager.BOLD_RED}|{self.color_manager.RESET} %(message)s",
            logging.ERROR: f"{self.color_manager.GREEN}%(asctime)s {self.color_manager.BOLD_RED}|{self.color_manager.RESET}{self.color_manager.RED_BG} %(levelname)s {self.color_manager.RESET}{self.color_manager.BOLD_RED}|{self.color_manager.RESET} %(message)s",
            logging.CRITICAL: f"{self.color_manager.GREEN}%(asctime)s {self.color_manager.BOLD_RED}|{self.color_manager.RESET} {self.color_manager.BOLD_RED}%(levelname)s{self.color_manager.RESET} {self.color_manager.BOLD_RED}|{self.color_manager.RESET} %(message)s",
        }

    def _colorize_message(self, message: str, level: int) -> str:
        if not self.color_manager.use_colors:
            return message
            
        # Colorize "Executing check" messages
        if "Executing check:" in message:
            return re.sub(
                r'(Executing check:)(\s*\[([^\]]+)\]\s*)(.+)',
                rf'{self.color_manager.ORANGE}\1\2{self.color_manager.RESET}\4',
                message
            )
        
        if "Finished check:" in message:
            def colorize_result(match):
                prefix = match.group(1)  # "Finished check: [ID] - Result: "
                status = match.group(2)  # "PASS", "FAIL", or "ERROR"
                suffix = match.group(3)  # "]"
                
                if status == "PASS":
                    status_color = self.color_manager.OKGREEN
                elif status == "FAIL":
                    status_color = self.color_manager.FAIL
                else:  # ERROR
                    status_color = self.color_manager.WARNING
                
                return f"{self.color_manager.BOLD}{prefix}{self.color_manager.RESET}[{status_color}{status}{self.color_manager.RESET}]{suffix}"
            
            message = re.sub(
                r'(Finished check: \[[^\]]+\] - Result: )\[([^\]]+)\](\]?)',
                colorize_result,
                message
            )
        
        if "AUDIT RUN HAS BEEN COMPLETED" in message:
            return f"{self.color_manager.CYAN}{message}{self.color_manager.RESET}"
            
        return message

    def format(self, record):
        # First apply the standard log format
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        formatted = formatter.format(record)
        
        # Extract the message part (after the last | character)
        if "|" in formatted:
            parts = formatted.rsplit("|", 1)
            if len(parts) == 2:
                prefix, message = parts
                colorized_message = self._colorize_message(message.strip(), record.levelno)
                formatted = f"{prefix}| {colorized_message}"
        
        return formatted

def setup_logger(log_level_str: str = 'INFO'):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"audit_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())

    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger