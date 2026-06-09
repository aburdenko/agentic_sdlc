#!/usr/bin/env python3
import os
import sys
import json
from google import genai
from google.genai import types

def main():
    # Read diff file
    diff_file = "pr_diff.txt"
    if not os.path.exists(diff_file):
        print(f"Error: Diff file '{diff_file}' not found.")
        sys.exit(1)
        
    with open(diff_file, "r") as f:
        diff_content = f.read()

    if not diff_content.strip():
        print("Warning: Diff content is empty. Nothing to review.")
        with open("agent_report.json", "w") as f:
            f.write("[]")
        sys.exit(0)

    # Load system instructions from agents/code-reviewer.md
    reviewer_file = "agents/code-reviewer.md"
    if os.path.exists(reviewer_file):
        with open(reviewer_file, "r") as f:
            system_instruction = f.read()
        print(f"Loaded system instructions from {reviewer_file}")
    else:
        system_instruction = "You are an experienced Staff Engineer conducting a thorough code review."
        print("Using default system instructions")

    # We want a structured JSON response
    prompt_text = f"""
Please review the following git diff and identify issues across correctness, readability, architecture, security, and performance.

For each issue found, you MUST specify:
- path: The file path relative to repository root (e.g. "test_code.py")
- line: The exact line number in the new/changed code where the issue resides.
- message: A clear, actionable description of the issue and the recommended fix.

You MUST respond with a JSON array where each item has the fields "path", "line", and "message".
Example:
[
  {{"path": "test_code.py", "line": 15, "message": "Using unsafe eval() can lead to arbitrary code execution. Use safer alternatives."}}
]

Important: Only comment on files and lines that are actually changed in the diff! Do not comment on unchanged lines.

Diff Content:
{diff_content}
"""

    print("=== Sending request to Gemini (gemini-2.5-flash) ===")
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema={
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "path": {"type": "STRING"},
                            "line": {"type": "INTEGER"},
                            "message": {"type": "STRING"}
                        },
                        "required": ["path", "line", "message"]
                    }
                }
            )
        )
        
        report_content = response.text
        print("=== Received Response ===")
        print(report_content)
        
        with open("agent_report.json", "w") as f:
            f.write(report_content)
            
        print("Successfully wrote agent_report.json")
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
