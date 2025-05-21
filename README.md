# GitHub Repository Auto-Update Tool

This script automatically monitors a GitHub repository for changes and updates a local copy whenever new commits are detected. It can also restart a Django server running in a tmux session after updates.

## Features

- Monitors a GitHub repository for new commits
- Automatically pulls changes when detected
- Handles local changes by stashing them before updating
- Restarts a Django server in a tmux session after updates
- Provides detailed logging of all operations

## Prerequisites

- Python 3.6+
- Git installed and configured
- tmux (for Django server management)
- GitHub Personal Access Token with repository access

## Installation

1. Clone this repository or download the script
2. Install required Python packages:

```bash
pip install requests python-dotenv
```

3. Create a `.env` file in the same directory as the script with your GitHub token:

```
GITHUB_TOKEN=your_github_personal_access_token
```

## Configuration

Edit the following variables in the script to match your setup:

```python
REPO = "Negarkhodro/ngr_diag"  # Your GitHub repository (username/repo)
BRANCH = "main"                # Branch to monitor
LOCAL_REPO_PATH = "/path/to/local/repository"  # Where to store the local copy
```

For Django server management, modify the `restart_django_server()` function if needed:

```python
# The tmux session number
"5"  # Change to your preferred session name/number

# Django server command
"python manage.py runserver 0.0.0.0:8002"  # Adjust port or command as needed
```

## Usage

Run the script manually:

```bash
python github_repo_updater.py
```

For automatic checking, set up a cron job to run the script at desired intervals:

```bash
# Example: Check every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/auto_pull.py >> /path/to/updater.log 2>&1

$ chmod +x /root/negar_actions/run_auto_pull.sh

# Step 3: Edit crontab to run the script every 30 seconds
$ (crontab -l 2>/dev/null; echo "* * * * * /root/negar_actions/run_auto_pull.sh") | crontab -
$ (crontab -l 2>/dev/null; echo "* * * * * sleep 30 && /root/negar_actions/run_auto_pull.sh") | crontab -

# To verify your crontab entry:
$ crontab -l
```

## How It Works

1. The script checks if the local repository exists and is a valid Git repository
2. If not, it clones the repository using the provided GitHub token
3. It compares the latest commit hash from the remote repository with the local commit
4. If they differ, it pulls the latest changes (stashing any local changes first)
5. After updating, it restarts the Django server in tmux session '5'

## Error Handling

The script includes comprehensive error handling:
- Validates the GitHub token is present
- Handles repository cloning issues
- Manages Git operation failures
- Reports detailed error messages

## Security Notes

- The script automatically removes the GitHub token from the Git remote URL after cloning
- Store your `.env` file securely and don't commit it to version control
- Use a GitHub token with minimal required permissions
