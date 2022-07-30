from flaskr.scrape import parse_disruptions_page
from tests.scaffolding.page_1 import html_raw as page_1
from tests.scaffolding.last_page import html_raw as last_page


def test_page_1():
    page = parse_disruptions_page(page_1)

    assert page.next == "https://www.saskhealthauthority.ca/news-events/service-disruptions?search_api_fulltext=&page=2"
    assert len(page.disruptions) == 10

def test_last_page():
    page = parse_disruptions_page(last_page)
    assert page.next == None
    assert len(page.disruptions) == 6