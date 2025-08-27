import os
import sys
import time
import platform
import subprocess
import threading
from typing import Dict, List, Tuple, Optional
import json
import wave
import numpy as np
from datetime import datetime

# Audio libraries
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️  PyAudio not available. Install with: pip install pyaudio")

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("⚠️  SoundDevice not available. Install with: pip install sounddevice")

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.ENDC}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

class AudioDiagnostics:
    def __init__(self):
        self.system_info = self.get_system_info()
        self.audio_devices = []
        self.test_results = {}
        self.recommendations = []
        
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version,
            'processor': platform.processor(),
            'hostname': platform.node(),
            'timestamp': datetime.now().isoformat()
        }
    
    def check_permissions(self) -> Dict:
        """Check microphone permissions across different OS platforms"""
        print_header("Checking Microphone Permissions")
        
        permissions = {
            'windows': self.check_windows_permissions(),
            'macos': self.check_macos_permissions(),
            'linux': self.check_linux_permissions(),
            'general': self.check_general_permissions()
        }
        
        return permissions
    
    def check_windows_permissions(self) -> Dict:
        """Check Windows-specific microphone permissions"""
        results = {'status': 'unknown', 'issues': [], 'solutions': []}
        
        try:
            # Check if we can access the Windows Registry for microphone settings
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone")
                results['status'] = 'accessible'
                print_success("Windows microphone registry accessible")
            except FileNotFoundError:
                results['status'] = 'no_registry_access'
                results['issues'].append("Microphone registry key not found")
                results['solutions'].append("Check Windows Privacy Settings > Microphone")
            except PermissionError:
                results['status'] = 'permission_denied'
                results['issues'].append("Registry access denied")
                results['solutions'].append("Run as administrator")
        except ImportError:
            results['status'] = 'winreg_unavailable'
            results['issues'].append("Windows registry module not available")
        
        # Check Windows Privacy Settings via PowerShell
        try:
            result = subprocess.run([
                'powershell', '-Command', 
                'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Windows" -Name "EnableLinkedConnections"'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print_success("Windows PowerShell access available")
            else:
                print_warning("Windows PowerShell access limited")
                results['solutions'].append("Enable PowerShell execution policy: Set-ExecutionPolicy RemoteSigned")
        except Exception as e:
            print_warning(f"PowerShell check failed: {e}")
        
        return results
    
    def check_macos_permissions(self) -> Dict:
        """Check macOS-specific microphone permissions"""
        results = {'status': 'unknown', 'issues': [], 'solutions': []}
        
        try:
            # Check microphone permission status
            result = subprocess.run([
                'osascript', '-e', 
                'tell application "System Events" to get properties of process "Python"'
            ], capture_output=True, text=True, timeout=5)
            
            if "microphone" in result.stdout.lower():
                print_success("macOS microphone permission detected")
                results['status'] = 'granted'
            else:
                print_warning("macOS microphone permission not detected")
                results['status'] = 'not_granted'
                results['issues'].append("Microphone permission not granted")
                results['solutions'].append("Go to System Preferences > Security & Privacy > Privacy > Microphone")
        except Exception as e:
            print_warning(f"macOS permission check failed: {e}")
            results['status'] = 'check_failed'
        
        return results
    
    def check_linux_permissions(self) -> Dict:
        """Check Linux-specific microphone permissions"""
        results = {'status': 'unknown', 'issues': [], 'solutions': []}
        
        try:
            # Check if user is in audio group
            result = subprocess.run(['groups'], capture_output=True, text=True, timeout=5)
            if 'audio' in result.stdout:
                print_success("User is in audio group")
                results['status'] = 'audio_group_member'
            else:
                print_warning("User not in audio group")
                results['status'] = 'not_in_audio_group'
                results['issues'].append("User not in audio group")
                results['solutions'].append("Add user to audio group: sudo usermod -a -G audio $USER")
            
            # Check PulseAudio status
            result = subprocess.run(['pulseaudio', '--check'], capture_output=True, timeout=5)
            if result.returncode == 0:
                print_success("PulseAudio is running")
            else:
                print_warning("PulseAudio not running")
                results['issues'].append("PulseAudio not running")
                results['solutions'].append("Start PulseAudio: pulseaudio --start")
                
        except Exception as e:
            print_warning(f"Linux permission check failed: {e}")
            results['status'] = 'check_failed'
        
        return results
    
    def check_general_permissions(self) -> Dict:
        """Check general microphone access"""
        results = {'status': 'unknown', 'issues': [], 'solutions': []}
        
        if not PYAUDIO_AVAILABLE:
            results['status'] = 'pyaudio_missing'
            results['issues'].append("PyAudio not installed")
            results['solutions'].append("Install PyAudio: pip install pyaudio")
            return results
        
        try:
            p = pyaudio.PyAudio()
            # Try to open a test stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            print_success("General microphone access successful")
            results['status'] = 'accessible'
        except Exception as e:
            print_error(f"General microphone access failed: {e}")
            results['status'] = 'access_denied'
            results['issues'].append(f"Microphone access error: {str(e)}")
            results['solutions'].append("Check microphone is not in use by other applications")
        
        return results
