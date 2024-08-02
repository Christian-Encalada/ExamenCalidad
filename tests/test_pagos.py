from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest

class TestPagoEnLinea(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:5000")

    def test_registro(self):
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Registro").click()
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "email").send_keys("test@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verificar mensaje de éxito
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("Registro exitoso", success_message.text)

    def test_login(self):
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verificar redirección a home
        self.assertIn("home", driver.current_url)

    def test_pago(self):
        self.test_login()  # Iniciar sesión primero

        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Realizar Pago").click()
        driver.find_element(By.ID, "monto").send_keys("10.00")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verificar mensaje de éxito
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("Pago realizado con éxito", success_message.text)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
