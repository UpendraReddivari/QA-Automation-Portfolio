from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

# =============================================
# SauceDemo — Sorting & Filter Test Suite
# Author: Upendra Reddivari
# Website: https://www.saucedemo.com
# Tools: Selenium WebDriver 4.x, Python 3.x
# =============================================

BASE_URL = "https://www.saucedemo.com"

def setup():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.get(BASE_URL)
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    time.sleep(2)
    return driver

def teardown(driver):
    time.sleep(1)
    driver.quit()

# -----------------------------------------------
# TC_011: Sort by Price Low to High
# -----------------------------------------------
def test_sort_price_low_to_high():
    print("\n🔵 TC_011: Sort Products — Price Low to High")
    driver = setup()
    try:
        sort = Select(driver.find_element(By.CLASS_NAME, "product_sort_container"))
        sort.select_by_value("lohi")
        time.sleep(1)

        prices = driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        price_values = [float(p.text.replace("$", "")) for p in prices]

        assert price_values == sorted(price_values)
        print(f"   ✅ PASSED — Prices sorted Low→High: {price_values}")
    except AssertionError:
        print("   ❌ FAILED — Prices not sorted correctly")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_012: Sort by Price High to Low
# -----------------------------------------------
def test_sort_price_high_to_low():
    print("\n🔵 TC_012: Sort Products — Price High to Low")
    driver = setup()
    try:
        sort = Select(driver.find_element(By.CLASS_NAME, "product_sort_container"))
        sort.select_by_value("hilo")
        time.sleep(1)

        prices = driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        price_values = [float(p.text.replace("$", "")) for p in prices]

        assert price_values == sorted(price_values, reverse=True)
        print(f"   ✅ PASSED — Prices sorted High→Low: {price_values}")
    except AssertionError:
        print("   ❌ FAILED — Prices not sorted correctly")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_013: Sort by Name A to Z
# -----------------------------------------------
def test_sort_name_az():
    print("\n🔵 TC_013: Sort Products — Name A to Z")
    driver = setup()
    try:
        sort = Select(driver.find_element(By.CLASS_NAME, "product_sort_container"))
        sort.select_by_value("az")
        time.sleep(1)

        names = driver.find_elements(By.CLASS_NAME, "inventory_item_name")
        name_values = [n.text for n in names]

        assert name_values == sorted(name_values)
        print(f"   ✅ PASSED — Products sorted A→Z correctly")
    except AssertionError:
        print("   ❌ FAILED — Products not sorted A→Z")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_014: Product Detail Page
# -----------------------------------------------
def test_product_detail_page():
    print("\n🔵 TC_014: Product Detail Page Test")
    driver = setup()
    try:
        first_product = driver.find_element(By.CLASS_NAME, "inventory_item_name")
        product_name = first_product.text
        first_product.click()
        time.sleep(1)

        detail_name = driver.find_element(By.CLASS_NAME, "inventory_details_name").text
        assert product_name == detail_name
        print(f"   ✅ PASSED — Product detail page loaded: '{product_name}'")
    except AssertionError:
        print("   ❌ FAILED — Product name mismatch on detail page")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_015: Logout Test
# -----------------------------------------------
def test_logout():
    print("\n🔵 TC_015: Logout Test")
    driver = setup()
    try:
        driver.find_element(By.ID, "react-burger-menu-btn").click()
        time.sleep(1)
        driver.find_element(By.ID, "logout_sidebar_link").click()
        time.sleep(1)
        assert driver.current_url == f"{BASE_URL}/"
        assert driver.find_element(By.ID, "login-button").is_displayed()
        print("   ✅ PASSED — Logout successful, redirected to login page")
    except AssertionError:
        print("   ❌ FAILED — Logout did not redirect to login")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# Run All Tests
# -----------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  SauceDemo — Sorting & Navigation Test Suite")
    print("  Author: Upendra Reddivari | QA Automation")
    print("=" * 55)
    test_sort_price_low_to_high()
    test_sort_price_high_to_low()
    test_sort_name_az()
    test_product_detail_page()
    test_logout()
    print("\n" + "=" * 55)
    print("  Test Execution Complete")
    print("=" * 55)
