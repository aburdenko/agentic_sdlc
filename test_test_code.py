import unittest
import os
import sys
import hashlib
from unittest.mock import patch, mock_open

# --- Start of copied source code for self-contained testing ---
# In a real project, you would import these functions from their module:
# from your_module_name import calculate_hash, execute_user_command, query_database, read_file_content, test1, test2

# 1. Hardcoded sensitive key (Security risk) - Not directly testable for behavior
DATABASE_PASSWORD = "my_super_secret_password_123!"

def calculate_hash(data):
    # 2. Using obsolete MD5 algorithm (Cryptographic issue)
    # print("hello") # Side effect, not part of core logic to test
    return hashlib.md5(data.encode()).hexdigest()

def execute_user_command(user_input):
    # 3. Unsafe eval statement (Arbitrary code execution risk)
    return eval(user_input)

def query_database(user_id):
    # 4. SQL Injection vulnerability (Security risk)
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    # print(f"Executing query: {query}") # Side effect
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

# The main() function and __name__ == "__main__" block are typically not
# unit tested as they handle program execution flow and side effects.
# --- End of copied source code ---


class TestVulnerableCode(unittest.TestCase):

    def test_calculate_hash_happy_path(self):
        """
        Verifies calculate_hash returns the correct MD5 hash for a standard string.
        """
        data = "test-data"
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_calculate_hash_empty_string(self):
        """
        Verifies calculate_hash handles an empty string correctly.
        """
        data = ""
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_calculate_hash_special_characters(self):
        """
        Verifies calculate_hash handles strings with special characters.
        """
        data = "!@#$%^&*()_+"
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_execute_user_command_happy_path_simple_expression(self):
        """
        Verifies execute_user_command evaluates simple, valid Python expressions.
        """
        self.assertEqual(execute_user_command("1 + 1"), 2)
        self.assertEqual(execute_user_command("'hello' + ' world'"), "hello world")
        self.assertEqual(execute_user_command("len([1, 2, 3])"), 3)

    def test_execute_user_command_invalid_syntax(self):
        """
        Verifies execute_user_command raises a SyntaxError for invalid Python syntax.
        """
        with self.assertRaises(SyntaxError):
            execute_user_command("1 +")
        with self.assertRaises(NameError):
            execute_user_command("undefined_variable")
        with self.assertRaises(TypeError):
            execute_user_command("len(123)") # len() expects a sequence, not an int

    @patch('os.system')
    def test_execute_user_command_demonstrates_arbitrary_code_execution(self, mock_os_system):
        """
        Demonstrates the arbitrary code execution vulnerability of execute_user_command
        by attempting to call os.system.
        """
        # This test confirms that the eval statement *would* execute arbitrary code.
        # We mock os.system to prevent actual system calls during the test run.
        command_to_execute = "os.system('echo Test Command Executed')"
        result = execute_user_command(command_to_execute)
        
        # eval returns the result of the last expression. os.system typically returns 0 on success.
        self.assertEqual(result, 0)
        mock_os_system.assert_called_once_with('echo Test Command Executed')

    def test_query_database_happy_path(self):
        """
        Verifies query_database constructs a correct SQL query for a valid user ID.
        """
        user_id = "123"
        expected_query = "SELECT * FROM users WHERE id = '123'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_sql_injection_attempt(self):
        """
        Demonstrates the SQL Injection vulnerability by showing the constructed query
        with a malicious user ID.
        """
        user_id = "1' OR 1=1 --"
        expected_query = "SELECT * FROM users WHERE id = '1' OR 1=1 --'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_empty_user_id(self):
        """
        Verifies query_database handles an empty user ID in the query string.
        """
        user_id = ""
        expected_query = "SELECT * FROM users WHERE id = ''"
        self.assertEqual(query_database(user_id), expected_query)

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_happy_path(self, mock_file):
        """
        Verifies read_file_content reads content from an existing file.
        """
        mock_file.return_value.read.return_value = "This is some file content."
        self.assertEqual(read_file_content("path/to/file.txt"), "This is some file content.")
        mock_file.assert_called_once_with("path/to/file.txt", 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_empty_file(self, mock_file):
        """
        Verifies read_file_content returns an empty string for an empty file.
        """
        mock_file.return_value.read.return_value = ""
        self.assertEqual(read_file_content("path/to/empty.txt"), "")
        mock_file.assert_called_once_with("path/to/empty.txt", 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_non_existent_file(self, mock_file):
        """
        Verifies read_file_content returns None when the file does not exist,
        due to the silent exception swallowing.
        """
        mock_file.side_effect = FileNotFoundError
        self.assertIsNone(read_file_content("path/to/nonexistent.txt"))
        mock_file.assert_called_once_with("path/to/nonexistent.txt", 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_permission_denied(self, mock_file):
        """
        Verifies read_file_content returns None on permission errors,
        due to the silent exception swallowing.
        """
        mock_file.side_effect = PermissionError
        self.assertIsNone(read_file_content("path/to/protected.txt"))
        mock_file.assert_called_once_with("path/to/protected.txt", 'r')

    def test_test1_returns_hello(self):
        """
        Verifies the test1 function returns the expected string.
        """
        self.assertEqual(test1(), "hello")

    def test_test2_returns_hello(self):
        """
        Verifies the test2 function returns the expected string.
        """
        self.assertEqual(test2(), "hello")

if __name__ == '__main__':
    # This allows running the tests directly from the command line
    # `argv=['first-arg-is-ignored']` is a common workaround for unittest.main
    # when running from environments that might pass extra arguments.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
