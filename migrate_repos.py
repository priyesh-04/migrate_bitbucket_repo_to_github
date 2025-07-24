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