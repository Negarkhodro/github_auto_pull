import subprocess
import requests
import os
from dotenv import load_dotenv
import sys

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("[!] Error: GITHUB_TOKEN environment variable not set")
    sys.exit(1)

REPO = "Negarkhodro/ngr_diag"
BRANCH = "main"
LOCAL_REPO_PATH = "/home/raminfp/PycharmProjects/repo_action/test"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def get_remote_commit():
    url = f"https://api.github.com/repos/{REPO}/commits/{BRANCH}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["sha"]
    else:
        raise Exception(f"Failed to fetch remote commit: {response.status_code} {response.text}")


def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))


def clone_repo():
    if os.path.exists(LOCAL_REPO_PATH):
        if os.listdir(LOCAL_REPO_PATH):  # Not empty
            raise Exception(f"Cannot clone: {LOCAL_REPO_PATH} exists and is not empty.")
        else:
            print("[*] Directory exists but is empty. Proceeding with clone...")
    else:
        os.makedirs(LOCAL_REPO_PATH, exist_ok=True)

    print("[*] Cloning the repository...")
    clone_url = f"https://{GITHUB_TOKEN}@github.com/{REPO}.git"
    result = subprocess.run(["git", "clone", "-b", BRANCH, clone_url, LOCAL_REPO_PATH],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git clone failed: {result.stderr}")

    # Remove token from remote URL
    subprocess.run(["git", "remote", "set-url", "origin", f"https://github.com/{REPO}.git"],
                   cwd=LOCAL_REPO_PATH)
    print("[+] Repository cloned successfully.")


def get_local_commit():
    result = subprocess.run(["git", "rev-parse", "HEAD"],
                            cwd=LOCAL_REPO_PATH,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git error: {result.stderr}")
    return result.stdout.strip()


def check_local_changes():
    result = subprocess.run(["git", "status", "--porcelain"],
                            cwd=LOCAL_REPO_PATH,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git status error: {result.stderr}")
    return bool(result.stdout.strip())


def pull_repo():
    if check_local_changes():
        print("[*] Stashing local changes...")
        subprocess.run(["git", "stash"], cwd=LOCAL_REPO_PATH)
        print("[*] Local changes stashed.")

    # Ensure we're on the correct branch
    checkout_result = subprocess.run(["git", "checkout", BRANCH],
                                     cwd=LOCAL_REPO_PATH,
                                     capture_output=True, text=True)
    if checkout_result.returncode != 0:
        raise Exception(f"Failed to checkout branch {BRANCH}: {checkout_result.stderr}")

    # Pull the latest changes
    pull_result = subprocess.run(["git", "pull", "origin", BRANCH],
                                 cwd=LOCAL_REPO_PATH,
                                 capture_output=True, text=True)
    if pull_result.returncode != 0:
        raise Exception(f"Git pull failed: {pull_result.stderr}")
    print("[+] Repo updated successfully.")
    print(pull_result.stdout)


def restart_django_server():
    """Kill tmux session 0 if it exists and restart the Django server."""
    try:
        # Check if tmux session '5' exists
        check_cmd = ["tmux", "has-session", "-t", "5"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Session exists; kill it
            print("[*] Killing existing tmux session '5'...")
            kill_cmd = ["tmux", "kill-session", "-t", "5"]
            subprocess.run(kill_cmd, check=True)
            print("[+] Killed existing tmux session '5'.")

        # Start a new tmux session running the Django server
        print("[*] Starting Django server in a new tmux session...")

        # Create the tmux session with a bash shell first
        create_session_cmd = ["tmux", "new-session", "-d", "-s", "5"]
        subprocess.run(create_session_cmd, check=True)

        # Send commands to the session
        activate_venv_cmd = ["tmux", "send-keys", "-t", "5", "cd " + LOCAL_REPO_PATH, "C-m"]
        subprocess.run(activate_venv_cmd, check=True)

        venv_cmd = ["tmux", "send-keys", "-t", "5", "source venv/bin/activate", "C-m"]
        subprocess.run(venv_cmd, check=True)

        run_cmd = ["tmux", "send-keys", "-t", "5", "python manage.py runserver 0.0.0.0:8002", "C-m"]
        subprocess.run(run_cmd, check=True)

        print("[+] Django server started successfully in tmux session '5'.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error restarting Django server: {e}")
        raise


def main():
    print(">>> Checking for new commits...")

    try:
        if not is_git_repo(LOCAL_REPO_PATH):
            print("[!] Directory is not a Git repository. Cloning...")
            clone_repo()

        remote_commit = get_remote_commit()
        local_commit = get_local_commit()
        print(f"Remote commit: {remote_commit}")
        print(f"Local commit:  {local_commit}")

        if remote_commit != local_commit:
            print("[*] Commits differ. Pulling changes...")
            pull_repo()
            print("[*] Restarting Django server...")
            restart_django_server()
        else:
            print("[=] Already up to date.")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()