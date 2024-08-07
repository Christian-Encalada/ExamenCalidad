from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import unittest

class TestApp(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("http://localhost:5000")  # URL de tu aplicación

    def tearDown(self):
        self.driver.quit()

    def test_login(self):
        driver = self.driver
        
        # Navegar a la página de login
        login_button = driver.find_element(By.LINK_TEXT, "Login")
        login_button.click()
        
        # Completar el formulario de login
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        
        username_input.send_keys("testuser")
        password_input.send_keys("password123")
        password_input.send_keys(Keys.RETURN)
        
        # Verificar que el login fue exitoso
        welcome_message = driver.find_element(By.ID, "welcome_message")
        self.assertIn("Welcome", welcome_message.text)

    def test_registration(self):
        driver = self.driver
        
        # Navegar a la página de registro
        register_button = driver.find_element(By.LINK_TEXT, "Register")
        register_button.click()
        
        # Completar el formulario de registro
        id_input = driver.find_element(By.NAME, "id")
        name_input = driver.find_element(By.NAME, "name")
        password_input = driver.find_element(By.NAME, "password")
        
        id_input.send_keys("12345")
        name_input.send_keys("Test User")
        password_input.send_keys("password123")
        password_input.send_keys(Keys.RETURN)
        
        # Verificar que el registro fue exitoso
        success_message = driver.find_element(By.ID, "success_message")
        self.assertIn("Registration successful", success_message.text)

if __name__ == "__main__":
    unittest.main()
