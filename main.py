from bs4 import BeautifulSoup
import cloudscraper

scraper = cloudscraper.create_scraper(browser='chrome')
indeed_url = 'https://ca.indeed.com/jobs?q=developer&l=downtown+toronto+ontario&fromage=1'


def mock_scrape(unused_url):
    with open('staticBaseSearch.html') as file:
        contents = file.read()
        soup = BeautifulSoup(contents, 'html.parser')
        return soup


def scrape(url):
    contents = scraper.get(url).text
    soup = BeautifulSoup(contents, 'html.parser')
    return soup


def find_links(url):
    html = mock_scrape(url).find(class_="jobsearch-ResultsList").find_all(recursive=False)

    links_arr = []

    for li in html:
        if 'mosaic-zone' not in li.div['class']:
            links_arr.append(li.find('a')['href'])

    return links_arr


links = find_links(indeed_url)

print(scrape(f'https://ca.indeed.com{links[0]}'))
