from bs4 import BeautifulSoup
from bs4.element import Comment

import cloudscraper
from time import sleep

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
            links_arr.append(li.find('a')['href'])

    return links_arr


# links = find_links(indeed_url)


# print(scrape(f'https://ca.indeed.com{links[0]}'))
def scrape_individual_post(url):
    html = mock_scrape('staticJobDescription.html')
    job_title = html.find(class_='jobsearch-JobInfoHeader-title-container').get_text()
    job_location = html.find(class_='jobsearch-JobInfoHeader-companyLocation').span.get_text()

    if job_description_pass(html):
        return {job_title, job_location, url}

    return False


def job_description_pass(html):
    dismiss_list = ['enrolled', '3-', '4-', '5-', '6-', '7-', '8-', '9-', '10-', '3 years', '4 years', '5 years',
                    '6 years', '7 years', '8 years', '9 years', '10 years', '3+', '4+', '5+', '6+', '7+', '8+', '9+', '10+']

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


print(scrape_individual_post('some url'))
