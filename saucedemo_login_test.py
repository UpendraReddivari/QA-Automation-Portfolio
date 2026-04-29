from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# =============================================
# SauceDemo — Login Test Suite
# Author: Upendra Reddivari
# Website: https://www.saucedemo.com
# Tools: Selenium WebDriver 4.x, Python 3.x
# =============================================

BASE_URL = "https://www.saucedemo.com"

def setup():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(5)
    return driver

def teardown(driver):
    time.sleep(1)
    driver.quit()

# -----------------------------------------------
# TC_001: Valid Login Test
# -----------------------------------------------
def test_valid_login():
    print("\n TC_001: Valid Login Test")
    driver = setup()
    try:
        driver.get(BASE_URL)
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()
        time.sleep(2)
        assert "inventory" in driver.current_url
        print("    PASSED — Valid login redirected to inventory page")
    except AssertionError:
        print("    FAILED — Inventory page not loaded")
    except Exception as e:
        print(f"    ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_002: Invalid Login Test
# -----------------------------------------------
def test_invalid_login():
    print("\n TC_002: Invalid Credentials Test")
    driver = setup()
    try:
        driver.get(BASE_URL)
        driver.find_element(By.ID, "user-name").send_keys("wrong_user")
        driver.find_element(By.ID, "password").send_keys("wrong_pass")
        driver.find_element(By.ID, "login-button").click()
        time.sleep(1)
        error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert error.is_displayed()
        print(f"    PASSED — Error shown: {error.text[:60]}")
    except AssertionError:
        print("    FAILED — No error message displayed")
    except Exception as e:
        print(f"    ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_003: Locked Out User Test
# -----------------------------------------------
def test_locked_out_user():
    print("\n TC_003: Locked Out User Test")
    driver = setup()
    try:
        driver.get(BASE_URL)
        driver.find_element(By.ID, "user-name").send_keys("locked_out_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()
        time.sleep(1)
        error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "locked out" in error.text.lower()
        print("    PASSED — Locked out user error displayed correctly")
    except AssertionError:
        print("    FAILED — Locked out message not shown")
    except Exception as e:
        print(f"    ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_004: Empty Username Test
# -----------------------------------------------
def test_empty_username():
    print("\n TC_004: Empty Username Validation Test")
    driver = setup()
    try:
        driver.get(BASE_URL)
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()
        time.sleep(1)
        error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Username is required" in error.text
        print("    PASSED — Username required validation working")
    except AssertionError:
        print("    FAILED — Username validation not triggered")
    except Exception as e:
        print(f"    ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_005: Empty Password Test
# -----------------------------------------------
def test_empty_password():
    print("\n TC_005: Empty Password Validation Test")
    driver = setup()
    try:
        driver.get(BASE_URL)
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "login-button").click()
        time.sleep(1)
        error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Password is required" in error.text
        print("    PASSED — Password required validation working")
    except AssertionError:
        print("    FAILED — Password validation not triggered")
    except Exception as e:
        print(f"    ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# Run All Tests
# -----------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  SauceDemo — Login Test Suite")
    print("  Author: Upendra Reddivari | QA Automation")
    print("=" * 55)
    test_valid_login()
    test_invalid_login()
    test_locked_out_user()
    test_empty_username()
    test_empty_password()
    print("\n" + "=" * 55)
    print("  Test Execution Complete")
    print("=" * 55)
