import subprocess
import psutil
import os
import platform
import socket
from typing import Dict, Any, List

class SystemController:
    """Handles system control operations like apps, volume, network, power management"""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else "N/A"
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "battery_percent": battery_percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_connected": self.check_network_connection(),
                "running_processes": len(psutil.pids()),
                "uptime": self._get_uptime()
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {str(e)}"}
    
    def control_volume(self, action: str, level: int = None) -> str:
        """Control system volume"""
        try:
            if self.system == "linux":
                if action == "up":
                    subprocess.run(["amixer", "set", "Master", "5%+"], check=True)
                    return "Volume increased"
                elif action == "down":
                    subprocess.run(["amixer", "set", "Master", "5%-"], check=True)
                    return "Volume decreased"
                elif action == "mute":
                    subprocess.run(["amixer", "set", "Master", "toggle"], check=True)
                    return "Volume toggled"
                elif action == "set" and level is not None:
                    subprocess.run(["amixer", "set", "Master", f"{level}%"], check=True)
                    return f"Volume set to {level}%"
            elif self.system == "windows":
                # Windows volume control would require additional libraries
                return "Volume control not implemented for Windows"
            elif self.system == "darwin":  # macOS
                if action == "up":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"], check=True)
                    return "Volume increased"
                elif action == "down":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"], check=True)
                    return "Volume decreased"
            
            return f"Volume action '{action}' not supported"
        except Exception as e:
            return f"Failed to control volume: {str(e)}"
    
    def launch_application(self, app_name: str) -> str:
        """Launch an application"""
        try:
            if self.system == "linux":
                # Common applications mapping
                app_commands = {
                    "firefox": "firefox",
                    "chrome": "google-chrome",
                    "terminal": "gnome-terminal",
                    "calculator": "gnome-calculator",
                    "file_manager": "nautilus",
                    "text_editor": "gedit",
                    "code": "code",
                    "vscode": "code"
                }
                
                command = app_commands.get(app_name.lower(), app_name)
                subprocess.Popen([command])
                return f"Launched {app_name}"
                
            elif self.system == "windows":
                app_commands = {
                    "notepad": "notepad",
                    "calculator": "calc",
                    "file_manager": "explorer",
                    "chrome": "chrome",
                    "firefox": "firefox"
                }
                command = app_commands.get(app_name.lower(), app_name)
                subprocess.Popen([command])
                return f"Launched {app_name}"
                
            elif self.system == "darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
                return f"Launched {app_name}"
                
        except Exception as e:
            return f"Failed to launch {app_name}: {str(e)}"
    
    def get_running_apps(self) -> List[Dict[str, Any]]:
        """Get list of running applications"""
        try:
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    apps.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return sorted(apps, key=lambda x: x['cpu_percent'], reverse=True)[:20]  # Top 20 by CPU
        except Exception as e:
            return [{"error": f"Failed to get running apps: {str(e)}"}]
    
    def close_application(self, app_name: str) -> str:
        """Close an application by name"""
        try:
            killed = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed:
                return f"Closed {app_name}"
            else:
                return f"Application {app_name} not found"
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"
    
    def check_network_connection(self) -> bool:
        """Check if network connection is available"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            info = {
                "connected": self.check_network_connection(),
                "interfaces": []
            }
            
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {"name": interface, "addresses": []}
                for addr in addrs:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
                info["interfaces"].append(interface_info)
            
            return info
        except Exception as e:
            return {"error": f"Failed to get network info: {str(e)}"}
    
    def power_management(self, action: str) -> str:
        """Handle power management operations"""
        try:
            if action == "shutdown":
                if self.system == "linux" or self.system == "darwin":
                    subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
                elif self.system == "windows":
                    subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
                return "System shutdown initiated"
                
            elif action == "restart":
                if self.system == "linux" or self.system == "darwin":
                    subprocess.run(["sudo", "reboot"], check=True)
                elif self.system == "windows":
                    subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
                return "System restart initiated"
                
            elif action == "sleep":
                if self.system == "linux":
                    subprocess.run(["systemctl", "suspend"], check=True)
                elif self.system == "windows":
                    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
                elif self.system == "darwin":
                    subprocess.run(["pmset", "sleepnow"], check=True)
                return "System sleep initiated"
                
            return f"Power action '{action}' not supported"
        except Exception as e:
            return f"Failed to execute power action: {str(e)}"
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            uptime_seconds = psutil.boot_time()
            import time
            uptime = time.time() - uptime_seconds
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            return f"{hours}h {minutes}m"
        except Exception:
            return "Unknown"