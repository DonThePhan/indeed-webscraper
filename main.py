from bs4 import BeautifulSoup
from bs4.element import Comment

import cloudscraper
from time import sleep
import random

scraper = cloudscraper.create_scraper(browser='chrome')
indeed_url = 'https://ca.indeed.com/jobs?q=developer&l=downtown+toronto+ontario&fromage=1'


def mock_scrape(file_name):
    with open(file_name) as file:
        contents = file.read()
        soup = BeautifulSoup(contents, 'html.parser')
        return soup


def scrape(url):
    contents = scraper.get(url).text
    soup = BeautifulSoup(contents, 'html.parser')
    return soup


def find_links(url):
    # html = mock_scrape('staticBaseSearch.html').find(class_="jobsearch-ResultsList").find_all(recursive=False)
    html = scrape(url).find(class_="jobsearch-ResultsList").find_all(recursive=False)

    links_arr = []

    for li in html:
        if 'mosaic-zone' not in li.div['class']:
            links_arr.append('https://ca.indeed.com' + li.find('a')['href'])

    return links_arr


def scrape_individual_post(url):
    # html = mock_scrape('staticJobDescription.html')
    html = scrape(url)

    job_title = None
    company = None
    job_location = None

    try:
        job_title = html.find(class_='jobsearch-JobInfoHeader-title-container').get_text()
    except AttributeError:
        pass

    try:
        company = html.find(class_='jobsearch-JobInfoHeader-subtitle').a.get_text()
    except AttributeError:
        pass

    try:
        job_location = html.find(class_='jobsearch-JobInfoHeader-subtitle').find_all(recursive=False)[1].get_text()
    except AttributeError:
        pass

    if job_description_pass(html):
        return {'title': job_title, 'company': company, 'location': job_location, 'url': url}

    return False


def job_description_pass(html):
    dismiss_list = ['enrolled', '3-', '4-', '5-', '6-', '7-', '8-', '9-', '10-', '3 years', '4 years', '5 years',
                    '6 years', '7 years', '8 years', '9 years', '10 years', '3+', '4+', '5+', '6+', '7+', '8+', '9+',
                    '10+']

    html_text = text_from_html(html)
    if any(dismissible in html_text for dismissible in dismiss_list):
        return False

    return True


def text_from_html(html):
    texts = html.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def scan():
    links = find_links(indeed_url)
    valid_hits = []
    for link in links:
        result = scrape_individual_post(link)
        if result:
            print(result)
            valid_hits.append(result)
        else:
            print('dismissed')

        sleep(1 + random.uniform(0, 1))

    print(valid_hits)


# scan()
data = [{'title': 'Associate Developer (Entry Level): Toronto/Calgary/Ottawa', 'company': 'IBM', 'location': 'Toronto, ON', 'url': 'https://ca.indeed.com/rc/clk?jk=6c1456992f5618b4&fccid=de71a49b535e21cb&vjs=3'}, {'title': 'Full Stack Developer', 'company': 'Payfare Inc', 'location': 'Toronto, ON', 'url': 'https://ca.indeed.com/company/Payfare-Inc/jobs/Full-Stack-Developer-6e1bedb1aed05169?fccid=ed6e242a00daa6e1&vjs=3'}, {'title': 'Full Stack Developer', 'company': 'Interaptix', 'location': 'Toronto, ON', 'url': 'https://ca.indeed.com/rc/clk?jk=caa70d4c6ad6b57b&fccid=90690727895dfd26&vjs=3'}, {'title': 'Software Developer, Frontend', 'company': 'Hootsuite', 'location': 'Toronto, ON', 'url': 'https://ca.indeed.com/rc/clk?jk=dd630bec2ced9d3f&fccid=cc35cdc10c90c921&vjs=3'}, {'title': 'Software Developer in Test', 'company': 'Auvik Networks', 'location': 'Toronto, ON', 'url': 'https://ca.indeed.com/rc/clk?jk=3086788587de2e96&fccid=f21f075945cd8f21&vjs=3'}]

