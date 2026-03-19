import unittest
import subprocess
from unittest.mock import patch, MagicMock
import report_tool  # основний файл

class TestSupportTool(unittest.TestCase):

    # Тест 1: Перевірка збору інформації про систему 
    @patch('socket.gethostname')
    @patch('os.getlogin')
    def test_get_system_info(self, mock_login, mock_host):
        mock_host.return_value = "TestPC"
        mock_login.return_value = "User1"
        
        host, user, ip = report_tool.get_system_info()
        
        self.assertEqual(host, "TestPC")
        self.assertEqual(user, "User1")
        

    # Тест 2: Валідація пінгу 
    @patch('subprocess.run')
    def test_ping_servers_success(self, mock_run):
        mock_run.return_value.returncode = 0  
        
        result = report_tool.ping_servers()
        self.assertIn("OK", result)

    # Тест 3: Валідація пінгу 
    @patch('subprocess.run')
    def test_ping_servers_fail(self, mock_run):
        # Імітуємо помилку 
        mock_run.side_effect = subprocess.CalledProcessError(1, ['ping'])
        
        result = report_tool.ping_servers()
        self.assertIn("FAIL", result)

    # Тест 4: Перевірка запису в БД 
    @patch('psycopg2.connect')
    def test_save_to_db_success(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        
        success, msg = report_tool.save_to_database(
            "PC", "User", "1.1.1.1", "Ping OK", "General", "Problem", "path/sc.png"
        )
        
        self.assertTrue(success)
        self.assertIn("Успішно", msg)
        mock_cursor.execute.assert_called_once() 

    # Тест 5: Перевірка обробки помилки БД 
    @patch('psycopg2.connect')
    def test_save_to_db_fail(self, mock_connect):
        # Імітуємо розрив з'єднання
        mock_connect.side_effect = Exception("DB Connection Lost")
        
        success, msg = report_tool.save_to_database(
            "PC", "User", "1.1.1.1", "Ping OK", "General", "Problem", None
        )
        
        self.assertFalse(success) 
        self.assertIn("Помилка БД", msg)

if __name__ == '__main__':
    unittest.main() 