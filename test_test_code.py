import unittest
import os
import sys
import hashlib
from unittest.mock import patch, mock_open

# --- Start of functions to be tested (copied from prompt for self-containment) ---
# Note: In a real-world scenario, these functions would typically be imported
# from a separate module, e.g., `from your_module import calculate_hash, ...`.
# They are included here directly to fulfill the request for "ONLY the executable
# Python unit test code" within a single markdown block.

# 1. Hardcoded sensitive key (Security risk) - Not directly testable as a function
DATABASE_PASSWORD = "my_super_secret_password_123!"

def calculate_hash(data):
    # 2. Using obsolete MD5 algorithm (Cryptographic issue)
    return hashlib.md5(data.encode()).hexdigest()

def execute_user_command(user_input):
    # 3. Unsafe eval statement (Arbitrary code execution risk)
    return eval(user_input)

def query_database(user_id):
    # 4. SQL Injection vulnerability (Security risk)
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    # print(f"Executing query: {query}") # Removed print for unit testing
    return query

def read_file_content(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        # 5. Empty exception block (Silent error swallowing)
        pass

# --- End of functions to be tested ---


class TestVulnerableCode(unittest.TestCase):

    # --- Tests for calculate_hash ---
    def test_calculate_hash_happy_path_string(self):
        """
        Verifies calculate_hash returns the correct MD5 hash for a standard string.
        """
        self.assertEqual(calculate_hash("hello world"), "5eb63bbbe01eeed093cb22bb8f5acdc3")
        self.assertEqual(calculate_hash("python"), "23eeeb4347bdd26bfc6b7ee9a3b755dd")

    def test_calculate_hash_empty_string(self):
        """
        Verifies calculate_hash returns the correct MD5 hash for an empty string.
        """
        self.assertEqual(calculate_hash(""), "d41d8cd98f00b204e9800998ecf8427e")

    def test_calculate_hash_non_string_input_raises_attribute_error(self):
        """
        Verifies calculate_hash raises AttributeError when given non-string input,
        as `data.encode()` is called.
        """
        with self.assertRaises(AttributeError):
            calculate_hash(123)
        with self.assertRaises(AttributeError):
            calculate_hash(None)
        with self.assertRaises(AttributeError):
            calculate_hash(['list', 'of', 'strings'])

    # --- Tests for execute_user_command ---
    def test_execute_user_command_happy_path_arithmetic(self):
        """
        Verifies execute_user_command correctly evaluates simple arithmetic expressions.
        """
        self.assertEqual(execute_user_command("1 + 1"), 2)
        self.assertEqual(execute_user_command("10 * 5 - 2"), 48)

    def test_execute_user_command_happy_path_string_methods(self):
        """
        Verifies execute_user_command correctly evaluates string methods.
        """
        self.assertEqual(execute_user_command("'hello'.upper()"), "HELLO")
        self.assertEqual(execute_user_command("len('test')"), 4)

    def test_execute_user_command_empty_string_raises_syntax_error(self):
        """
        Verifies execute_user_command raises SyntaxError for an empty input string.
        """
        with self.assertRaises(SyntaxError):
            execute_user_command("")

    def test_execute_user_command_invalid_syntax_raises_syntax_error(self):
        """
        Verifies execute_user_command raises SyntaxError for syntactically incorrect input.
        """
        with self.assertRaises(SyntaxError):
            execute_user_command("1 +")
        with self.assertRaises(SyntaxError):
            execute_user_command("def func(): pass") # eval doesn't allow statements

    def test_execute_user_command_undefined_variable_raises_name_error(self):
        """
        Verifies execute_user_command raises NameError when trying to evaluate
        an undefined variable.
        """
        with self.assertRaises(NameError):
            execute_user_command("undefined_variable")

    def test_execute_user_command_arbitrary_code_execution_demonstration(self):
        """
        Demonstrates the arbitrary code execution capability of `eval` by
        executing a built-in function and verifying its effect.
        This test highlights the vulnerability by showing what `eval` can do.
        """
        # Test execution of a simple built-in function
        self.assertEqual(execute_user_command("abs(-5)"), 5)

        # Test execution of a function from an imported module (like os)
        # This shows that eval can access the global scope, including imported modules.
        # We mock os.getcwd to avoid actual file system interaction in a unit test.
        with patch('os.getcwd', return_value='/mock/path') as mock_getcwd:
            result = execute_user_command("__import__('os').getcwd()")
            self.assertEqual(result, '/mock/path')
            mock_getcwd.assert_called_once()

        # Test a side effect like printing
        with patch('builtins.print') as mock_print:
            execute_user_command("print('eval was here')")
            mock_print.assert_called_once_with('eval was here')

    # --- Tests for query_database ---
    def test_query_database_happy_path_integer_id(self):
        """
        Verifies query_database generates the correct SQL query for an integer user ID.
        """
        expected_query = "SELECT * FROM users WHERE id = '123'"
        self.assertEqual(query_database(123), expected_query)

    def test_query_database_happy_path_string_id(self):
        """
        Verifies query_database generates the correct SQL query for a string user ID.
        """
        expected_query = "SELECT * FROM users WHERE id = 'john_doe'"
        self.assertEqual(query_database("john_doe"), expected_query)

    def test_query_database_empty_string_id(self):
        """
        Verifies query_database generates the correct SQL query for an empty string ID.
        """
        expected_query = "SELECT * FROM users WHERE id = ''"
        self.assertEqual(query_database(""), expected_query)

    def test_query_database_none_id(self):
        """
        Verifies query_database handles None as user ID by converting it to the string 'None'.
        """
        expected_query = "SELECT * FROM users WHERE id = 'None'"
        self.assertEqual(query_database(None), expected_query)

    def test_query_database_sql_injection_attempt_simple(self):
        """
        Demonstrates the SQL injection vulnerability by showing how a malicious
        input modifies the generated query.
        """
        malicious_id = "1' OR '1'='1"
        expected_query = "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        self.assertEqual(query_database(malicious_id), expected_query)

    def test_query_database_sql_injection_attempt_with_comment(self):
        """
        Demonstrates a more advanced SQL injection attempt using comments.
        """
        malicious_id = "1'; DROP TABLE users; --"
        expected_query = "SELECT * FROM users WHERE id = '1'; DROP TABLE users; --'"
        self.assertEqual(query_database(malicious_id), expected_query)

    # --- Tests for read_file_content ---
    def test_read_file_content_happy_path_existing_file(self):
        """
        Verifies read_file_content correctly reads content from an existing file.
        Uses mock_open to simulate file system interaction.
        """
        mock_file_content = "This is some test file content.\nLine 2."
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
            result = read_file_content("path/to/existing_file.txt")
            self.assertEqual(result, mock_file_content)
            mock_file.assert_called_once_with("path/to/existing_file.txt", 'r')

    def test_read_file_content_empty_file(self):
        """
        Verifies read_file_content returns an empty string for an empty file.
        """
        mock_file_content = ""
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
            result = read_file_content("path/to/empty_file.txt")
            self.assertEqual(result, "")
            mock_file.assert_called_once_with("path/to/empty_file.txt", 'r')

    def test_read_file_content_non_existent_file_returns_none(self):
        """
        Verifies read_file_content returns None when the file does not exist,
        due to the silent error swallowing.
        """
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = read_file_content("path/to/non_existent_file.txt")
            self.assertIsNone(result)

    def test_read_file_content_permission_denied_returns_none(self):
        """
        Verifies read_file_content returns None when there's a permission error,
        due to the silent error swallowing.
        """
        with patch('builtins.open', side_effect=PermissionError):
            result = read_file_content("path/to/protected_file.txt")
            self.assertIsNone(result)

    def test_read_file_content_io_error_returns_none(self):
        """
        Verifies read_file_content returns None for a generic IOError,
        due to the silent error swallowing.
        """
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = read_file_content("path/to/file.txt")
            self.assertIsNone(result)

    def test_read_file_content_none_filepath_returns_none(self):
        """
        Verifies read_file_content returns None when filepath is None,
        as `open()` would raise a TypeError, which is then swallowed.
        """
        with patch('builtins.open', side_effect=TypeError("expected str, bytes or os.PathLike object, not NoneType")):
            result = read_file_content(None)
            self.assertIsNone(result)

    def test_read_file_content_invalid_filepath_type_returns_none(self):
        """
        Verifies read_file_content returns None when filepath is of an invalid type (e.g., int),
        as `open()` would raise a TypeError, which is then swallowed.
        """
        with patch('builtins.open', side_effect=TypeError("expected str, bytes or os.PathLike object, not int")):
            result = read_file_content(12345)
            self.assertIsNone(result)


# This allows the tests to be run directly from the command line
if __name__ == '__main__':
    # Use argv to prevent unittest from trying to parse command line arguments
    # that might be intended for the script itself, and exit=False to allow
    # the script to continue or be run in environments like IDEs without exiting.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
