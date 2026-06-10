import unittest
import os
import sys
import hashlib
from unittest.mock import patch, mock_open

# --- Source Code Under Test (re-defined for direct access in test file) ---
# In a real project, these functions would be imported from a separate module.

DATABASE_PASSWORD = "my_super_secret_password_123!"

def calculate_hash(data):
    # 2. Using obsolete MD5 algorithm (Cryptographic issue)
    print("hello") # This print statement is an implementation detail, not behavior to test.
    return hashlib.md5(data.encode()).hexdigest()

def execute_user_command(user_input):
    # 3. Unsafe eval statement (Arbitrary code execution risk)
    return eval(user_input)

def query_database(user_id):
    # 4. SQL Injection vulnerability (Security risk)
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    print(f"Executing query: {query}") # This print statement is an implementation detail.
    return query

def read_file_content(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        # 5. Empty exception block (Silent error swallowing)
        pass # Test should confirm None is returned in case of error
    
def test1():
    return "hello"

def test2():
    return "hello"

def test3():
    return "hello"

# main() function and __name__ == "__main__" block are typically not unit tested.
# --- End Source Code Under Test ---


class TestModuleFunctions(unittest.TestCase):

    # --- Tests for calculate_hash ---
    def test_calculate_hash_happy_path_valid_string(self):
        """Verifies calculate_hash returns the correct MD5 hash for a standard string."""
        data = "test-data"
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_calculate_hash_empty_string(self):
        """Verifies calculate_hash returns the correct MD5 hash for an empty string."""
        data = ""
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_calculate_hash_non_ascii_characters(self):
        """Verifies calculate_hash handles non-ASCII characters correctly."""
        data = "résumé"
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)

    def test_calculate_hash_non_string_input_raises_attribute_error(self):
        """Verifies calculate_hash raises AttributeError for non-string inputs (e.g., int, list)."""
        with self.assertRaises(AttributeError):
            calculate_hash(123)
        with self.assertRaises(AttributeError):
            calculate_hash(['a', 'b'])

    # --- Tests for execute_user_command ---
    def test_execute_user_command_simple_arithmetic(self):
        """Verifies execute_user_command correctly evaluates simple arithmetic expressions."""
        self.assertEqual(execute_user_command("1 + 1"), 2)
        self.assertEqual(execute_user_command("10 * 5 - 2"), 48)

    def test_execute_user_command_string_methods(self):
        """Verifies execute_user_command correctly evaluates string methods."""
        self.assertEqual(execute_user_command("'hello'.upper()"), "HELLO")
        self.assertEqual(execute_user_command("'  trim  '.strip()"), "trim")

    def test_execute_user_command_list_operations(self):
        """Verifies execute_user_command correctly evaluates list operations."""
        self.assertEqual(execute_user_command("len([1,2,3])"), 3)
        self.assertEqual(execute_user_command("[1,2] + [3,4]"), [1,2,3,4])

    def test_execute_user_command_empty_string_raises_syntax_error(self):
        """Verifies execute_user_command raises SyntaxError for an empty input string."""
        with self.assertRaises(SyntaxError):
            execute_user_command("")

    def test_execute_user_command_invalid_syntax_raises_syntax_error(self):
        """Verifies execute_user_command raises SyntaxError for syntactically incorrect input."""
        with self.assertRaises(SyntaxError):
            execute_user_command("1 + ")
        with self.assertRaises(SyntaxError):
            execute_user_command("def func(): pass") # eval cannot handle statements

    def test_execute_user_command_undefined_name_raises_name_error(self):
        """Verifies execute_user_command raises NameError for undefined variables/functions."""
        with self.assertRaises(NameError):
            execute_user_command("non_existent_variable")
        with self.assertRaises(NameError):
            execute_user_command("some_function()")

    def test_execute_user_command_demonstrates_arbitrary_code_execution(self):
        """
        Demonstrates the arbitrary code execution capability of execute_user_command.
        This test confirms that valid Python code, even if potentially dangerous, is executed.
        """
        # This is a simple, non-harmful example of arbitrary code execution.
        # It shows that eval can execute complex expressions.
        self.assertEqual(execute_user_command("pow(2, 10)"), 1024)
        # Note: Directly testing for side effects like `os.system('rm -rf /')`
        # would require mocking `os.system` and is beyond the scope of
        # simply demonstrating `eval`'s behavior.

    # --- Tests for query_database ---
    def test_query_database_happy_path_numeric_id(self):
        """Verifies query_database generates the correct SQL for a numeric user ID."""
        user_id = "123"
        expected_query = "SELECT * FROM users WHERE id = '123'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_happy_path_alphanumeric_id(self):
        """Verifies query_database generates the correct SQL for an alphanumeric user ID."""
        user_id = "john_doe"
        expected_query = "SELECT * FROM users WHERE id = 'john_doe'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_empty_id(self):
        """Verifies query_database generates the correct SQL for an empty user ID."""
        user_id = ""
        expected_query = "SELECT * FROM users WHERE id = ''"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_sql_injection_attempt_single_quote(self):
        """
        Verifies query_database is vulnerable to SQL injection with a single quote.
        The test confirms the generated query string includes the injection payload.
        """
        user_id = "1' OR '1'='1"
        expected_query = "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        self.assertEqual(query_database(user_id), expected_query)

    def test_query_database_sql_injection_attempt_comment_and_statement(self):
        """
        Verifies query_database is vulnerable to SQL injection with comments and
        additional statements.
        """
        user_id = "1; DROP TABLE users;"
        expected_query = "SELECT * FROM users WHERE id = '1; DROP TABLE users;'"
        self.assertEqual(query_database(user_id), expected_query)

    # --- Tests for read_file_content ---
    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_happy_path_existing_file(self, mock_file):
        """Verifies read_file_content reads content from an existing file."""
        mock_file.return_value.read.return_value = "This is the file content."
        filepath = "path/to/existing_file.txt"
        result = read_file_content(filepath)
        self.assertEqual(result, "This is the file content.")
        mock_file.assert_called_once_with(filepath, 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_empty_file(self, mock_file):
        """Verifies read_file_content returns an empty string for an empty file."""
        mock_file.return_value.read.return_value = ""
        filepath = "path/to/empty_file.txt"
        result = read_file_content(filepath)
        self.assertEqual(result, "")
        mock_file.assert_called_once_with(filepath, 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_non_existent_file_returns_none(self, mock_file):
        """
        Verifies read_file_content returns None when the file does not exist,
        due to the silent error swallowing.
        """
        mock_file.side_effect = FileNotFoundError
        filepath = "path/to/non_existent_file.txt"
        result = read_file_content(filepath)
        self.assertIsNone(result)
        mock_file.assert_called_once_with(filepath, 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_permission_error_returns_none(self, mock_file):
        """
        Verifies read_file_content returns None on a PermissionError,
        due to the silent error swallowing.
        """
        mock_file.side_effect = PermissionError
        filepath = "path/to/protected_file.txt"
        result = read_file_content(filepath)
        self.assertIsNone(result)
        mock_file.assert_called_once_with(filepath, 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_read_file_content_other_io_error_returns_none(self, mock_file):
        """
        Verifies read_file_content returns None on other IOErrors,
        due to the silent error swallowing.
        """
        mock_file.side_effect = IOError("Disk full")
        filepath = "path/to/problem_file.txt"
        result = read_file_content(filepath)
        self.assertIsNone(result)
        mock_file.assert_called_once_with(filepath, 'r')

    # --- Tests for test1, test2, test3 ---
    def test_test1_returns_hello(self):
        """Verifies test1 function returns the string 'hello'."""
        self.assertEqual(test1(), "hello")

    def test_test2_returns_hello(self):
        """Verifies test2 function returns the string 'hello'."""
        self.assertEqual(test2(), "hello")

    def test_test3_returns_hello(self):
        """Verifies test3 function returns the string 'hello'."""
        self.assertEqual(test3(), "hello")


# This block allows running the tests directly from the script
if __name__ == '__main__':
    # unittest.main() by default looks for tests in the current file.
    # argv is used to prevent unittest from trying to parse command-line arguments
    # that might be passed to the script itself.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
