#!/usr/bin/env python3
import os
import sys
from google import genai
from google.genai import types

def main():
    target_file = "test_code.py"
    if not os.path.exists(target_file):
        print(f"Error: Target file '{target_file}' not found.")
        sys.exit(1)
        
    with open(target_file, "r") as f:
        code_content = f.read()

    # Load system instructions from agents/test-engineer.md
    persona_file = "agents/test-engineer.md"
    if os.path.exists(persona_file):
        with open(persona_file, "r") as f:
            system_instruction = f.read()
        print(f"Loaded test-engineer system instructions from {persona_file}")
    else:
        system_instruction = "You are an experienced QA Engineer specialized in writing unit and integration tests."
        print("Using default QA instructions")

    prompt_text = f"""
Analyze the following Python source code and write a comprehensive unit test suite using Python's standard `unittest` framework.

The unit tests should cover:
1. Happy path scenarios for all functions
2. Edge cases and error handling (such as invalid inputs, non-existent files)
3. Any assertions to verify the expected behavior

Source Code to Test:
```python
{code_content}
```

Please output ONLY the executable Python unit test code inside a markdown code block starting with ```python.
"""

    print("=== Sending request to Test Engineer Agent (gemini-2.5-flash) ===")
    try:
        # Configure client with Vertex AI using standard project/location
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or "kallogjeri-project-345114"
        location = os.environ.get("GOOGLE_CLOUD_LOCATION") or "us-central1"
        client = genai.Client(vertexai=True, project=project_id, location=location)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2
            )
        )
        
        response_text = response.text
        print("=== Received Response from Test Engineer ===")
        
        # Extract python code block
        test_code = ""
        if "```python" in response_text:
            parts = response_text.split("```python")
            if len(parts) > 1:
                test_code = parts[1].split("```")[0].strip()
        elif "```" in response_text:
            parts = response_text.split("```")
            if len(parts) > 1:
                test_code = parts[1].strip()
        else:
            test_code = response_text.strip()

        if not test_code:
            print("Error: Could not extract Python code from response.")
            print(response_text)
            sys.exit(1)

        output_file = "test_test_code.py"
        with open(output_file, "w") as f:
            f.write(test_code + "\n")
            
        print(f"Successfully generated unit test suite: {output_file}")
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
