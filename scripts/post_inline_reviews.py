#!/usr/bin/env python3
import os
import sys
import json
import requests

def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo_owner = os.environ.get("REPO_OWNER")
    repo_name = os.environ.get("REPO_NAME")
    pr_number = os.environ.get("PR_NUMBER")
    commit_sha = os.environ.get("COMMIT_SHA")
    
    if not commit_sha or len(commit_sha) != 40 or not all(c in "0123456789abcdefABCDEF" for c in commit_sha):
        print(f"Warning: COMMIT_SHA environment variable '{commit_sha}' is not a valid 40-character commit SHA. Attempting to get it via git rev-parse HEAD...")
        try:
            import subprocess
            commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
            print(f"Successfully retrieved commit SHA from git: {commit_sha}")
        except Exception as e:
            print(f"Error: Could not retrieve commit SHA from git: {e}")
    
    if not all([token, repo_owner, repo_name, pr_number, commit_sha]):
        print("Error: Missing required environment variables (GITHUB_TOKEN, REPO_OWNER, REPO_NAME, PR_NUMBER, COMMIT_SHA).")
        sys.exit(1)

    agent_output_file = "agent_report.json"
    if not os.path.exists(agent_output_file):
        print(f"Error: Agent output file '{agent_output_file}' not found.")
        sys.exit(1)

    with open(agent_output_file, "r") as f:
        content = f.read().strip()
        # Clean up any potential markdown backticks enclosing the JSON if the model added them
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            comments = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse agent output as JSON: {e}")
            print("Raw output was:")
            print(content)
            sys.exit(1)

    if not isinstance(comments, list):
        print("Error: Expected agent output JSON to be a list of comments.")
        sys.exit(1)

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    success_count = 0
    for comment in comments:
        path = comment.get("path")
        line = comment.get("line")
        body = comment.get("message") or comment.get("body")
        
        if not path or not line or not body:
            print(f"Warning: Skipping invalid comment entry: {comment}")
            continue

        payload = {
            "body": f"🤖 **Antigravity Review:**\n\n{body}",
            "commit_id": commit_sha,
            "path": path,
            "line": int(line),
            "side": "RIGHT"
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            success_count += 1
        else:
            print(f"Error posting inline comment for {path}:{line}. Response: {response.status_code} - {response.text}")

    print(f"Successfully posted {success_count} inline review comment(s).")

if __name__ == "__main__":
    main()
