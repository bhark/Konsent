"""NOTE: In order for the tests to run firefox and geckodriver must be on $PATH."""

import pytest
from selenium.webdriver import Firefox


URL = 'http://127.0.0.1:5000/' 


@pytest.fixture
def browser():
    firefox = Firefox()
    yield firefox
    # firefox.quit()


def test_main(browser):
    browser.get(URL)

    assert 'Konsent' in browser.title

    # wrong login
    browser.get(URL)
    home_login_button = browser.find_element_by_css_selector('a.btn:nth-child(6)')
    home_login_button.click()

    assert browser.current_url.endswith('/login')

    user_field = browser.find_element_by_css_selector('div.form-group:nth-child(1) > input:nth-child(2)')
    pass_field = browser.find_element_by_css_selector('div.form-group:nth-child(2) > input:nth-child(2)')
    login_confirm_button = browser.find_element_by_css_selector('.btn')

    user_field.send_keys("WRONG_USER")
    pass_field.send_keys("SOME_PASSWORD")
    login_confirm_button.click()

    alert = browser.find_element_by_css_selector('.alert')
    assert 'This user doesnt exist' in alert.text

    # create new account missing fields
    browser.get(URL)
    home_new_account_button = browser.find_element_by_css_selector('.btn:nth-child(7)')
    home_new_account_button.click()

    assert browser.current_url.endswith('/register')

    new_account_submit_button = browser.find_element_by_css_selector('input.btn')
    new_account_submit_button.click()

    assert browser.current_url.endswith('/register')
    assert 'This field is required' in browser.page_source
