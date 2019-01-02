"""Extension of functions for the API."""

import re

import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
from .constants import BASE_URL


def get_articles(soup):
    """"Scrape the articles per page."""
    articles = []
    available_pages = None

    # A hacky way to get the page count.
    for ul_pagination in soup.find_all('ul', attrs={'id': 'pagination'}):
        if ul_pagination.find('li', attrs={'class': 'next'}):
            available_pages = len(
                ul_pagination.find_all('li', recursive=False)) - 2
        else:
            # For archived pages.
            available_pages = len(
                ul_pagination.find_all('li', recursive=False)) - 1

    for i, td_article in enumerate(soup.find_all('td', attrs={'valign': 'top'})):
        article_title = None
        article_url = None
        article_thumbnail_url = None
        article_body = None
        article_media = None

        # h3 for "index<num>.html" pages.
        article_title = td_article.find_all(
            ['h2', 'h3'])[0].get_text()

        for div_article in td_article.find_all('div'):
            article_text = div_article.get_text()
            article_body = re.sub(r'\bmore\b\.{1,3}', '', article_text)

            for a_article in div_article.find_all('a', recursive=False):
                article_url = a_article.attrs['href']

            for img_article in div_article.find_all('img', recursive=False):
                thumbnail_uri = img_article.attrs['src']
                if thumbnail_uri: article_thumbnail_url = urljoin(BASE_URL, thumbnail_uri)

            # For videos (`article_url` is replaced).
            for iframe_article in div_article.find_all('iframe', recursive=False):
                article_url = iframe_article.attrs['src']

            article = {
                'index': i,
                'title': article_title.strip(),
                'url': article_url,
                'thumbnail-url': article_thumbnail_url,
                'body': article_body.strip(),
            }

            articles.append(article)

    return available_pages, articles


def get_archives_list(soup):
    """"Scrape the archives list in the side bar."""
    archives_list = []

    for li_archive_year in soup.find_all('li'):
        try:
            # idk why this is needed.
            archive_year = li_archive_year.find(
                'a', attrs={'class': 'links'}).get_text(strip=True)
        except AttributeError:
            archive_year = None

        months = []

        for li_archive_month in li_archive_year.find_all('li'):
            archive_month = li_archive_month.find('a').get_text(strip=True)
            archive_month_uri = li_archive_month.find('a')['href']

            month = {
                'month': archive_month,
                'month-uri': archive_month_uri
            }

            months.append(month)

        years = {
            'year': str(archive_year),
            'months': months
        }

        # Fix, or find better method.
        if months:
            archives_list.append(years)

    return archives_list


def get_links_list(tr_tag):
    """"Scrape the link indexes in the side bar."""
    links_list = []

    for a_links in tr_tag.find_all('a', attrs={'class': 'links'}):
        link_text = a_links.get_text(strip=True)
        link_href = a_links['href']

        link = {
            'link-text': link_text,
            'link-href': link_href
        }

        links_list.append(link)

    return links_list


def fetch_articles(base_url, page):
    """Fetch articles from a particular page."""
    if page > 0:
        page += 1
        url = '{0}index{1}.html'.format(base_url, page)
    else:
        url = '{0}index.html'.format(base_url)

    response = requests.get(url, stream=False)

    remote_status_code = response.status_code

    if remote_status_code == requests.codes.ok:
        strainer = SoupStrainer(
            'table', attrs={'cellpadding': 1, 'cellspacing': 0})

        soup = BeautifulSoup(
            response.content, 'lxml', parse_only=strainer)

        available_pages, articles = get_articles(soup)
    else:
        available_pages = None
        articles = None

    return url, remote_status_code, available_pages, articles


def fetch_archives(year, month, page):
    """Generate archive url and feed it to 'fetch_articles()'."""

    months_list = {
        'january': 'jan',
        'february': 'feb',
        'march': 'mar',
        'april': 'apr',
        'may': 'may',
        'june': 'june',
        'july': 'july',
        'august': 'aug',
        'september': 'sep',
        'october': 'oct',
        'november': 'nov',
        'december': 'dec',
    }

    month = month.lower()

    if month in months_list.values():
        url = '%s%s/%s/' % (BASE_URL, year, month)
    else:
        url = '%s%s/%s/' % (BASE_URL, year, months_list.get(month))

    archives = fetch_articles(url, page)

    return archives


def fetch_archives_list():
    """Fetch archives list."""

    response = requests.get(BASE_URL, stream=False)

    remote_status_code = response.status_code

    if remote_status_code == requests.codes.ok:
        strainer = SoupStrainer('ul', attrs={'id': 'navmenu'})

        soup = BeautifulSoup(
            response.content, 'lxml', parse_only=strainer)

        archives_list = get_archives_list(soup)
    else:
        archives_list = None

    return BASE_URL, remote_status_code, archives_list


def fetch_link_lists(list_type):
    """
    Fetch links according to the list type.
    'tr_tag_list' matches the <tr> position according to the 'list_type'.
    """

    tr_tag_list = {
        'news-paper': 2,
        'news-site': 4,
        'radio': 6,
        'tv': 8,
        'video': 10
    }

    list_type = list_type.lower()

    response = requests.get(BASE_URL, stream=False)

    remote_status_code = response.status_code

    if remote_status_code == requests.codes.ok:
        if list_type in tr_tag_list.keys():
            strainer = SoupStrainer(
                'table', attrs={'width': 120, 'border': 0, 'cellpadding': 0, 'cellspacing': 0})

            soup = BeautifulSoup(
                response.content, 'lxml', parse_only=strainer)

            tr_tag = soup.find_all('tr')[tr_tag_list.get(list_type)]

            link_list = get_links_list(tr_tag)
        else:
            link_list = None
    else:
        link_list = None

    return BASE_URL, remote_status_code, link_list
