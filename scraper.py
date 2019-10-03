def __open_url(url):
    from contextlib import closing
    from requests import get
    from requests.exceptions import RequestException

    try:
        with closing(get(url, stream=True)) as resp:
            if __is_valid_response(resp):
                return resp.content
            else:
                __log_error('invalid response received')
                return None
    except RequestException as e:
        __log_error(e)
        return None


def __is_valid_response(response):
    content_type = response.headers['Content-Type'].lower()

    return (response.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def __log_error(msg):
    print(msg)


def __soup(url):
    from bs4 import BeautifulSoup as bs

    return bs(__open_url(url), 'html.parser')


def __find_talk_pages(base_url):
    import re
    from urllib.parse import urljoin

    base_site = __soup(base_url)

    talk_pages = set()
    pages = set()

    # find all page-links which end in a digit
    for page in base_site.findAll('a', class_='page-link', href=re.compile('\d/$')):
        url = page.attrs['href']

        # keep track of pages we have already scraped
        if not url in pages:
            pages.add(url)

            page_data = __soup(urljoin(base_url, url))

            for talk in page_data.find_all('a', class_=False, href=re.compile('^/talks/')):
                talk_pages.add(urljoin(base_url, talk.attrs['href']))

    return talk_pages


def __extract_details_from_page(talk_url):
    talk_page = __soup(talk_url)
    talk_section = talk_page.find('section', class_='wafer-talk')
    info = {}

    info['title'] = talk_section.find('h1').text.strip()

    for text in talk_section.find('div').findChildren('p'):
        clean_text = text.text.replace('\n', '').strip()
        key, value = clean_text.split(':', 1)
        info[key.lower()] = value.strip()

    info['abstract'] = talk_section.find('div', id='abstract').text

    return info


def scrape_url(base_url):
    talks = [__extract_details_from_page(talk)
             for talk in __find_talk_pages(base_url)]

    return talks
