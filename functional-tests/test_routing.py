import json

import pytest
from selenium.webdriver.support.ui import WebDriverWait

def test_title(sb, base_address):
    sb.get(base_address)
    sb.assert_title_contains('Textcavator')

def test_admin(sb, admin_address):
    sb.get(admin_address)
    sb.assert_title_contains('Django')


@pytest.fixture
def login(sb, login_address, credentials):
    sb.get(login_address)
    sb.assert_title_contains('Textcavator')
    sb.type('input[name="username"]', credentials[0])
    sb.type('input[name="password"]', credentials[1])
    sb.click('button.button.is-primary')
    wait = WebDriverWait(sb, 4)
    wait.until(lambda sb: sb.get_current_url() != login_address)


def test_login(sb, login):
    sb.assert_title_contains('Home')


def test_filter(sb, login, search_address, corpus):
    sb.get(search_address)
    sb.wait_for_element('div.navbar-brand')
    sb.assert_text('Search', 'h1.title')
    field_name = corpus['field_name']
    first_option = corpus['first_option']
    sb.click(f'#{field_name}')
    sb.click('li:first-child')
    wait = WebDriverWait(sb, 4)
    wait.until(lambda sb: sb.get_current_url() != search_address)
    assert sb.get_current_url() == search_address + f'?{field_name}={first_option}'


def test_visualization(sb, login, search_address):
    sb.get(search_address)
    sb.wait_for_element('div.navbar-brand')
    sb.click('#tab-visualizations')
    sb.click('.dropdown-trigger')
    sb.click('.dropdown-item:nth-child(2)')
    sb.wait_for_element('div.block')
    wait = WebDriverWait(sb, 4)
    wait.until(lambda sb: sb.get_current_url() != search_address)
    assert 'wordcloud' in sb.get_current_url()
    sb.refresh_page()
    sb.wait_for_element('div.block')
    assert 'wordcloud' in sb.get_current_url()


def test_word_models(sb, login, corpus, search_address, wordmodels_address):
    sb.get(search_address)
    try:
        sb.wait_for_element('.fa-diagram-project')
    except:
        pytest.skip('No word models found in this configuration, skipping')
    sb.get(wordmodels_address)
    sb.wait_for_element('h1.title')
    sb.assert_text('Word models', 'h1.title')
    query = corpus['query_term']
    sb.type('[name="query"]', query)
    sb.click('button.button')
    sb.wait_for_element('div#relatedwords')
    wm_query_url = sb.get_current_url()
    assert wm_query_url == wordmodels_address + f'?query={query}'
    sb.click('#tab-wordsimilarity')
    sb.wait_for_element('div#wordsimilarity')
    wait = WebDriverWait(sb, 4)
    wait.until(lambda sb: sb.get_current_url() != wm_query_url)
    assert sb.get_current_url() == wordmodels_address + f'?query={query}&show=wordsimilarity'
