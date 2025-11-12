#!/usr/bin/env python
"""
Helper script to create and run virtual environment and execute tests
This script handles cross-platform compatibility for Windows
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def run_command(cmd, cwd=None, shell=False):
    """Run a command and return exit code."""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=shell, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return 1

def create_venv(project_dir):
    """Create virtual environment."""
    venv_path = os.path.join(project_dir, 'venv')
    
    if os.path.exists(venv_path):
        print(f"Virtual environment already exists: {venv_path}")
    else:
        print(f"Creating virtual environment: {venv_path}")
        if sys.platform == 'win32':
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        else:
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
    
    return venv_path

def activate_and_run(project_dir, command):
    """Activate venv and run command."""
    venv_path = create_venv(project_dir)
    
    if sys.platform == 'win32':
        # Windows
        python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        pip_exe = os.path.join(venv_path, 'Scripts', 'pip.exe')
    else:
        # Linux/Mac
        python_exe = os.path.join(venv_path, 'bin', 'python')
        pip_exe = os.path.join(venv_path, 'bin', 'pip')
    
    # Install requirements
    requirements_path = os.path.join(project_dir, 'requirements.txt')
    if os.path.exists(requirements_path):
        print(f"Installing requirements from {requirements_path}")
        subprocess.run([pip_exe, 'install', '-r', requirements_path], check=True)
    
    # Execute command with python from venv
    full_command = f"{python_exe} {' '.join(command)}"
    return run_command(full_command, cwd=project_dir, shell=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_helper.py <project_dir> [command...]")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    command = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if not os.path.exists(project_dir):
        print(f"Project directory not found: {project_dir}")
        sys.exit(1)
    
    sys.exit(activate_and_run(project_dir, command))
