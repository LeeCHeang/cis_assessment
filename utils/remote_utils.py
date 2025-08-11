import logging
from typing import Tuple
import paramiko


class RemoteExecutor:
    def __init__(self, hostname: str, port: int = 22, username: str = None, 
                 password: str = None, key_path: str = None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path
        self.client = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Determine authentication method
            auth_kwargs = {}
            if self.key_path:
                self.logger.info(f"Connecting to {self.hostname}:{self.port} using key authentication")
                auth_kwargs['key_filename'] = self.key_path
            elif self.password:
                self.logger.info(f"Connecting to {self.hostname}:{self.port} using password authentication")
                auth_kwargs['password'] = self.password
            else:
                raise ValueError("Either password or key_path must be provided for authentication")
            
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                timeout=30,
                **auth_kwargs
            )
            
            self.logger.info(f"Successfully connected to {self.hostname}")
            return True
            
        except paramiko.AuthenticationException:
            self.logger.error(f"Authentication failed for {self.username}@{self.hostname}")
            return False
        except paramiko.SSHException as e:
            self.logger.error(f"SSH connection error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.hostname}: {e}")
            return False
    
    def disconnect(self):
        if self.client:
            self.client.close()
            self.logger.info(f"Disconnected from {self.hostname}")
    
    def run_command(self, command: str, timeout: int = 30) -> Tuple[str, str]:
        if not self.client:
            if not self.connect():
                raise ConnectionError(f"Could not establish connection to {self.hostname}")
        
        try:
            if command.strip().startswith('sudo '):
                return self.call_sudo_command(command, timeout)
            else:
                stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
                
                stdout_content = stdout.read().decode('utf-8')
                stderr_content = stderr.read().decode('utf-8')
                
                exit_status = stdout.channel.recv_exit_status()
                
                self.logger.debug(f"Command executed with exit status: {exit_status}")
                self.logger.debug(f"STDOUT: {stdout_content}")
                if stderr_content:
                    self.logger.debug(f"STDERR: {stderr_content}")
                
                return stdout_content, stderr_content
            
        except paramiko.SSHException as e:
            self.logger.error(f"SSH execution error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise
    
    def call_sudo_command(self, command: str, timeout: int = 30) -> Tuple[str, str]:
        try:
            sudo_command = command.replace('sudo ', 'sudo -S -p "" ', 1)
            stdin, stdout, stderr = self.client.exec_command(sudo_command, timeout=timeout)
            
            if hasattr(self, 'password') and self.password:
                stdin.write(self.password + '\n')
                stdin.flush()
            
            stdout_content = stdout.read().decode('utf-8')
            stderr_content = stderr.read().decode('utf-8')
            
            exit_status = stdout.channel.recv_exit_status()
            
            self.logger.debug(f"Sudo command executed with exit status: {exit_status}")
            self.logger.debug(f"STDOUT: {stdout_content}")
            if stderr_content:
                self.logger.debug(f"STDERR: {stderr_content}")
            
            return stdout_content, stderr_content
            
        except paramiko.SSHException as e:
            self.logger.error(f"SSH sudo execution error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Sudo command execution failed: {e}")
            raise
    
    def run_script(self, script_content: str, timeout: int = 30) -> Tuple[str, str]:
        wrapped_command = f"sudo bash -c {repr(script_content)}"
        return self.run_command(wrapped_command, timeout)
    
    def file_exists(self, file_path: str) -> bool:
        try:
            stdout, stderr = self.run_command(f"test -f {file_path} && echo 'exists'")
            return 'exists' in stdout.strip()
        except:
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        if not self.client:
            self.logger.error("SSH connection not established")
            return False
            
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            self.logger.debug(f"Successfully uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            return False
    
    def upload_script_content(self, script_content: str, remote_path: str) -> bool:
        if not self.client:
            self.logger.error("SSH connection not established")
            return False
            
        try:
            sftp = self.client.open_sftp()
            with sftp.file(remote_path, 'w') as remote_file:
                remote_file.write(script_content)
            sftp.close()
            # Change permissions to make it executable
            self.run_command(f"sudo chmod +x {remote_path}")
            self.logger.debug(f"Successfully uploaded script content to {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"Script upload failed: {e}")
            return False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
