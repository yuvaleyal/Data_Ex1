import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Base URL for the demographics overview
BASE_URL = "https://www.worldometers.info/demographics/"
OUTPUT_DIR = "output"


def get_country_links():
    """
    Crawl the main demographics page and extract all country links
    by selecting anchors with a data-country attribute and href under /demographics/.
    """
    resp = requests.get(BASE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Select all <a> tags that have data-country attribute and href to demographics pages
    anchors = soup.select('a[data-country][href]')
    links = []
    for a in anchors:
        href = a['href']
        if href.startswith('/demographics/') and 'demographics' in href:
            full_url = urljoin(BASE_URL, href)
            links.append(full_url)

    # Remove duplicates while preserving order
    unique_links = list(dict.fromkeys(links))
    if not unique_links:
        raise RuntimeError("No country links found matching the demographics URL pattern")
    return unique_links


def extract_country_data(url):
    """
    Given a country demographics URL, extract:
      - Country name
      - Life Expectancy (Both Sexes, Females, Males)
      - Urban Population (%) and absolute numbers
      - Population Density (per sq. km)
    Missing values are recorded as None.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    data = {}

    # Country name from the main <h1>
    country_name = soup.find('h1')
    if country_name:
        title = country_name.text.strip()
        data['Country'] = title.rsplit(' ', 1)[0] if title.lower().endswith('demographics') else title
    else:
        raise ValueError("Could not find country name in the page")

    ################### Helper functions #########################
    # Helper to find the life expectancy values
    def find_value(desc_pattern):
        desc_div = soup.find('div', string=re.compile(desc_pattern, re.IGNORECASE))
        if desc_div:
            parent = desc_div.parent
            val_div = parent.find('div', class_=re.compile(r"text-2xl|font-bold"))
            if val_div:
                return val_div.get_text(strip=True)
        return None

    # Helper to find urban population stats
    def find_urban_stats():
        header = soup.find('h2', string=re.compile(r'Urban Population', re.IGNORECASE))
        if header:
            p = header.find_next_sibling('p')
            if p:
                strong_tag = p.find('strong')
                perc = strong_tag.get_text(strip=True).strip('%') if strong_tag else None
                abs_match = re.search(r"\(([\d,]+)\s*people", p.get_text(), re.IGNORECASE)
                absn = abs_match.group(1).replace(',', '') if abs_match else None
                return perc, absn
        return None, None

    # Helper to find population density
    def find_population_density():
        header = soup.find('h2', string=re.compile(r'Population Density', re.IGNORECASE))
        if header:
            p = header.find_next_sibling('p')
            if p:
                m = re.search(r"(\d+)\s*people per\s*Km2", p.get_text(), re.IGNORECASE)
                if m:
                    return m.group(1)
        return None

    ################### Extracting the data ######################
    data['LifeExpectancy_Both']   = find_value(r'life expectancy at birth, both sexes combined')
    data['LifeExpectancy_Female'] = find_value(r'life expectancy at birth, females')
    data['LifeExpectancy_Male']   = find_value(r'life expectancy at birth, males')

    data['UrbanPopulation_Percentage'], data['UrbanPopulation_Absolute'] = find_urban_stats()

    data['PopulationDensity'] = find_population_density()

    return data


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Collect country links
    country_links = get_country_links()

    # 2. Extract data for each country
    records = []
    for link in country_links:
        try:
            rec = extract_country_data(link)
            records.append(rec)
        except Exception as e:
            print(f"Error processing {link}: {e}")

    # 3. Load into DataFrame
    df_demographics = pd.DataFrame(records)

    # 4. Cast numeric columns
    for col in [
        'LifeExpectancy_Both',
        'LifeExpectancy_Female',
        'LifeExpectancy_Male',
        'UrbanPopulation_Percentage',
        'UrbanPopulation_Absolute',
        'PopulationDensity'
    ]:
        df_demographics[col] = pd.to_numeric(df_demographics[col], errors='coerce')

    # 5. Save full dataset
    df_demographics.to_csv(
        os.path.join(OUTPUT_DIR, 'demographics_data.csv'), index=False)