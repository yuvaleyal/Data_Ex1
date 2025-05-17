import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from pathlib import Path

BASE_URL = "https://www.worldometers.info/demographics/"
URL_PREFIX = "https://www.worldometers.info"
COLS = ["Life Expectancy Both", "Life Expectancy Female", "Life Expectancy Male", "Urban Population Percentage", "Urban Population Absolute", "Population Density"]
OUTPUT_FOLDER = "output"

def get_country_links() -> list[str]:
    """returns a list of country links from the demographics page.

    Returns:
        list[str]: List of country URLs.
    """
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    country_links = []
    # Find 'Demographics of Countries' section
    for h2 in soup.find_all('h2'):
        if 'Demographics of Countries' in h2.text:
            demographics_section = h2.find_next('ul')
    # Extract links
    for li in demographics_section.find_all('li'):
        a_tag = li.find('a')
        if a_tag and 'href' in a_tag.attrs:
            full_link = URL_PREFIX + a_tag['href']
            country_links.append(full_link)
    return country_links

def country_name(soup: BeautifulSoup) -> str:
    """returns the country name from the soup object.

    Args:
        soup (BeautifulSoup): soup object of the page.

    Returns:
        str: Country name.
    """
    name = soup.find('h1')
    if name:
        title = name.text.strip()
        return title.rsplit(' ', 1)[0] if title.lower().endswith('demographics') else title

def life_expectancy(soup: BeautifulSoup, population: str) -> float:
    """returns the life expectancy for a given population type (Male, Female or Both).

    Args:
        soup (BeautifulSoup): soup object of the page.
        population (str): indicator for the type of life expectancy.

    Returns:
        float: Life expectancy.
    """
    result = soup.find('div', string=re.compile(population, re.IGNORECASE))
    if result:
        parent = result.parent
        value = parent.find('div', class_=re.compile(r"text-2xl|font-bold"))
        if value:
            return float(value.get_text(strip=True))
    return None

def urban_stats(soup: BeautifulSoup) -> tuple[float, float]:
    """extracts and return the urban population percentage and absolute number.

    Args:
        soup (BeautifulSoup): soup object of the page.

    Returns:
        tuple[float, float]: [urban population percentage, urban population absolute number]
    """
    header = soup.find('h2', string=re.compile(r'Urban Population', re.IGNORECASE))
    if header:
        p = header.find_next_sibling('p')
        if p:
            tagged_strong = p.find('strong')
            urban_percent = tagged_strong.get_text(strip=True).strip('%') if tagged_strong else None
            abs_match = re.search(r"\(([\d,]+)\s*people", p.get_text(), re.IGNORECASE)
            urban_absolute = abs_match.group(1).replace(',', '') if abs_match else None
            return float(urban_percent), float(urban_absolute)
    return None, None

def population_density(soup: BeautifulSoup) -> float:
    """finds and returns the population density from the soup object.

    Args:
        soup (BeautifulSoup): soup object of the page.

    Returns:
        float: Population density.
    """
    header = soup.find('h2', string=re.compile(r'Population Density', re.IGNORECASE))
    if header:
        p = header.find_next_sibling('p')
        if p:
            m = re.search(r"(\d+)\s*people per\s*Km2", p.get_text(), re.IGNORECASE)
            if m:
                return float(m.group(1))
    return None

def crwal_page(url: str) -> dict:
    """crawls a single country page and returns the data in a dictionary.

    Args:
        url (str): url to the page.

    Returns:
        dict: the data extracted.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}
    data['Country'] = country_name(soup)
    data[COLS[0]] = life_expectancy(soup, r'life expectancy at birth, both sexes combined')
    data[COLS[1]] = life_expectancy(soup, r'life expectancy at birth, females')
    data[COLS[2]] = life_expectancy(soup, r'life expectancy at birth, males')
    urban_percent, urban_abs = urban_stats(soup)
    data[COLS[3]] = urban_percent
    data[COLS[4]] = urban_abs
    data[COLS[5]] = population_density(soup)
    return data
    
def crawl_all_countries() -> pd.DataFrame:
    """crawls all country pages and returns a DataFrame of the extracted data.

    Returns:
        pd.DataFrame: all the extracted data.
    """
    country_links = get_country_links()
    data = []
    for link in country_links:
        data.append(crwal_page(link))
    return pd.DataFrame(data, columns=['Country'] + COLS)

if __name__ == "__main__":
    data = crawl_all_countries()
    data.set_index('Country', inplace=True)
    data.to_csv(Path(__file__).parent.parent/OUTPUT_FOLDER/"demographics_data.csv", index=True)
    print(data.head(10))
    data.head(10).to_csv(Path(__file__).parent.parent/OUTPUT_FOLDER/"demographics_before_sort.csv", index=True)
    data.sort_index(inplace=True)
    print(data.head(10))
    data.head(10).to_csv(Path(__file__).parent.parent/OUTPUT_FOLDER/"demographics_after_sort.csv", index=True)