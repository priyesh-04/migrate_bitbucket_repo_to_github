
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

def fetch_bitbucket_repositories():
    """Fetch all repositories from Bitbucket using pagination."""
    url = f'https://api.bitbucket.org/2.0/repositories/{BITBUCKET_USER}'
    repos = []
    while url:
        response = requests.get(url, auth=(BITBUCKET_USER, BITBUCKET_TOKEN))
        if response.status_code == 200:
            data = response.json()
            repos.extend([repo['name'] for repo in data['values']])
            # Get the next page URL if exists
            url = data.get('next', None)
        else:
            print(f"Error fetching Bitbucket repositories: {response.json()}")
            break
    return repos

def create_github_repo(repo_name, private=True):
    """Create a new repository on GitHub using the GitHub API."""
    url = f'https://api.github.com/user/repos'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': repo_name,
        'private': private,
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print(f"Successfully created GitHub repository: {repo_name}")
    else:
        print(f"Error creating GitHub repository {repo_name}: {response.json()}")

def migrate_repository(repo_name, private=True, keep_temp=False):
    """Clone the repository from Bitbucket and push it to GitHub."""
    try:
        # Step 1: Create the repository on GitHub
        create_github_repo(repo_name, private=private)

        repo_dir = os.path.join(TEMP_DIR, repo_name)

        # Step 2: Clone the repository from Bitbucket (with authentication)
        bitbucket_url = f'https://{BITBUCKET_USER}:{BITBUCKET_TOKEN}@bitbucket.org/{BITBUCKET_USER}/{repo_name}.git'
        run_command(['git', 'clone', '--mirror', bitbucket_url, repo_dir])

        # Step 3: Add GitHub remote (with authentication)
        github_url = f'https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{repo_name}.git'
        run_command(['git', 'remote', 'add', 'github', github_url], cwd=repo_dir)

        # Step 4: Push all branches and tags to GitHub
        run_command(['git', 'push', '--mirror', 'github'], cwd=repo_dir)

        # Optional: Clean up the local copy after migration
        if not keep_temp and os.path.exists(repo_dir):
            # Close any open git processes to prevent file locks
            run_command(['git', 'gc'], cwd=repo_dir)
            
            # Add a small delay to ensure files are released
            time.sleep(1)
            
            try:
                shutil.rmtree(repo_dir)
                print(f"Removed temporary clone: {repo_dir}")
            except PermissionError:
                print(f"Warning: Could not remove {repo_dir} due to file locks. You may need to delete it manually.")

        return True
    except Exception as e:
        print(f"Error migrating repository {repo_name}: {str(e)}")
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Migrate repositories from Bitbucket to GitHub')
    parser.add_argument('--public', action='store_true', help='Create public repositories instead of private')
    parser.add_argument('--repos', nargs='*', help='Specific repositories to migrate (migrates all if not specified)')
    parser.add_argument('--keep-temp', action='store_true', help='Keep temporary cloned repositories')
    parser.add_argument('--skip-existing', action='store_true', help='Skip repositories that already exist on GitHub')
    return parser.parse_args()

def check_github_repo_exists(repo_name):
    """Check if a repository already exists on GitHub."""
    url = f'https://api.github.com/repos/{GITHUB_USER}/{repo_name}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def validate_tokens():
    """Check if the provided tokens are valid."""
    # Check Bitbucket token
    bb_url = f'https://api.bitbucket.org/2.0/user'
    bb_response = requests.get(bb_url, auth=(BITBUCKET_USER, BITBUCKET_TOKEN))
    
    # Check GitHub token
    gh_url = 'https://api.github.com/user'
    gh_headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    gh_response = requests.get(gh_url, headers=gh_headers)
    
    if bb_response.status_code != 200:
        print("Error: Invalid Bitbucket credentials")
        return False
        
    if gh_response.status_code != 200:
        print("Error: Invalid GitHub token")
        return False
        
    return True

def main():
    """Main function to handle multiple repository migrations."""
    # Check if environment variables are set
    if not all([BITBUCKET_USER, GITHUB_USER, BITBUCKET_TOKEN, GITHUB_TOKEN]):
        print("Error: Missing required environment variables. Please check your .env file.")
        return
        
    if not validate_tokens():
        return

    args = parse_arguments()
    
    print("Fetching Bitbucket repositories...")
    all_repos = fetch_bitbucket_repositories()
    
    if not all_repos:
        print("No repositories found in your Bitbucket account.")
        return
    
    # Filter repositories if specific ones were requested
    if args.repos:
        repos_to_migrate = [repo for repo in all_repos if repo in args.repos]
        if not repos_to_migrate:
            print("None of the specified repositories were found in your Bitbucket account.")
            return
    else:
        repos_to_migrate = all_repos
    
    print(f"Found {len(repos_to_migrate)} repositories to migrate.")
    
    successful = []
    failed = []
    
    for repo in repos_to_migrate:
        if args.skip_existing and check_github_repo_exists(repo):
            print(f"Skipping existing repository: {repo}")
            continue

        print(f"Migrating repository: {repo}")
        success = migrate_repository(repo, private=not args.public, keep_temp=args.keep_temp)
        if success:
            successful.append(repo)
            print(f"Successfully migrated: {repo}\n")
        else:
            failed.append(repo)
            print(f"Failed to migrate: {repo}\n")
    
    # Print summary
    print("\n=== Migration Summary ===")
    print(f"Total repositories processed: {len(repos_to_migrate)}")
    print(f"Successfully migrated: {len(successful)}")
    print(f"Failed to migrate: {len(failed)}")
    
    if failed:
        print("\nFailed repositories:")
        for repo in failed:
            print(f" - {repo}")

if __name__ == '__main__':
    main()
