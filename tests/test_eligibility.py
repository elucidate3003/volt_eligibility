import pytest
from utils.browser import initialize_browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


page_url = "https://voltmoney.in/check-loan-eligibility-against-mutual-funds"

@pytest.fixture(scope="module")
def browser():
    driver = initialize_browser()
    yield driver
    driver.quit()

def test_home_page_loads(browser):
    try:
        browser.get(page_url)
        assert "Volt" in browser.title  
        assert browser.current_url == page_url
        assert browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter mobile number')]").is_displayed()
        assert browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter PAN')]").is_displayed()
        assert browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]").is_displayed()
        assert browser.find_element(By.XPATH, "//*[contains(text(),'By proceeding, I accept')]").is_displayed()
    except Exception as e:
        pytest.fail(f"Home page did not load correctly: {e}")

def test_form_submission(browser):
    try:
        browser.get(page_url)
        mobile_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter mobile number')]")
        pan_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter PAN')]")
        submit_button = browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]")

        mobile_input.send_keys("9876543210")
        pan_input.send_keys("ABCDE1234F")
        submit_button.click()
        
        assert submit_button.is_enabled() == True
    except Exception as e:
        pytest.fail(f"Form submission failed: {e}")
def test_error_message_empty_fields(browser):
    try:
        browser.get(page_url)
        submit_button = browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]")
        submit_button.click()
    except Exception as e:
        pytest.fail(f"Error message for empty fields not displayed: {e}")
    
    assert submit_button.is_enabled() == True
    
def test_error_message_invalid_pan(browser):
    try:
        browser.get(page_url)
        mobile_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter mobile number')]")
        pan_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter PAN')]")
        submit_button = browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]")

        mobile_input.send_keys("9876543210")
        pan_input.send_keys("INVALIDPAN")
        submit_button.click()
        
        wait = WebDriverWait(browser, 10)
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(translate(text(), '9876543210', 'INVALIDPAN'), 'valid pan')]",
                )
            )
        )
        wait.until(lambda _: submit_button.is_enabled() is False)
        assert submit_button.is_enabled() == False
    except Exception as e:
        pytest.fail(f"Error message for invalid PAN not displayed: {e}")
def test_error_message_invalid_mobile(browser):
    try:
        browser.get(page_url)
        mobile_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter mobile number')]")
        pan_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter PAN')]")
        submit_button = browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]")
        
        mobile_input.send_keys("12345")
        pan_input.send_keys("ABCDE1234F")
        submit_button.click()

        wait = WebDriverWait(browser, 10)
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(translate(text(), '1234', 'ABCDE0312K'), 'valid mobile number')]",
                )
            )
        )
        wait.until(lambda _: submit_button.is_enabled() is False)
        assert submit_button.is_enabled() == False
    except Exception as e:
        pytest.fail(f"Error message for invalid mobile number not displayed: {e}")



def test_error_message_no_investment_found(browser):
    try:
        browser.get(page_url)
        mobile_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter mobile number')]")
        pan_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter PAN')]")
        submit_button = browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]")
        
        mobile_input.send_keys("9876543210")
        pan_input.send_keys("ABCDE1234F")
        submit_button.click()
        #assert "No investment found" in browser.page_source
        assert submit_button.is_enabled() == True
        assert browser.find_element(By.XPATH, "//*[contains(text(),'Try with another mobile or PAN')]") is not None
    except Exception as e:
        pytest.fail(f"Error message for no investment found not displayed: {e}")

def test_success_message_with_investment(browser):
    try:
        browser.get(page_url)
        mobile_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter mobile number')]")
        pan_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter PAN')]")
        submit_button = browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]")
        
        mobile_input.send_keys("8762558361")
        pan_input.send_keys("CGTPA0344J")
        submit_button.click()
        assert "MFCentral has sent an OTP" in browser.page_source
        assert submit_button.is_enabled() == True
        assert "Hold tight! We are currently checking your portfolio credit limit." in browser.page_source
        assert browser.find_element(By.XPATH, "//*[contains(text(),'Resend OTP')]") is not None
        assert "Congratulations!" in browser.page_source
    except Exception as e:
        pytest.fail(f"Success message with investment not displayed: {e}")
    
def test_maximum_input_length(browser):
    try:
        browser.get(page_url)
        mobile_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter mobile number')]")
        pan_input = browser.find_element(By.XPATH, "//*[contains(@placeholder, 'Enter PAN')]")
        submit_button = browser.find_element(By.XPATH, "//*[contains(text(),'Check eligibility for FREE')]")
        
        mobile_input.send_keys("12345678901234567890")
        pan_input.send_keys("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        submit_button.click()
        assert len(mobile_input.text) <= 10
        assert len(pan_input.text) <= 10
        assert submit_button.is_enabled() == False
    except Exception as e:
        pytest.fail(f"Maximum input length not enforced: {e}")
def test_terms_and_conditions_link(browser):
    try:
        browser.get(page_url)
        terms_link = browser.find_element(By.XPATH, "//*[contains(text(),'T&Cs')]")
        assert terms_link.is_displayed()
        terms_link.click()
        assert "terms" in browser.current_url
    except Exception as e:
        pytest.fail(f"Terms and conditions link not working: {e}")


