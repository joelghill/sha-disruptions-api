import requests
from datetime import datetime
from typing import Any, List
from bs4 import BeautifulSoup
from flaskr.sha import ServiceDisruption, ServiceDisruptionsPage


BASE_URL = "https://www.saskhealthauthority.ca"
DISRUPTIONS_URL = "news-events/service-disruptions"


def __clean_text(html_text: str):
    """ Cleans extra whitespace from element
    """
    return " ".join(html_text.split())


def __parse_disruption(disruption) -> ServiceDisruption:
    """ Helper function to parse the HTML of a single disruption listing

    Args:
        disruption (beautiful soup): A disruption element as found with beautiful soup
        base_url (str): The base URL of links

    Returns:
        ServiceDisruption: A service disruption DTO
    """

    ## Title
    title = ''
    title_elem = disruption.find(class_="c-teaser__title")

    if title_elem:
        relative_link = title_elem.a.attrs.get("href")
        link = f"{BASE_URL}{relative_link}"
        title_text: str = title_elem.a.span.string

        if title_text:
            title = __clean_text(title_text)

    ## Start and End Times
    times = disruption.find_all("time")

    start_text = ""
    end_text = ""

    if times:
        start_text = times[0].attrs.get("datetime")
    if len(times) == 2:
        end_text = times[1].attrs.get("datetime")

    # Format 2022-04-02T01:01:00Z
    start = (
        datetime.strptime(start_text, "%Y-%m-%dT%H:%M:%SZ") if start_text else None
    )
    end = datetime.strptime(end_text, "%Y-%m-%dT%H:%M:%SZ") if end_text else None

    # Community information
    tags = disruption.find(class_="c-teaser__tags").find_all(class_="c-tag")

    if len(tags) == 3:
        facility = __clean_text(tags[0].string)
        disruption_type = __clean_text(tags[1].string)
        community = __clean_text(tags[2].string)
        region = None
    elif len(tags) == 4:
        facility = __clean_text(tags[0].string)
        disruption_type = __clean_text(tags[1].string)
        region = __clean_text(tags[2].string)
        community = __clean_text(tags[3].string)

    # Build object
    return ServiceDisruption(
        start_date=start.isoformat() if start else None,
        end_date=end.isoformat() if end else None,
        title=title,
        link=link,
        facility_name=facility,
        community_name=community,
        region_name=region,
        disruption=disruption_type,
    )
    

def parse_disruptions_page(page: Any) -> ServiceDisruptionsPage:
    """ Parses a single page of HTML into a service disruptions page object

    Args:
        base_url (str): Base URL for all links scraped in page
        page (Any): The raw page HTML

    Returns:
        ServiceDisruptionsPage: An object representing a page of disruptions 
    """

    soup = BeautifulSoup(page, "html.parser")
    disruptions_raw = soup.find_all(class_="c-teaser__content")
    disruptions: List[ServiceDisruption] = []

    for disruption in disruptions_raw:

        # Build object
        disruptions.append(__parse_disruption(disruption=disruption))

    # Get next page link
    next_elem = soup.find(class_="c-pagination__item c-pagination__item--next")

    if next_elem:
        relative_next_link = next_elem.a.attrs.get("href")
        if relative_next_link:
            next_link = f"{BASE_URL}/{DISRUPTIONS_URL}{relative_next_link}"
    else:
        next_link = None

    return ServiceDisruptionsPage(disruptions=disruptions, next=next_link)


def get_all_disruptions(url):

    # Parse first page
    response = requests.get(url)
    current_page = parse_disruptions_page(response.content)
    disruptions = current_page.disruptions

    # Parse the rest while there are more
    while current_page.next:
        response = requests.get(current_page.next)
        current_page = parse_disruptions_page(response.content)
        disruptions.extend(current_page.disruptions)

    # Return all of them
    return disruptions