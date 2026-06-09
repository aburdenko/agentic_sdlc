import unittest
import os
import sys
import hashlib
from unittest.mock import patch, mock_open
from io import StringIO

# --- Start of the source code to be tested (included for self-contained execution) ---
# Note: In a real project, this code would be in a separate module (e.g., `my_module.py`)
# and imported as `from my_module import ...`. For this exercise, it's included directly.

# 1. Hardcoded sensitive key (Security risk)
DATABASE_PASSWORD = "my_super_secret_password_123!"

def calculate_hash(data):
    # 2. Using obsolete MD5 algorithm (Cryptographic issue)
    # print("hello") # This print statement is a side effect, we'll mock stdout for it.
    return hashlib.md5(data.encode()).hexdigest()

def execute_user_command(user_input):
    # 3. Unsafe eval statement (Arbitrary code execution risk)
    return eval(user_input)

def query_database(user_id):
    # 4. SQL Injection vulnerability (Security risk)
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    # print(f"Executing query: {query}") # Side effect, we'll mock stdout for it.
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

# The `main()` function and `if __name__ == "__main__":` block are typically
# not unit tested directly as they serve as entry points and orchestrators,
# often involving side effects that are better tested at the individual function level.
# --- End of the source code to be tested ---


class TestSecurityVulnerabilities(unittest.TestCase):
    """
    Tests related to security vulnerabilities and bad practices identified in the code.
    These tests aim to demonstrate the problematic behavior or confirm its existence.
    """

    def test_database_password_is_hardcoded(self):
        """
        Verifies that DATABASE_PASSWORD is hardcoded with the expected sensitive value.
        This test confirms the existence of the identified security risk.
        """
        self.assertIsNotNone(DATABASE_PASSWORD)
        self.assertIsInstance(DATABASE_PASSWORD, str)
        self.assertEqual(DATABASE_PASSWORD, "my_super_secret_password_123!")

    def test_sql_injection_vulnerability_demonstration(self):
        """
        Demonstrates the SQL Injection vulnerability in query_database.
        Verifies that malicious input is directly embedded into the query string.
        """
        malicious_user_id = "1' OR '1'='1"
        expected_query = "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            actual_query = query_database(malicious_user_id)
            self.assertEqual(actual_query, expected_query)
            self.assertIn(f"Executing query: {expected_query}", fake_out.getvalue())

        malicious_user_id_drop = "1; DROP TABLE users;"
        expected_query_drop = "SELECT * FROM users WHERE id = '1; DROP TABLE users;'"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            actual_query_drop = query_database(malicious_user_id_drop)
            self.assertEqual(actual_query_drop, expected_query_drop)
            self.assertIn(f"Executing query: {expected_query_drop}", fake_out.getvalue())

    def test_eval_arbitrary_code_execution_demonstration(self):
        """
        Demonstrates the arbitrary code execution risk of execute_user_command using eval().
        Tests simple expressions and mocks os.system to show potential for system calls.
        """
        self.assertEqual(execute_user_command("1 + 1"), 2)
        self.assertEqual(execute_user_command("'hello'.upper()"), "HELLO")
        self.assertEqual(execute_user_command("len([1,2,3])"), 3)

        # Demonstrate potential for system calls by mocking os.system
        with patch('os.system') as mock_os_system:
            execute_user_command("os.system('echo hello from eval')")
            mock_os_system.assert_called_once_with('echo hello from eval')

        # Demonstrate access to built-in functions
        self.assertEqual(execute_user_command("abs(-5)"), 5)

    def test_empty_exception_block_swallows_errors_in_read_file_content(self):
        """
        Verifies that read_file_content silently swallows exceptions and returns None.
        This highlights the silent error swallowing issue.
        """
        # Mock open to simulate FileNotFoundError
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = read_file_content("non_existent_file.txt")
            self.assertIsNone(result)

        # Mock open to simulate a generic IOError (e.g., permission denied)
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = read_file_content("permission_denied_file.txt")
            self.assertIsNone(result)

        # Test with None filepath, which would cause TypeError in open()
        result = read_file_content(None)
        self.assertIsNone(result)

        # Test with empty string filepath, which would cause FileNotFoundError in open()
        result = read_file_content("")
        self.assertIsNone(result)


class TestCalculateHash(unittest.TestCase):
    """
    Tests for the calculate_hash function, including happy paths and edge cases.
    """

    @patch('sys.stdout', new_callable=StringIO)
    def test_calculate_hash_happy_path_standard_string(self, mock_stdout):
        """
        Tests calculate_hash with a standard string input.
        """
        data = "test-data"
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)
        # Assert that no unexpected output was printed to stdout
        self.assertEqual(mock_stdout.getvalue(), "")

    @patch('sys.stdout', new_callable=StringIO)
    def test_calculate_hash_empty_string(self, mock_stdout):
        """
        Tests calculate_hash with an empty string input.
        """
        data = ""
        expected_hash = hashlib.md5(data.encode()).hexdigest()
        self.assertEqual(calculate_hash(data), expected_hash)
        self.assertEqual(mock_stdout.getvalue(), "")

    def test_calculate_hash_non_string_input_raises_attribute_error(self):
        """
        Tests calculate_hash with non-string inputs, expecting an AttributeError
        due to the `.encode()` call.
        """
        with self.assertRaises(AttributeError):
            calculate_hash(123)
        with self.assertRaises(AttributeError):
            calculate_hash(None)
        with self.assertRaises(AttributeError):
            calculate_hash(['a', 'b'])

    def test_calculate_hash_output_format_and_length(self):
        """
        Verifies that the output of calculate_hash is a 32-character hexadecimal string,
        consistent with an MD5 hash.
        """
        data = "check_md5_format"
        hash_result = calculate_hash(data)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash_result))


class TestExecuteUserCommand(unittest.TestCase):
    """
    Tests for the execute_user_command function, covering various valid and invalid inputs.
    """

    def test_execute_user_command_arithmetic_expressions(self):
        """
        Tests execute_user_command with basic arithmetic operations.
        """
        self.assertEqual(execute_user_command("1 + 2"), 3)
        self.assertEqual(execute_user_command("10 / 2"), 5.0)
        self.assertEqual(execute_user_command("(3 * 4) - 1"), 11)

    def test_execute_user_command_string_operations(self):
        """
        Tests execute_user_command with string manipulation methods.
        """
        self.assertEqual(execute_user_command("'hello' + ' world'"), "hello world")
        self.assertEqual(execute_user_command("'python'.upper()"), "PYTHON")
        self.assertEqual(execute_user_command("' test '.strip()"), "test")

    def test_execute_user_command_list_operations(self):
        """
        Tests execute_user_command with basic list operations.
        """
        self.assertEqual(execute_user_command("[1, 2, 3][0]"), 1)
        self.assertEqual(execute_user_command("len([1, 2, 3])"), 3)

    def test_execute_user_command_invalid_python_syntax_raises_syntax_error(self):
        """
        Tests execute_user_command with syntactically incorrect input.
        """
        with self.assertRaises(SyntaxError):
            execute_user_command("1 +")
        with self.assertRaises(SyntaxError):
            execute_user_command("def func(): pass") # eval cannot execute statements

    def test_execute_user_command_undefined_name_raises_name_error(self):
        """
        Tests execute_user_command with an undefined variable name.
        """
        with self.assertRaises(NameError):
            execute_user_command("undefined_var")

    def test_execute_user_command_type_mismatch_raises_type_error(self):
        """
        Tests execute_user_command with operations involving incompatible types.
        """
        with self.assertRaises(TypeError):
            execute_user_command("1 + 'a'")

    def test_execute_user_command_empty_string_raises_syntax_error(self):
        """
        Tests execute_user_command with an empty string input.
        """
        with self.assertRaises(SyntaxError):
            execute_user_command("")

    def test_execute_user_command_none_input_raises_type_error(self):
        """
        Tests execute_user_command with None as input.
        """
        with self.assertRaises(TypeError):
            execute_user_command(None)


class TestQueryDatabase(unittest.TestCase):
    """
    Tests for the query_database function, focusing on query construction.
    """

    @patch('sys.stdout', new_callable=StringIO)
    def test_query_database_happy_path_integer_id(self, mock_stdout):
        """
        Tests query_database with an integer user ID.
        """
        user_id = 123
        expected_query = "SELECT * FROM users WHERE id = '123'"
        self.assertEqual(query_database(user_id), expected_query)
        self.assertIn(f"Executing query: {expected_query}", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_query_database_happy_path_string_id(self, mock_stdout):
        """
        Tests query_database with a string user ID.
        """
        user_id = "abc"
        expected_query = "SELECT * FROM users WHERE id = 'abc'"
        self.assertEqual(query_database(user_id), expected_query)
        self.assertIn(f"Executing query: {expected_query}", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_query_database_empty_string_id(self, mock_stdout):
        """
        Tests query_database with an empty string user ID.
        """
        user_id = ""
        expected_query = "SELECT * FROM users WHERE id = ''"
        self.assertEqual(query_database(user_id), expected_query)
        self.assertIn(f"Executing query: {expected_query}", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_query_database_none_id(self, mock_stdout):
        """
        Tests query_database with None as user ID, expecting it to be converted to 'None'.
        """
        user_id = None
        expected_query = "SELECT * FROM users WHERE id = 'None'"
        self.assertEqual(query_database(user_id), expected_query)
        self.assertIn(f"Executing query: {expected_query}", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_query_database_id_with_single_quote(self, mock_stdout):
        """
        Tests query_database with a user ID containing a single quote,
        demonstrating how it breaks the SQL string literal.
        """
        user_id = "john's_id"
        expected_query = "SELECT * FROM users WHERE id = 'john's_id'"
        self.assertEqual(query_database(user_id), expected_query)
        self.assertIn(f"Executing query: {expected_query}", mock_stdout.getvalue())


class TestReadFileContent(unittest.TestCase):
    """
    Tests for the read_file_content function, covering file existence and error handling.
    """

    def setUp(self):
        """
        Sets up temporary files for testing before each test method.
        """
        self.test_file_path = "temp_test_file.txt"
        with open(self.test_file_path, 'w') as f:
            f.write("Hello, world!\nThis is a test file.")
        
        self.empty_file_path = "empty_test_file.txt"
        with open(self.empty_file_path, 'w') as f:
            pass # Create an empty file

    def tearDown(self):
        """
        Cleans up temporary files after each test method.
        """
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        if os.path.exists(self.empty_file_path):
            os.remove(self.empty_file_path)

    def test_read_file_content_happy_path_existing_file_with_content(self):
        """
        Tests reading an existing file that contains content.
        """
        expected_content = "Hello, world!\nThis is a test file."
        self.assertEqual(read_file_content(self.test_file_path), expected_content)

    def test_read_file_content_happy_path_existing_empty_file(self):
        """
        Tests reading an existing file that is empty.
        """
        self.assertEqual(read_file_content(self.empty_file_path), "")

    def test_read_file_content_non_existent_file_returns_none(self):
        """
        Tests reading a file that does not exist, expecting None due to error swallowing.
        """
        self.assertIsNone(read_file_content("definitely_non_existent_file.txt"))

    def test_read_file_content_none_filepath_returns_none(self):
        """
        Tests read_file_content with None as the filepath, expecting None.
        """
        self.assertIsNone(read_file_content(None))

    def test_read_file_content_empty_string_filepath_returns_none(self):
        """
        Tests read_file_content with an empty string as the filepath, expecting None.
        """
        self.assertIsNone(read_file_content(""))

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_read_file_content_permission_denied_returns_none(self, mock_open):
        """
        Tests read_file_content when a permission error occurs, expecting None.
        Mocks `open` to simulate the IOError.
        """
        self.assertIsNone(read_file_content("file_with_permission_issues.txt"))
        mock_open.assert_called_once_with("file_with_permission_issues.txt", 'r')


class TestSimpleFunctions(unittest.TestCase):
    """
    Tests for the simple utility functions test1 and test2.
    """

    def test_test1_returns_hello(self):
        """
        Verifies that test1 returns the string "hello".
        """
        self.assertEqual(test1(), "hello")

    def test_test2_returns_hello(self):
        """
        Verifies that test2 returns the string "hello".
        """
        self.assertEqual(test2(), "hello")


# This block allows running the tests directly from the script
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
