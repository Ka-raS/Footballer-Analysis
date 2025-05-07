from pathlib import Path
from collections.abc import Iterable

import bs4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchDriverException
from sklearn.decomposition import PCA
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error


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

def get_transfer_values_from_table(names: set[str], soup: bs4.BeautifulSoup) -> Iterable[tuple[str, float]]:
    """return generator of (name, value)"""

    for tr in soup.select('tbody#player-table-body > tr'):
        a = tr.select_one('td.td-player > div > div.text > a')
        name = a.get_text(strip=True)
        name = UNIQUE_NAMES.get(name, name)
        if name not in names:
            continue
        span = tr.select_one('td.text-center > span')
        value = float(span.get_text(strip=True)[1:-1]) # '€12.3M' -> 12.3
        yield name, value 

def scrape_players_transfer_values(players_df: pd.DataFrame, from_archives: bool) -> pd.DataFrame:
    """Scrape data from footballtransfers.com
    - get players with minutes > 900
    - 2 columns: player name, value
    """
    names_values: list[tuple[str, float]] = []
    names = set(players_df.loc[players_df['minutes'] > MINUTES_MINIMUM, 'name'])
    soups = get_tables_page_sources_archived() if from_archives else get_tables_page_sources()
    for soup in soups:
        names_values.extend(get_transfer_values_from_table(names, soup))
    
    # sort by name
    names_values.sort(key=lambda x: x[0])
    df = pd.DataFrame(names_values, columns=['name', 'value (€1M)'])
    return df

# Problem IV.2

GK_STATS = [
    'gk_goals_against_per90', 'gk_save_pct', 'gk_clean_sheets_pct', 'gk_pens_save_pct'
]

def process_data(players_df: pd.DataFrame) -> pd.DataFrame:
    """fillna, one-hot encode, standardize"""
    df = players_df.drop(columns=['name'])

    # fillna mean for goal keepers' goal keeper stats
    df.loc[df['position'] == 'GK', GK_STATS].fillna(df[GK_STATS].mean(), inplace=True)
    # fillna 0 for outfielder's goal keeper stats
    df[GK_STATS] = df[GK_STATS].fillna(0)

    df = pd.get_dummies(df, dtype=int, drop_first=True) # one-hot encoding    
    df = df.fillna(df.mean())
    data = StandardScaler().fit_transform(df)
    return pd.DataFrame(data, columns=df.columns)

def scatter_pca_2d(X: pd.DataFrame, y: pd.Series) -> plt.Figure:
    X_pca = PCA(1).fit_transform(X)[:, 0]

    # fitting line
    coefs = np.polyfit(X_pca, y, 1)
    p = np.poly1d(coefs)

    plt.figure(figsize=(16, 9))
    plt.plot(X_pca, p(X_pca), label='fitting line', c='red', linewidth=10)
    plt.scatter(X_pca, y, c='black', s=100)

    plt.title('PCA 2D Map')
    plt.xlabel('X')
    plt.ylabel('y', rotation=45)
    plt.tight_layout()
    return plt.gcf()

def perform_tests(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:...

def predict_transfer_values(X_all: pd.DataFrame, values_scraped_df: pd.DataFrame, 
                            players_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    X = X_all.loc[players_df['name'].isin(values_scraped_df['name'])].reset_index(drop=True)
    y = values_scraped_df['value (€1M)']
    y = y.rename('value true (€1M)')

    model = LassoCV(cv=10, max_iter=20000).fit(X, y)
    y_pred_all = model.predict(X_all)

    values = pd.DataFrame({
        'name': players_df['name'].values,
        'value predict (€1M)': y_pred_all
    }).merge(values_scraped_df, on='name', how='left')
    values['value predict (€1M)'] = values['value predict (€1M)'].round(3)

    feature_importances = pd.DataFrame({
        'Feature': X.columns,
        'Importance': np.abs(model.coef_)
    }).sort_values('Importance', ascending=False)

    return values, feature_importances

def solve(players_df: pd.DataFrame, values_scraped_df: pd.DataFrame) -> None:
    IV_DIR.mkdir(parents=True, exist_ok=True)

    # all player dataset
    X_all = process_data(players_df)

    # drop players without transfer value
    X = X_all.loc[players_df['name'].isin(values_scraped_df['name'])].reset_index(drop=True)
    y = values_scraped_df['value (€1M)']

    pca_2d = scatter_pca_2d(X, y)
    pca_2d.savefig(IV_DIR / 'pca_2d.svg')
    print('Output pca_2d.svg')

    # test_result = perform_tests(X, y)
    # test_result.to_csv(IV_DIR / 'test_result.csv', encoding='utf-8')
    # print('Output test_result.csv')

    values, feature_importance = predict_transfer_values(X_all, values_scraped_df, players_df)
    values.to_csv(IV_DIR / 'transfer_values_predicted.csv', na_rep='N/a', encoding='utf-8')
    print('Output transfer_values_predicted.csv')
    feature_importance.to_csv(IV_DIR / 'feature_importance.csv', encoding='utf-8')
    print('Output feature_importance.csv')

    plt.close('all')