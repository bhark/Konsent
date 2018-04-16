"""
Intergration tests for Konsent
the tests must run in order, they are NOT independent from each other.

NOTE: In order for the tests to run firefox and geckodriver must be on $PATH.
"""
import random


import pytest
from selenium import webdriver


URL = 'http://127.0.0.1:5000/'

def rand():
    return str(random.random())[2:]

_suffix = rand()
TEST_USERNAME = 'test_username_' + _suffix
TEST_PASSWORD = 'test_passw0rD_' + _suffix
TEST_UNION_NAME = 'test_union_name_' + _suffix
TEST_UNION_PASSWORD = 'test_union_password_' + _suffix

# CSS selectors
HOME_LOGIN_BUTTON = 'a.btn:nth-child(6)'
HOME_NEW_ACCOUNT_BUTTON = 'a.btn:nth-child(7)'
LOGIN_USER_FIELD = 'input[name="username"]'
LOGIN_PASS_FIELD = 'input[name="password"]'
LOGIN_CONFIG_BUTTON = '.form-submit'
ALERT = '.alert'
TOP_NEW_ACCOUNT = 'li.nav-item:nth-child(1) > a:nth-child(1)'
REGISTER_SUBMIT_BUTTON = '.form-submit'
REGISTER_CREATE_NEW_UNION_BUTTON = 'a.btn'
REGISTER_USERNAME = '#username'
REGISTER_PASSWORD = '#password'
REGISTER_CONFIRM_PASSWORD = '#confirm'
REGISTER_UNION = '#users_union'
REGISTER_UNION_PASSWORD = '#union_password'
UNION_REGISTER_NAME = '#union_name'
UNION_REGISTER_PASSWORD = '#password'
UNION_REGISTER_PASSWORD_CONFIRM = '#confirm'
UNION_REGISTER_SUBMIT_BUTTON = '.btn'
NAVLINK_LOGIN = '#navlink-login'

# after login
HOME_NEW_ISSUE_BUTTON = '.btn'
NEW_ISSUE_TITLE_FIELD = '#title'
NEW_ISSUE_BODY_FIELD = '#editor'
NEW_ISSUE_SUBMIT_BUTTON = '.btn'


# phase 1
PHASE1_VOTEUP = '.btn'
PHASE1_ISSUE = '.list-group-item > a:nth-child(2)'
NAVLINK_PHASE2 = '#navlink-phase2'
TOP_SOLUTION_PROPOSAL_BUTTON = 'ul.navbar-nav:nth-child(1) > li:nth-child(2) > a:nth-child(1)'

# phase 2
PHASE2_ISSUE = '.list-group-item > a:nth-child(1)'
ADD_URL_FIELD = '#url'
ADD_URL_BUTTON = '#submit_url'
ADD_PROPOSAL_FIELD = '#body'
ADD_PROPOSAL_BUTTON = '#submit_comment'
FIRST_URL = '#discussions > a'
FIRST_PROPOSAL_BODY = '#proposals > li.body'
FIRST_PROPOSAL_VOTE_UP = '.vote-up'
FIRST_PROPOSAL_CANCEL_VOTE = '.cancel-vote'

@pytest.fixture(scope='module')
def browser():
    firefox = webdriver.Firefox()
    firefox.implicitly_wait(20)
    yield firefox
    # firefox.quit()


def test_user_story_account(browser):
    find = browser.find_element_by_css_selector

    # user enters the url on the browser
    browser.get(URL)

    assert 'Konsent' in browser.title

    # she clicks the login button
    find(HOME_LOGIN_BUTTON).click()

    # she tries to login with wrong credentials
    find(LOGIN_USER_FIELD).send_keys("WRONG_USER")
    find(LOGIN_PASS_FIELD).send_keys("SOME_PASSWORD")
    find(LOGIN_CONFIG_BUTTON).click()

    # an alert popups with an error message
    assert 'This user doesnt exist' in find(ALERT).text

    # she clicks a button for creating a new account on top bar
    find(TOP_NEW_ACCOUNT).click()

    # she creates a new union
    find(REGISTER_CREATE_NEW_UNION_BUTTON).click()

    # she fills the required field and sumbits
    find(UNION_REGISTER_NAME).send_keys(TEST_UNION_NAME)
    find(UNION_REGISTER_PASSWORD).send_keys(TEST_UNION_PASSWORD)
    find(UNION_REGISTER_PASSWORD_CONFIRM).send_keys(TEST_UNION_PASSWORD)
    find(UNION_REGISTER_SUBMIT_BUTTON).click()
    assert "Your union is now registered" in find(ALERT).text

    # she goes back to register a new account
    find(HOME_NEW_ACCOUNT_BUTTON).click()
    # she fills the required fields
    find(REGISTER_USERNAME).send_keys(TEST_USERNAME)
    find(REGISTER_PASSWORD).send_keys(TEST_PASSWORD)
    find(REGISTER_CONFIRM_PASSWORD).send_keys(TEST_PASSWORD)
    # she selects her new union
    options = find(REGISTER_UNION).find_elements_by_tag_name('option')
    test_union_option = next(opt for opt in options
                             if opt.get_property('value') == TEST_UNION_NAME)
    test_union_option.click()
    find(REGISTER_UNION_PASSWORD).send_keys(TEST_UNION_PASSWORD)
    # she sumbits the information
    find(REGISTER_SUBMIT_BUTTON).click()
    assert 'and can now log in' in find(ALERT).text

    # she logins with the correct credentials
    find(NAVLINK_LOGIN).click()
    find(LOGIN_USER_FIELD).send_keys(TEST_USERNAME)
    find(LOGIN_PASS_FIELD).send_keys(TEST_PASSWORD)
    find(LOGIN_CONFIG_BUTTON).click()
    assert 'Youve been logged in' in find(ALERT).text


def test_user_story_issue(browser):
    find = browser.find_element_by_css_selector

    ## PHASE 1

    # user starts a new issue
    find(HOME_NEW_ISSUE_BUTTON).click()

    # she fills the required fields
    find(NEW_ISSUE_TITLE_FIELD).send_keys('New test issue')
    find(NEW_ISSUE_BODY_FIELD).send_keys(
        'This is a test issue that was created for the purpose of testing, obviously')
    # she submits the issue
    find(NEW_ISSUE_SUBMIT_BUTTON).click()
    assert 'Your post have been published' in find(ALERT).text

    # she chooses her issue
    find(PHASE1_ISSUE).click()

    # she votes for the issue
    find(PHASE1_VOTEUP).click()

    ## PHASE 2

    # she goes on to phase 2
    find(NAVLINK_PHASE2).click()

    # she chooses her issue
    find(PHASE2_ISSUE).click()

    # she adds a link to external discussion
    find(ADD_URL_FIELD).send_keys('https://raddle.me')
    find(ADD_URL_BUTTON).click()

    # she adds a proposal
    find(ADD_PROPOSAL_FIELD).send_keys('This is a test proposal, BEEP BOOP')
    find(ADD_PROPOSAL_BUTTON).click()

    # she makes sure that her URL and proposal was added
    assert 'https://raddle.me' in find(FIRST_URL).text
    assert 'This is a test proposal, BEEP BOOP' in find(FIRST_PROPOSAL_BODY).text

    # she votes for her proposal, because it's just that good
    find(FIRST_PROPOSAL_VOTE_UP).click()

    # she realizes it's not that good, and cancels her vote
    find(FIRST_PROPOSAL_CANCEL_VOTE).click()
