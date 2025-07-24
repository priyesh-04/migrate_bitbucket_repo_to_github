import os
import subprocess
import requests
import argparse
import shutil
import time  # Add this import for sleep functionality
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bitbucket and GitHub credentials from environment variables
BITBUCKET_USER = os.environ.get('BITBUCKET_USER')
GITHUB_USER = os.environ.get('GITHUB_USER')
BITBUCKET_TOKEN = os.environ.get('BITBUCKET_TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Directory to store the cloned repositories temporarily
TEMP_DIR = 'bitbucket_cloned_repos'  # Change to a suitable directory for your system

# Create the temporary directory if it doesn't exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def run_command(command, cwd=None):
    """Run a system command and print its output."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running command {' '.join(command)}:\n{result.stderr}")
        return False
    else:
        print(result.stdout)
        return True