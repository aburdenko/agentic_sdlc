import unittest
import os
import sys
import hashlib
from unittest.mock import patch, mock_open

# --- Start of the provided source code (for direct inclusion in test file for self-containment) ---
# In a real project, these functions would typically be in a separate module (e.g., 'app.py')
# and imported as 'from app import calculate_hash, ...'
# For this exercise, we include them directly to make the test script self-contained and runnable.

DATABASE_PASSWORD = "my_super_secret_password_123!"

def calculate_hash(data):
    print("hello") # This print statement is an implementation detail.
    return hashlib.md5(data.encode()).hexdigest()

def execute_user_command(user_input):
    return eval(user_input)

def query_database(user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    print(f"Executing query: {query}") # This print statement is an implementation detail.
    return query

def read_file_content(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        # 5. Empty exception block (Silent error swallowing)
        pass
    
def test1():
    return "hello"

def test2():
    return "hello"

# The `main` function is an application entry point and typically orchestrates other functions.
# Unit testing it directly often involves extensive mocking of its dependencies (like print, calculate_hash).
# Per the persona's guidelines, we focus on testing the core logic functions at the lowest level.
# Therefore, `main` is not included in this unit test suite.
# --- End of the provided source code ---


class TestVulnerableApp(unittest.TestCase):

    # --- Tests for calculate_hash ---
    def test_calculate_hash_happy_path_string(self):
        """Verifies calculate_hash returns correct MD5 hash for a standard string."""
        data = "test-data"
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_calculate_hash_empty_string(self):
        """Verifies calculate_hash returns correct MD5 hash for an empty string."""
        data = ""
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_calculate_hash_non_string_input_raises_attribute_error(self):
        """Verifies calculate_hash raises AttributeError for non-string input due to .encode()."""
        with self.assertRaises(AttributeError):
            calculate_hash(123)
        with self.assertRaises(AttributeError):
            calculate_hash(None)
        with self.assertRaises(AttributeError):
            calculate_hash(['list', 'of', 'strings'])

    # --- Tests for execute_user_command ---
    def test_execute_user_command_arithmetic_expression(self):
        """Verifies execute_user_command correctly evaluates simple arithmetic expressions."""
        self.assertEqual(execute_user_command("1 + 1"), 2)
        self.assertEqual(execute_user_command("10 * 2 - 5"), 15)
        self.assertEqual(execute_user_command("2 ** 3"), 8)

    def test_execute_user_command_string_operation(self):
        """Verifies execute_user_command correctly evaluates string methods."""
        self.assertEqual(execute_user_command("'hello'.upper()"), "HELLO")
        self.assertEqual(execute_user_command("' Python '.strip()"), "Python")

    def test_execute_user_command_invalid_syntax_raises_syntax_error(self):
        """Verifies execute_user_command raises SyntaxError for invalid Python syntax."""
        with self.assertRaises(SyntaxError):
            execute_user_command("1 +")
        with self.assertRaises(SyntaxError):
            execute_user_command("def func(): pass") # eval doesn't allow statements

    def test_execute_user_command_undefined_name_raises_name_error(self):
        """Verifies execute_user_command raises NameError for undefined variables."""
        with self.assertRaises(NameError):
            execute_user_command("undefined_variable")

    def test_execute_user_command_arbitrary_code_execution_demonstration(self):
        """
        Demonstrates the arbitrary code execution vulnerability of execute_user_command.
        Mocks os.system to prevent actual system calls during testing.
        """
        with patch('os.system') as mock_os_system:
            execute_user_command("os.system('echo pwned')")
            mock_os_system.assert_called_once_with('echo pwned')
        
        # Another example: accessing built-ins
        self.assertEqual(execute_user_command("len('abc')"), 3)
        self.assertEqual(execute_user_command("max(1, 5, 2)"), 5)

    # --- Tests for query_database ---
    def test_query_database_happy_path_integer_id(self):
        """Verifies query_database generates correct SQL for an integer user ID."""
        user_id = 123
        expected_query = "SELECT * FROM users WHERE id = '123'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_happy_path_string_id(self):
        """Verifies query_database generates correct SQL for a string user ID."""
        user_id = "john_doe"
        expected_query = "SELECT * FROM users WHERE id = 'john_doe'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_sql_injection_vulnerability_demonstration(self):
        """
        Demonstrates the SQL Injection vulnerability in query_database.
        Verifies that malicious input alters the query structure.
        """
        malicious_id = "1' OR '1'='1"
        expected_query = "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        self.assertEqual(query_database(malicious_id), expected_query)

        malicious_id_with_comment = "1'; DROP TABLE users; --"
        expected_query_with_comment = "SELECT * FROM users WHERE id = '1'; DROP TABLE users; --'"
        self.assertEqual(query_database(malicious_id_with_comment), expected_query_with_comment)
        
        # This test confirms the *construction* of the vulnerable query string,
        # not its execution against a database.

    def test_query_database_empty_id(self):
        """Verifies query_database handles an empty user ID correctly."""
        user_id = ""
        expected_query = "SELECT * FROM users WHERE id = ''"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_none_id(self):
        """Verifies query_database handles a None user ID (converts to 'None' string)."""
        user_id = None
        expected_query = "SELECT * FROM users WHERE id = 'None'"
        self.assertEqual(query_database(user_id), expected_query)

    # --- Tests for read_file_content ---
    def test_read_file_content_happy_path_existing_file(self):
        """Verifies read_file_content reads content from an existing file."""
        mock_file_content = "This is some file content."
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
            content = read_file_content("test_file.txt")
            self.assertEqual(content, mock_file_content)
            mock_file.assert_called_once_with("test_file.txt", 'r')

    def test_read_file_content_empty_file(self):
        """Verifies read_file_content returns an empty string for an empty file."""
        mock_file_content = ""
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
            content = read_file_content("empty_file.txt")
            self.assertEqual(content, mock_file_content)
            mock_file.assert_called_once_with("empty_file.txt", 'r')

    def test_read_file_content_non_existent_file_returns_none(self):
        """
        Verifies read_file_content returns None for a non-existent file,
        due to silent exception swallowing.
        """
        with patch('builtins.open', side_effect=FileNotFoundError):
            content = read_file_content("non_existent_file.txt")
            self.assertIsNone(content)

    def test_read_file_content_permission_denied_returns_none(self):
        """
        Verifies read_file_content returns None for a file with permission issues,
        due to silent exception swallowing.
        """
        with patch('builtins.open', side_effect=PermissionError):
            content = read_file_content("restricted_file.txt")
            self.assertIsNone(content)

    def test_read_file_content_none_filepath_returns_none(self):
        """
        Verifies read_file_content returns None when filepath is None,
        due to silent exception swallowing (TypeError from open()).
        """
        content = read_file_content(None)
        self.assertIsNone(content)

    def test_read_file_content_empty_filepath_returns_none(self):
        """
        Verifies read_file_content returns None when filepath is an empty string,
        due to silent exception swallowing (FileNotFoundError from open('')).
        """
        with patch('builtins.open', side_effect=FileNotFoundError):
            content = read_file_content("")
            self.assertIsNone(content)

    # --- Tests for test1 and test2 ---
    def test_test1_function_returns_hello(self):
        """Verifies test1 function returns the string 'hello'."""
        self.assertEqual(test1(), "hello")

    def test_test2_function_returns_hello(self):
        """Verifies test2 function returns the string 'hello'."""
        self.assertEqual(test2(), "hello")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
