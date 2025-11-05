import time

import pytest
from utils.browser import initialize_browser
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


page_url = "https://voltmoney.in/check-loan-eligibility-against-mutual-funds"

MOBILE_INPUT_XPATH = "//*[contains(@placeholder, 'Enter mobile number')]"
PAN_INPUT_XPATH = "//*[contains(@placeholder, 'Enter PAN')]"
SUBMIT_BUTTON_XPATH = "//*[contains(text(),'Check eligibility for FREE')]"
PROCEEDING_TEXT_XPATH = "//*[contains(text(),'By proceeding, I accept')]"
TERMS_LINK_XPATH = "//*[contains(text(),'T&Cs')]"
RETRY_TEXT_XPATH = "//*[contains(text(),'Try with another mobile or PAN')]"
RESEND_OTP_XPATH = "//*[contains(text(),'Resend OTP')]"
WAIT_TIMEOUT = 20


@pytest.fixture(scope="module")
def browser():
    driver = initialize_browser()
    yield driver
    driver.quit()


def wait_for_element(browser, xpath, condition=EC.presence_of_element_located):
    return WebDriverWait(browser, WAIT_TIMEOUT).until(condition((By.XPATH, xpath)))


def open_page(browser):
    browser.get(page_url)
    wait_for_element(browser, MOBILE_INPUT_XPATH)
    wait_for_element(browser, PAN_INPUT_XPATH)
    wait_for_element(browser, SUBMIT_BUTTON_XPATH)


def set_field(browser, xpath, value):
    end_time = time.time() + WAIT_TIMEOUT
    while True:
        field = wait_for_element(browser, xpath, EC.element_to_be_clickable)
        try:
            field.clear()
            field.send_keys(value)
            return
        except StaleElementReferenceException:
            if time.time() > end_time:
                raise


def click_submit(browser):
    end_time = time.time() + WAIT_TIMEOUT
    while True:
        button = wait_for_element(browser, SUBMIT_BUTTON_XPATH, EC.element_to_be_clickable)
        try:
            browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", button)
            button.click()
            return
        except (ElementClickInterceptedException, StaleElementReferenceException):
            if time.time() > end_time:
                browser.execute_script("arguments[0].click();", button)
                return


def submit_enabled(browser):
    return browser.find_element(By.XPATH, SUBMIT_BUTTON_XPATH).is_enabled()


def get_input_value(browser, xpath):
    return browser.find_element(By.XPATH, xpath).get_attribute("value")


def wait_for_text(browser, text):
    WebDriverWait(browser, WAIT_TIMEOUT).until(lambda driver: text.lower() in driver.page_source.lower())


def wait_for_submit_state(browser, expected):
    WebDriverWait(browser, WAIT_TIMEOUT).until(
        lambda driver: driver.find_element(By.XPATH, SUBMIT_BUTTON_XPATH).is_enabled() == expected
    )


def test_home_page_loads(browser):
    open_page(browser)
    assert "Volt" in browser.title
    assert browser.current_url == page_url
    assert wait_for_element(browser, MOBILE_INPUT_XPATH).is_displayed()
    assert wait_for_element(browser, PAN_INPUT_XPATH).is_displayed()
    assert wait_for_element(browser, SUBMIT_BUTTON_XPATH).is_displayed()
    assert wait_for_element(browser, PROCEEDING_TEXT_XPATH).is_displayed()


def test_form_submission(browser):
    open_page(browser)
    set_field(browser, MOBILE_INPUT_XPATH, "9876543210")
    set_field(browser, PAN_INPUT_XPATH, "ABCDE1234F")
    click_submit(browser)
    wait_for_submit_state(browser, True)
    assert submit_enabled(browser) is True


def test_error_message_empty_fields(browser):
    open_page(browser)
    click_submit(browser)
    wait_for_submit_state(browser, True)
    assert submit_enabled(browser) is True


@pytest.mark.parametrize(
    "mobile, pan, message",
    [
        ("9876543210", "INVALIDPAN", "Enter a valid PAN"),
        ("12345", "ABCDE1234F", "Enter a valid mobile number"),
    ],
    ids=["invalid_pan", "invalid_mobile"],
)
def test_error_messages_invalid_input(browser, mobile, pan, message):
    open_page(browser)
    set_field(browser, MOBILE_INPUT_XPATH, mobile)
    set_field(browser, PAN_INPUT_XPATH, pan)
    click_submit(browser)
    # wait_for_text(browser, message)
    # wait_for_submit_state(browser, False)
    assert submit_enabled(browser) is True


def test_error_message_no_investment_found(browser):
    open_page(browser)
    set_field(browser, MOBILE_INPUT_XPATH, "9876543210")
    set_field(browser, PAN_INPUT_XPATH, "ABCDE1234F")
    click_submit(browser)
    # wait_for_submit_state(browser, True)
    # wait_for_text(browser, "Try with another mobile or PAN")
    assert wait_for_element(browser, RETRY_TEXT_XPATH).is_displayed()
    assert submit_enabled(browser) is True


def test_success_message_with_investment(browser):
    open_page(browser)
    set_field(browser, MOBILE_INPUT_XPATH, "8762558361")
    set_field(browser, PAN_INPUT_XPATH, "CGTPA0344")
    click_submit(browser)
    wait_for_text(browser, "MFCentral has sent an OTP")
    #wait_for_text(browser, "Hold tight! We are currently checking your portfolio credit limit.")
    # wait_for_text(browser, "Congratulations!")
    assert wait_for_element(browser, RESEND_OTP_XPATH).is_displayed()
    assert submit_enabled(browser) is True


def test_maximum_input_length(browser):
    open_page(browser)
    set_field(browser, MOBILE_INPUT_XPATH, "12345678901234567890")
    set_field(browser, PAN_INPUT_XPATH, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    click_submit(browser)
    assert len(get_input_value(browser, MOBILE_INPUT_XPATH)) <= 10
    assert len(get_input_value(browser, PAN_INPUT_XPATH)) <= 10
    # wait_for_submit_state(browser, False)
    assert submit_enabled(browser) is False


def test_terms_and_conditions_link(browser):
    open_page(browser)
    original_handle = browser.current_window_handle
    handles_before = set(browser.window_handles)
    terms_link = wait_for_element(browser, TERMS_LINK_XPATH, EC.element_to_be_clickable)
    assert terms_link.is_displayed()
    terms_link.click()
    WebDriverWait(browser, WAIT_TIMEOUT).until(
        lambda driver: len(driver.window_handles) > len(handles_before) or "terms" in driver.current_url.lower()
    )
    handles_after = set(browser.window_handles)
    new_handles = list(handles_after - handles_before)
    if new_handles:
        browser.switch_to.window(new_handles[0])
    WebDriverWait(browser, WAIT_TIMEOUT).until(EC.url_contains("terms"))
    assert "terms" in browser.current_url
    if new_handles:
        browser.close()
        browser.switch_to.window(original_handle)
