from pathlib import Path
from collections.abc import Iterable

import bs4
import numpy as np
import numpy.typing as npt
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchDriverException
from sklearn.linear_model import LinearRegression


IV_DIR = Path('output/problem_iv')

# Problem IV.1

ARCHIVES_DIR = Path(__file__).parents[1] / 'archives/footballtransfers.com'

MINUTES_MINIMUM = 900
TABLE_PAGES = range(1, 23)
FBTRANSFERS_PREMIER_URL = 'https://www.footballtransfers.com/en/values/players/most-valuable-players/playing-in-uk-premier-league/'

# player names from footballtransfers.com to fbref.com 
UNIQUE_NAMES = {
    'Albert Grønbæk': 'Albert Grønbaek', 'Alphonse Aréola': 'Alphonse Areola', 'Arijanet Murić': 'Arijanet Muric',
    'Armel Bella-Kotchap': 'Armel Bella Kotchap', 'Bobby Reid': 'Bobby De Cordova-Reid', 'Caoimhin Kelleher': 'Caoimhín Kelleher',
    'Edward Nketiah': 'Eddie Nketiah', 'Felipe Morato': 'Morato', 'Ferdi Kadıoğlu': 'Ferdi Kadioglu', 'Hee-chan Hwang': 'Hwang Hee-chan',
    'Heung-min Son': 'Son Heung-min', 'Idrissa Gueye': 'Idrissa Gana Gueye', 'Igor Júlio': 'Igor', 'Ismaïla Sarr': 'Ismaila Sarr', 
    'J. Philogene': 'Jaden Philogene Bidace', 'James McAtee': 'James Mcatee', 'Jurrien Timber': 'Jurriën Timber', 
    'Jérémy Doku': 'Jeremy Doku', 'Manuel Ugarte': 'Manuel Ugarte Ribeiro', 'Miloš Kerkez': 'Milos Kerkez', 
    'Mykhaylo Mudryk': 'Mykhailo Mudryk', 'Nathan Wood': 'Nathan Wood-Gordon', 'Nico González': 'Nicolás González',
    'O. Hutchinson': 'Omari Hutchinson', 'Radu Drăguşin': 'Radu Drăgușin', 'Rasmus Winther Højlund': 'Rasmus Højlund',
    'Rayan Aït Nouri': 'Rayan Aït-Nouri', 'Victor Kristiansen': 'Victor Bernth Kristiansen', 'Will Smallbone': 'William Smallbone'
}

def get_tables_page_sources() -> Iterable[bs4.BeautifulSoup]:
    try:
        driver = webdriver.Firefox()
    except NoSuchDriverException:
        driver = webdriver.Chrome()

    for page in TABLE_PAGES:
        url = f'{FBTRANSFERS_PREMIER_URL}{page}'    
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                "tbody#player-table-body > tr:not(.table-placeholder)"
            ))
        ) # load javascript
        soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
        yield soup
    driver.close()

def get_tables_page_sources_archived() -> Iterable[bs4.BeautifulSoup]:
    for html_dir in ARCHIVES_DIR.glob('*.html'):
        with open(html_dir, 'r', encoding='utf-8') as html:
            soup = bs4.BeautifulSoup(html.read(), 'html.parser')
        yield soup

def get_transfer_values_from_table(names: set[str], soup: bs4.BeautifulSoup) -> Iterable[tuple[str, int]]:
    """return generator of (name, value)"""

    for tr in soup.select('tbody#player-table-body > tr'):
        a = tr.select_one('td.td-player > div > div.text > a')
        name = a.get_text(strip=True)
        name = UNIQUE_NAMES.get(name, name)
        if name not in names:
            continue
        span = tr.select_one('td.text-center > span')
        value = span.get_text(strip=True)[1:-1] # '€12.3M' -> '12.3'
        value = int(float(value) * 1_000_000)
        yield name, value 

def scrape_players_transfer_values(players_df: pd.DataFrame, from_archives: bool) -> pd.DataFrame:
    """Scrape data from footballtransfers.com
    - get players with minutes > 900
    - 2 columns: player name, value
    """
    names_values: list[tuple[str, int]] = []
    names = set(players_df.loc[players_df['minutes'] > MINUTES_MINIMUM, 'name'])
    soups = get_tables_page_sources_archived() if from_archives else get_tables_page_sources()

    for soup in soups:
        names_values.extend(get_transfer_values_from_table(names, soup))
    
    # sort by name
    names_values.sort(key=lambda x: x[0])
    df = pd.DataFrame(names_values, columns=['name', 'value (€)'])
    return df

# Problem IV.2

def process_data(players_df: pd.DataFrame, transfer_values: pd.DataFrame) -> tuple[pd.DataFrame, npt.NDArray[np.int_]]:
    merged = pd.merge(players_df, transfer_values, on='name') # both sorted but trust issue hits hard
    merged = merged.dropna(subset=['value (€)'])

    y = merged['value (€)'].to_numpy()
    X = merged.select_dtypes('number')
    X = X.drop(columns='value (€)')
    X = X.fillna(0)
    X = pd.get_dummies(X, dtype=int, drop_first=True) # one-hot encoding
    
    return X, y


def solve(players_df: pd.DataFrame, transfer_values: pd.DataFrame) -> None:
    transfer_values.to_csv(IV_DIR / 'transfer_values_scraped.csv', na_rep='N/a', encoding='utf-8')
    print('Output transfer_values_scraped.csv')

    X, y = process_data(players_df, transfer_values)
    return
    return X, y
    # features = problem_iv.select_features(players_df, transfer_values)
    
    # model = problem_iv.make_transfers_eval_model()