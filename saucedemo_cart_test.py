from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# =============================================
# SauceDemo — Shopping Cart Test Suite
# Author: Upendra Reddivari
# Website: https://www.saucedemo.com
# Tools: Selenium WebDriver 4.x, Python 3.x
# =============================================

BASE_URL = "https://www.saucedemo.com"

def setup():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(5)
    # Login before each test
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
# TC_006: Inventory Page Load Test
# -----------------------------------------------
def test_inventory_page_loaded():
    print("\n🔵 TC_006: Inventory Page Load Test")
    driver = setup()
    try:
        assert "inventory" in driver.current_url
        products = driver.find_elements(By.CLASS_NAME, "inventory_item")
        assert len(products) > 0
        print(f"   ✅ PASSED — Inventory loaded with {len(products)} products")
    except AssertionError:
        print("   ❌ FAILED — Inventory page not loaded properly")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_007: Add Product to Cart
# -----------------------------------------------
def test_add_to_cart():
    print("\n🔵 TC_007: Add Product to Cart Test")
    driver = setup()
    try:
        # Add first product to cart
        driver.find_element(By.CSS_SELECTOR, ".inventory_item button").click()
        time.sleep(1)
        cart_count = driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
        assert cart_count == "1"
        print(f"   ✅ PASSED — Product added, cart count: {cart_count}")
    except AssertionError:
        print("   ❌ FAILED — Cart count not updated")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_008: Remove Product from Cart
# -----------------------------------------------
def test_remove_from_cart():
    print("\n🔵 TC_008: Remove Product from Cart Test")
    driver = setup()
    try:
        # Add then remove
        driver.find_element(By.CSS_SELECTOR, ".inventory_item button").click()
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".inventory_item button").click()
        time.sleep(1)
        badges = driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        assert len(badges) == 0
        print("   ✅ PASSED — Product removed, cart is empty")
    except AssertionError:
        print("   ❌ FAILED — Cart badge still visible after removal")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_009: Navigate to Cart Page
# -----------------------------------------------
def test_navigate_to_cart():
    print("\n🔵 TC_009: Navigate to Cart Page Test")
    driver = setup()
    try:
        driver.find_element(By.CSS_SELECTOR, ".inventory_item button").click()
        time.sleep(1)
        driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        time.sleep(1)
        assert "cart" in driver.current_url
        cart_items = driver.find_elements(By.CLASS_NAME, "cart_item")
        assert len(cart_items) > 0
        print(f"   ✅ PASSED — Cart page loaded with {len(cart_items)} item(s)")
    except AssertionError:
        print("   ❌ FAILED — Cart page not loaded")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# TC_010: Complete Checkout Flow (E2E)
# -----------------------------------------------
def test_checkout_flow():
    print("\n🔵 TC_010: End-to-End Checkout Flow Test")
    driver = setup()
    try:
        # Add product
        driver.find_element(By.CSS_SELECTOR, ".inventory_item button").click()
        time.sleep(1)

        # Go to cart
        driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        time.sleep(1)

        # Checkout
        driver.find_element(By.ID, "checkout").click()
        time.sleep(1)

        # Fill checkout info
        driver.find_element(By.ID, "first-name").send_keys("Upendra")
        driver.find_element(By.ID, "last-name").send_keys("Reddivari")
        driver.find_element(By.ID, "postal-code").send_keys("517247")
        driver.find_element(By.ID, "continue").click()
        time.sleep(1)

        # Finish order
        driver.find_element(By.ID, "finish").click()
        time.sleep(2)

        # Verify order confirmation
        confirmation = driver.find_element(By.CLASS_NAME, "complete-header")
        assert "Thank you" in confirmation.text
        print(f"   ✅ PASSED — E2E checkout complete: '{confirmation.text}'")

    except AssertionError:
        print("   ❌ FAILED — Checkout flow not completed")
    except Exception as e:
        print(f"   ❌ ERROR — {e}")
    finally:
        teardown(driver)

# -----------------------------------------------
# Run All Tests
# -----------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  SauceDemo — Shopping Cart Test Suite")
    print("  Author: Upendra Reddivari | QA Automation")
    print("=" * 55)
    test_inventory_page_loaded()
    test_add_to_cart()
    test_remove_from_cart()
    test_navigate_to_cart()
    test_checkout_flow()
    print("\n" + "=" * 55)
    print("  Test Execution Complete")
    print("=" * 55)
