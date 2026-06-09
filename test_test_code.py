import unittest
import os
import sys
import hashlib
import tempfile
from unittest.mock import patch, mock_open

# Assuming the provided code is in a file named 'my_module.py'
# For this example, we'll put the functions directly here for simplicity
# In a real scenario, you would import them:
# from my_module import calculate_hash, execute_user_command, query_database, read_file_content, test1

# --- Start of the code to be tested (for self-contained example) ---
# This block would typically be in a separate file like 'my_module.py'

DATABASE_PASSWORD = "my_super_secret_password_123!"

def calculate_hash(data):
    print("hello") # This print statement is an implementation detail, not behavior to test
    return hashlib.md5(data.encode()).hexdigest()

def execute_user_command(user_input):
    return eval(user_input)

def query_database(user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    print(f"Executing query: {query}") # This print statement is an implementation detail
    return query

def read_file_content(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        # Silent error swallowing - this behavior should be tested
        pass
    
def test1():
    return "hello"

# --- End of the code to be tested ---


class TestMyModule(unittest.TestCase):

    def test_calculate_hash_happy_path(self):
        """
        Verifies calculate_hash returns the correct MD5 hex digest for valid input.
        """
        test_data = "hello world"
        expected_hash = hashlib.md5(test_data.encode()).hexdigest()
        self.assertEqual(calculate_hash(test_data), expected_hash)

    def test_calculate_hash_empty_string(self):
        """
        Verifies calculate_hash handles an empty string input correctly.
        """
        test_data = ""
        expected_hash = hashlib.md5(test_data.encode()).hexdigest()
        self.assertEqual(calculate_hash(test_data), expected_hash)

    def test_calculate_hash_non_string_input(self):
        """
        Verifies calculate_hash raises an AttributeError when given non-string input
        because .encode() is called on it.
        """
        with self.assertRaises(AttributeError):
            calculate_hash(123)
        with self.assertRaises(AttributeError):
            calculate_hash(None)
        with self.assertRaises(AttributeError):
            calculate_hash(['a', 'b'])

    def test_execute_user_command_happy_path_arithmetic(self):
        """
        Verifies execute_user_command correctly evaluates simple arithmetic expressions.
        """
        self.assertEqual(execute_user_command("1 + 1"), 2)
        self.assertEqual(execute_user_command("10 * 5 - 2"), 48)
        self.assertEqual(execute_user_command("len('test')"), 4)

    def test_execute_user_command_invalid_syntax(self):
        """
        Verifies execute_user_command raises a SyntaxError for invalid Python syntax.
        """
        with self.assertRaises(SyntaxError):
            execute_user_command("1 +")
        with self.assertRaises(NameError): # NameError for undefined variables
            execute_user_command("undefined_variable")

    def test_execute_user_command_malicious_input_demonstration(self):
        """
        Demonstrates the arbitrary code execution vulnerability of execute_user_command.
        This test confirms the function's dangerous behavior, it does not fix it.
        """
        # This is a dangerous test, but it proves the vulnerability.
        # In a real system, you would never allow eval with untrusted input.
        # We'll use a mock to capture stdout to avoid actual side effects in the test runner.
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = execute_user_command("print('Malicious code executed!')")
            self.assertIsNone(result) # print returns None
            self.assertIn("Malicious code executed!", mock_stdout.getvalue())

    def test_query_database_happy_path(self):
        """
        Verifies query_database generates the correct SQL query string for a valid user ID.
        """
        user_id = "123"
        expected_query = "SELECT * FROM users WHERE id = '123'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_empty_user_id(self):
        """
        Verifies query_database generates the correct SQL query string for an empty user ID.
        """
        user_id = ""
        expected_query = "SELECT * FROM users WHERE id = ''"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_sql_injection_demonstration(self):
        """
        Demonstrates the SQL injection vulnerability of query_database.
        This test confirms the function's dangerous behavior, it does not fix it.
        """
        # A common SQL injection payload
        user_id = "1' OR '1'='1"
        expected_query = "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        self.assertEqual(query_database(user_id), expected_query)

        # Another payload to demonstrate
        user_id_drop = "1'; DROP TABLE users; --"
        expected_query_drop = "SELECT * FROM users WHERE id = '1'; DROP TABLE users; --'"
        self.assertEqual(query_database(user_id_drop), expected_query_drop)

    def test_read_file_content_happy_path(self):
        """
        Verifies read_file_content correctly reads content from an existing file.
        Uses a temporary file for testing.
        """
        test_content = "This is a test file content.\nLine 2."
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(test_content)
            tmp_file_path = tmp_file.name
        
        try:
            self.assertEqual(read_file_content(tmp_file_path), test_content)
        finally:
            os.remove(tmp_file_path)

    def test_read_file_content_empty_file(self):
        """
        Verifies read_file_content returns an empty string for an empty file.
        Uses a temporary file for testing.
        """
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp_file:
            # File is created but nothing is written
            tmp_file_path = tmp_file.name
        
        try:
            self.assertEqual(read_file_content(tmp_file_path), "")
        finally:
            os.remove(tmp_file_path)

    def test_read_file_content_non_existent_file(self):
        """
        Verifies read_file_content returns None for a non-existent file due to
        the silent error swallowing.
        """
        non_existent_path = "this_file_does_not_exist_12345.txt"
        self.assertIsNone(read_file_content(non_existent_path))

    def test_read_file_content_permission_denied(self):
        """
        Verifies read_file_content returns None when file permissions prevent reading,
        due to the silent error swallowing.
        This test mocks the open function to simulate PermissionError.
        """
        mock_file_path = "/path/to/restricted_file.txt"
        
        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")) as mock_open_func:
            self.assertIsNone(read_file_content(mock_file_path))
            mock_open_func.assert_called_once_with(mock_file_path, 'r')

    def test_test1_happy_path(self):
        """
        Verifies test1 returns the string "hello".
        """
        self.assertEqual(test1(), "hello")

# To run the tests from the command line:
# python -m unittest your_test_file_name.py
if __name__ == '__main__':
    # Add a dummy io import for the eval test demonstration
    import io 
    unittest.main()
