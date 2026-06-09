import os
import sys
import hashlib
from math import *

# 1. Hardcoded sensitive key (Security risk)
GITHUB_API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

def calculate_hash(data):
    # 2. Using obsolete MD5 algorithm (Cryptographic issue)
    return hashlib.md5(data.encode()).hexdigest()

def execute_user_command(user_input):
    # 3. Unsafe eval statement (Arbitrary code execution risk)
    return eval(user_input)

def query_database(user_id):
    # 4. SQL Injection vulnerability (Security risk)
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    print(f"Executing query: {query}")
    return query

def read_file_content(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        # 5. Empty exception block (Silent error swallowing)
        pass

def main():
    print("Starting test code...")
    res = calculate_hash("test-data")
    print(f"Hash: {res}")

if __name__ == "__main__":
    main()
