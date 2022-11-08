from bs4 import BeautifulSoup
from bs4.element import Comment
import csv
from skills_list import skills_list

import cloudscraper
from time import sleep
import random

scraper = cloudscraper.create_scraper(browser='chrome')

INDEED_URL = 'https://ca.indeed.com/jobs?q=developer&l=downtown+toronto+ontario&fromage=1'
PAGES = 5
TITLE_DISMISS = ['sr', 'senior']
DESCRIPTION_DISMISS = ['enrolled', '3-', '4-', '5-', '6-', '7-', '8-', '9-', '10-', '3 years', '4 years', '5 years',
                       '6 years', '7 years', '8 years', '9 years', '10 years', '3+', '4+', '5+', '6+', '7+', '8+', '9+',
                       '10+', '11+', '12+', '13+', '14+', '15+']


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
    html = scrape(url).find(class_="jobsearch-ResultsList").find_all(recursive=False)

    links_arr = []

    for li in html:
        if 'mosaic-zone' not in li.div['class']:
            links_arr.append('https://ca.indeed.com' + li.find('a')['href'])

    return links_arr


# scrape and return only valid posts
def scrape_individual_post(url):
    print(f'Scraping {url}')

    job_title = None
    company = None
    job_location = None

    try:
        # html = mock_scrape('testJobDescription.html')
        html = scrape(url)
    except AttributeError:
        print("Scraping error - couldn't extract html")
        return False

    try:
        job_title = html.find(class_='jobsearch-JobInfoHeader-title-container').get_text()

        # check for red flags in job title
        for dismiss_word in TITLE_DISMISS:
            if dismiss_word in job_title.lower():
                return False
    except AttributeError:
        print("Scraping error - couldn't find job title")

    try:
        company = html.find(class_='jobsearch-JobInfoHeader-subtitle').a.get_text()
    except AttributeError:
        company = html.find(class_='jobsearch-CompanyInfoWithReview').find(
            class_='jobsearch-JobInfoHeader-companyName').get_text()
    except AttributeError:
        print("Scraping error - couldn't find company")

    try:
        job_location = html.find(class_='jobsearch-JobInfoHeader-subtitle').find_all(recursive=False)[1].get_text()
    except AttributeError:
        job_location = html.find(class_='jobsearch-CompanyInfoWithReview').find(
            class_='jobsearch-JobInfoHeader-companyLocation').get_text()
    except AttributeError:
        print("Scraping error - couldn't find job location")

    try:
        html_job_description = html.find(id='jobDescriptionText')
        html_job_description_text = text_from_html_lowercase(html_job_description)
    except AttributeError:
        print("Scraping error - couldn't find job description")

    if job_description_pass(html_job_description_text):
        skills = generate_skills(html_job_description_text)
        return {'title': job_title, 'company': company, 'location': job_location, 'url': url, 'skills': skills}

    return False


def check_word_valid(word, key, skills):
    if key not in word:
        return False

    # if key IS in word

    # if key is for a string (otherwise dict)
    if isinstance(skills_list[key], str):
        if skills_list[key] not in skills:
            return skills_list[key]

    # else we're working with a dictionary -> check if our word is just part of a larger word i.e 'unity' in 'community'
    else:
        skill = skills_list[key]['word']

        # check if it's already in the list
        if skill in skills:
            return False

        # check if it's a wrong word
        not_arr = skills_list[key]['not']
        for not_word in not_arr:
            if word in not_word:
                return False

        return skill

    return False


def generate_skills(html_job_description_text):
    skills = []

    job_description_arr = html_job_description_text.lower().split(' ')
    for word in job_description_arr:
        for key in skills_list:
            valid_word = check_word_valid(word, key, skills)
            if valid_word:
                skills.append(valid_word)

    skills_string = ''
    for skill in skills:
        skills_string += skill + '\n'

    skills_string = skills_string[:-1]

    return skills_string


def job_description_pass(html_job_description_text):
    if any(dismissible in html_job_description_text for dismissible in DESCRIPTION_DISMISS):
        return False

    return True


def text_from_html_lowercase(html):
    texts = html.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts).lower()


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def scan():
    valid_hits = []

    for page in range(PAGES):
        links = find_links(f'{INDEED_URL}&start={page * 10}')
        for i in range(len(links)):
            try:
                result = scrape_individual_post(links[i])
                if result:
                    # if we start getting repeats, finish (probably hit the last page)
                    if any(hit['url'] == result['url'] for hit in valid_hits):
                        return valid_hits

                    valid_hits.append(result)
                else:
                    pass
            except AttributeError:
                print(f'scrape unsuccessful for link {i} of {len(links)}:')
                print(links[i])
                return valid_hits  # if any issues, just end search

            finally:
                sleep(1 + random.uniform(0, 1))

    return valid_hits


def write_to_csv(data):
    # write all postings to cvs, so I can copy and paste into my job log
    with open('postings.csv', 'w') as csvfile:
        fieldnames = ['company', 'title', 'url', 'location', 'skills']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for entry in data:
            writer.writerow({'company': entry['company'], 'title': entry['title'], 'url': entry['url'],
                             'location': entry['location'], 'skills': entry['skills']})


def run():
    data = scan()
    write_to_csv(data)


run()
# print(scrape_individual_post('asdf'))
