# Bitbucket to GitHub Repository Migration Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python script that automates migrating repositories from Bitbucket to GitHub while preserving all branches, tags, and commit history.

## Features

- Automates the entire migration process from Bitbucket to GitHub
- Maintains complete git history, branches, and tags
- Handles authentication securely through environment variables
- Supports pagination for accounts with many repositories
- Creates private repositories on GitHub by default
- Provides status updates throughout the migration process

## Prerequisites

- Python 3.6+
- Git command-line tools installed and in your PATH
- Active Bitbucket and GitHub accounts
- Personal access tokens for both platforms:
  - [Creating a Bitbucket app password](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/)
  - [Creating a GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## Installation

1. Clone this repository: 

git clone https://github.com/your-username/migrate_repos_bitbucket_to_github.git 

cd migrate_repos_bitbucket_to_github


2. Install required dependencies:

pip install -r requirements.txt


3. Create a `.env` file in the project root directory with your credentials:

BITBUCKET_USER=your_bitbucket_username BITBUCKET_TOKEN=your_bitbucket_app_password GITHUB_USER=your_github_username GITHUB_TOKEN=your_github_personal_access_token


## Usage

Run the script to start the migration process:


The script will:
1. Fetch all repositories from your Bitbucket account
2. Create corresponding repositories on GitHub
3. Mirror each repository to GitHub (preserving history)
4. Provide status updates in the console

## Usage Examples

### Basic Usage

Migrate all repositories from Bitbucket to GitHub as private repositories:
python migrate_repos.py


### Migrate Specific Repositories

Migrate only certain repositories by name:
python migrate_repos.py --repos repo1 repo2 repo3


### Create Public Repositories

By default, repositories are created as private on GitHub. To create public repositories instead:
python migrate_repos.py --public


### Keep Temporary Files

Keep the temporary cloned repositories for debugging or verification:
python migrate_repos.py --keep-temp


### Skip Existing Repositories

Skip repositories that already exist on GitHub (useful for resuming a previous migration):
python migrate_repos.py --skip-existing


### Combining Options

You can combine multiple options:

Migrate specific repositories as public, skipping any that already exist
python migrate_repos.py --repos repo1 repo2 --public --skip-existing

Migrate all repositories and keep temporary files
python migrate_repos.py --keep-temp



### Troubleshooting File Lock Issues

If you encounter file access issues on Windows, try running with the `--keep-temp` flag:
python migrate_repos.py --keep-temp

Then manually delete the `bitbucket_cloned_repos` directory after migration.


## How It Works

1. **Authentication**: Uses API tokens to authenticate with both Bitbucket and GitHub
2. **Repository Discovery**: Fetches a list of all repositories from your Bitbucket account
3. **Repository Creation**: Creates equivalent repositories on GitHub
4. **Migration**: For each repository:
   - Clones from Bitbucket with `--mirror` flag to preserve all data
   - Adds GitHub as a remote
   - Pushes everything to GitHub
   - Cleans up temporary files

## Customization

- By default, GitHub repositories are created as private. To change this, modify the `private` parameter in the `create_github_repo` function.
- The temporary directory for clones can be changed by updating the `TEMP_DIR` variable.

## Security Notes

- Never commit your `.env` file containing tokens
- The included `.gitignore` file is configured to prevent accidental exposure of credentials

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.