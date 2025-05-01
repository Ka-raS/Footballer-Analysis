import bs4
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver.support import expected_conditions as EC


MINUTES_PLAYED_ABOVE = 900
TABLE_PAGES = range(1, 23)
FBTRANSFERS_PREMIER_URL = 'https://www.footballtransfers.com/en/values/players/most-valuable-players/playing-in-uk-premier-league/'

# player names from footballtransfers.com to fbref.com 
UNIQUE_NAMES = {
    'Albert Grønbæk': 'Albert Grønbaek',
    'Alphonse Aréola': 'Alphonse Areola',
    'Arijanet Murić': 'Arijanet Muric',
    'Armel Bella-Kotchap': 'Armel Bella Kotchap',
    'Bobby Reid': 'Bobby De Cordova-Reid',
    'Caoimhin Kelleher': 'Caoimhín Kelleher',
    'Edward Nketiah': 'Eddie Nketiah',
    'Felipe Morato': 'Morato',
    'Ferdi Kadıoğlu': 'Ferdi Kadioglu',
    'Hee-chan Hwang': 'Hwang Hee-chan',
    'Heung-min Son': 'Son Heung-min',
    'Idrissa Gueye': 'Idrissa Gana Gueye',
    'Igor Júlio': 'Igor',
    'Ismaïla Sarr': 'Ismaila Sarr',
    'J. Philogene': 'Jaden Philogene Bidace',
    'James McAtee': 'James Mcatee',
    'Jurrien Timber': 'Jurriën Timber',
    'Jérémy Doku': 'Jeremy Doku',
    'Manuel Ugarte': 'Manuel Ugarte Ribeiro',
    'Miloš Kerkez': 'Milos Kerkez',
    'Mykhaylo Mudryk': 'Mykhailo Mudryk',
    'Nathan Wood': 'Nathan Wood-Gordon',
    'Nico González': 'Nicolás González',
    'O. Hutchinson': 'Omari Hutchinson',
    'Radu Drăguşin': 'Radu Drăgușin',
    'Rasmus Winther Højlund': 'Rasmus Højlund',
    'Rayan Aït Nouri': 'Rayan Aït-Nouri',
    'Victor Kristiansen': 'Victor Bernth Kristiansen',
    'Will Smallbone': 'William Smallbone'
}


def _get_transfer_values(names: set[str]) -> list[tuple[str, float]]:
    """return list of (name, transfer value - Million €)"""
    try:
        driver = webdriver.Firefox()
    except NoSuchDriverException:
        driver = webdriver.Chrome()
    result: list[tuple[str, float]] = []

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

        for tr in soup.select('tbody#player-table-body > tr'):
            a = tr.select_one('td.td-player > div > div.text > a')
            name = a.get_text(strip=True)
            name = UNIQUE_NAMES.get(name, name)
            if name not in names:
                continue
            span = tr.select_one('td.text-center > span')
            value = float(span.get_text(strip=True)[1:-1]) # '€12.3M' -> 12.3
            result.append((name, value)) 
    
    driver.close()
    return result

def scrape_players_transfer_values(players_df: pd.DataFrame) -> pd.DataFrame:
    """Scrape data from footballtransfers.com
    - get players with minutes > 900
    - 2 columns: player name, transfer value
    """
    names = players_df.loc[players_df['minutes'] > MINUTES_PLAYED_ABOVE, 'name']
    name_transfer_values = _get_transfer_values(set(names))
    df = pd.DataFrame(name_transfer_values, columns=['name', 'transfer_value'])
    return df

