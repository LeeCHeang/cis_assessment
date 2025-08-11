import os
import sys
import platform


class ColorManager:
    
    def __init__(self):
        self.use_colors = self.pick_colors()
        self.set_colors()
        
    def pick_colors(self):
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
            
        if os.environ.get('NO_COLOR'):
            return False
            
        if os.environ.get('FORCE_COLOR'):
            return True
            
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                # IRTUAL_TERMINAL_PROCESSING (0x0004)
                new_mode = mode.value | 0x0004
                success = kernel32.SetConsoleMode(handle, new_mode)
                if success:
                    return True
            except:
                pass
                
            try:
                import colorama
                colorama.init(autoreset=True)
                return True
            except ImportError:
                return False
        else:
            return True
    
    def set_colors(self):
        if self.use_colors:
            # ANSI color codes
            self.OKGREEN = '\033[92m'
            self.WARNING = '\033[93m'
            self.FAIL = '\033[91m'
            self.ENDC = '\033[0m'
            self.BOLD = '\033[1m'
            self.GREY = "\x1b[38;20m"
            self.BLUE = "\x1b[34;20m"
            self.YELLOW = "\x1b[33;20m"
            self.RED = "\x1b[31;20m"
            self.BOLD_RED = "\x1b[31;1m"
            self.GREEN = '\033[32m'
            self.ORANGE = '\033[38;2;255;165;0m'
            self.CYAN = "\x1b[36;1m"
            self.RESET = "\x1b[0m"
            self.BOLD_LBLUE = '\033[94m\033[1m'
            self.RED_BG = "\x1b[41;1;37m"
        else:
            self.OKGREEN = self.WARNING = self.FAIL = self.ENDC = self.BOLD = ""
            self.GREY = self.BLUE = self.YELLOW = self.RED = self.BOLD_RED = ""
            self.GREEN = self.ORANGE = self.CYAN = self.RESET = self.BOLD_LBLUE = self.RED_BG = ""


# Global instance
color_manager = ColorManager()


class Colors:
    @property
    def OKGREEN(self):
        return color_manager.OKGREEN
    
    @property
    def WARNING(self):
        return color_manager.WARNING
    
    @property
    def FAIL(self):
        return color_manager.FAIL
    
    @property
    def ENDC(self):
        return color_manager.ENDC
    
    @property
    def BOLD(self):
        return color_manager.BOLD
    
    @property
    def GREY(self):
        return color_manager.GREY
    
    @property
    def BLUE(self):
        return color_manager.BLUE
    
    @property
    def YELLOW(self):
        return color_manager.YELLOW
    
    @property
    def RED(self):
        return color_manager.RED
    
    @property
    def BOLD_RED(self):
        return color_manager.BOLD_RED
    
    @property
    def GREEN(self):
        return color_manager.GREEN
    
    @property
    def ORANGE(self):
        return color_manager.ORANGE
    
    @property
    def CYAN(self):
        return color_manager.CYAN
    
    @property
    def RESET(self):
        return color_manager.RESET
    
    @property
    def BOLD_LBLUE(self):
        return color_manager.BOLD_LBLUE
    
    @property
    def RED_BG(self):
        return color_manager.RED_BG


Colors = Colors()


def draw_color_manager():
    return color_manager


def use_colors():
    return color_manager.use_colors
