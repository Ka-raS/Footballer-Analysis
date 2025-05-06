from pathlib import Path
from collections.abc import Iterable

import bs4
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException


II_DIR = Path('output/problem_i')
ARCHIVES_DIR = Path(__file__).parents[1] / 'archives/fbref.com'

MINUTES_PLAYED_ABOVE = 90
FBREF_PREMIER_URL = 'https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats/'

# Premier League Table
TEAM_TABLE_ID = 'results2024-202591_overall'

# table ids + stat lists
TABLES_STATS = [
(
    'stats_standard_9', [
        'nationality', 'position', 'age',  'games', 'games_starts', 'minutes', 'goals', 'assists', 
        'cards_yellow', 'cards_red', 'xg', 'xg_assist', 'progressive_carries', 'progressive_passes', 
        'progressive_passes_received', 'goals_per90', 'assists_per90', 'xg_per90', 'xg_assist_per90'
    ]
),
(
    'stats_keeper_9', [
        'gk_goals_against_per90', 'gk_save_pct', 'gk_clean_sheets_pct', 'gk_pens_save_pct'
    ]
),
(
    'stats_shooting_9', [
        'shots_on_target_pct', 'shots_on_target_per90', 'goals_per_shot', 'average_shot_distance'
    ]
),
(
    'stats_passing_9', [
        'passes_completed', 'passes_pct', 'passes_total_distance', 'passes_pct_short', 'passes_pct_medium', 
        'passes_pct_long', 'assisted_shots', 'passes_into_final_third', 'passes_into_penalty_area', 'crosses_into_penalty_area'
    ]
),
(
    'stats_gca_9', [
        'sca', 'sca_per90', 'gca', 'gca_per90'
    ]
),
(
    'stats_defense_9', [
        'tackles', 'tackles_won', 'challenges', 'challenges_lost', 'blocks', 'blocked_shots', 'blocked_passes', 'interceptions'
    ]
),
(
    'stats_possession_9', [
        'touches', 'touches_def_pen_area', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd', 'touches_att_pen_area', 
        'take_ons', 'take_ons_won_pct', 'take_ons_tackled_pct', 'carries', 'carries_progressive_distance', 
        'carries_into_final_third', 'carries_into_penalty_area', 'miscontrols', 'dispossessed', 'passes_received'
    ]
),
(
    'stats_misc_9', [
        'fouls', 'fouled', 'offsides', 'crosses', 'ball_recoveries', 'aerials_won', 'aerials_lost', 'aerials_won_pct'
    ]
)
] # TABLES_DATA_STATS

def get_teams_page_sources() -> Iterable[tuple[str, bs4.BeautifulSoup]]:
    """return generator of (team name, page source)"""
    try:
        driver = webdriver.Firefox()
    except NoSuchDriverException:
        driver = webdriver.Chrome()
    driver.get(FBREF_PREMIER_URL)
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')

    for a in soup.select(f'table#{TEAM_TABLE_ID} > tbody > tr > td[data-stat="team"] > a'):
        team = a.get_text(strip=True)
        url = 'https://fbref.com' + a['href']
        driver.get(url)
        soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
        yield team, soup

    driver.close()

def get_teams_page_sources_archived() -> Iterable[tuple[str, bs4.BeautifulSoup]]:
    """return generator of (team name, page source)"""
    for html_dir in ARCHIVES_DIR.glob('*.html'):
        team = html_dir.stem
        if team == 'Premier League':
            continue
        with open(html_dir, 'r', encoding='utf-8') as html:
            soup = bs4.BeautifulSoup(html.read(), 'html.parser')
        yield team, soup

def get_players_from_team(team: str, soup: bs4.BeautifulSoup) -> Iterable[list[str]]:
    """return team members data in TABLES_STATS"""
    # str: name
    players: dict[str, list[str]] = {} 

    # add players with minutes > 90
    standard_table_id = TABLES_STATS[0][0]
    list_tr = soup.select(f'table#{standard_table_id} > tbody > tr:not(.thead)')
    for tr in list_tr:
        name = tr.th.get_text(strip=True)
        td = tr.select_one('td[data-stat="minutes"]')
        minutes = int('0' + td.get_text(strip=True).replace(',', '')) # '1,234' -> 01234
        if minutes > MINUTES_PLAYED_ABOVE:
            players[name] = [name, team]
    
    # find data-stats
    stat_count = 2 # [name, team]
    for table_id, stat_targets in TABLES_STATS:
        stat_count += len(stat_targets)

        # players in table
        for tr in soup.select(f'table#{table_id} > tbody > tr:not(.thead)'):
            name = tr.th.get_text(strip=True)
            if name not in players:
                continue
            data_found = {
                td['data-stat']: td.get_text(strip=True)
                for td in tr.select('td[data-stat]')
            }
            players[name].extend(
                data_found[stat]
                for stat in stat_targets
            )

        # players not in table
        for stat_list in players.values():
            missing = stat_count - len(stat_list)
            stat_list.extend([''] * missing)

    return players.values()

def process_data(players: list[list[str]]) -> pd.DataFrame:
    # sort by name
    players.sort()
    columns = ['name', 'team'] + [
        stat
        for _, stat_list in TABLES_STATS
            for stat in stat_list 
    ]
    df = pd.DataFrame(players, columns=columns)
    df.drop_duplicates(['name'], keep='first', inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.replace('', np.nan)
    
    # '23-123' -> 23.337
    def convert_age(age: str) -> float:
        years, days = map(int, age.split('-'))
        return round(years + days / 365, ndigits=3)
    
    def to_numeric(series: pd.Series) -> pd.Series:
        try:
            return pd.to_numeric(series)
        except ValueError:
            return series.astype('string')

    df['age'] = df['age'].apply(convert_age)
    df['minutes'] = df['minutes'].str.replace(',', '') # '1,234 -> 1234'
    df['nationality'] = df['nationality'].str[-3:] # 'eng ENG' -> 'ENG'
    df = df.apply(to_numeric)
    return df

def scrape_premier_league_players(from_archives: bool) -> pd.DataFrame:
    """scrape data from fbref.com.
    - get players with minutes > 90
    - each row is a player
    - each column is a stat
    """
    players: list[list[str]] = []
    teams_soups = get_teams_page_sources_archived() if from_archives else get_teams_page_sources()
    for team, soup in teams_soups:
        players.extend(get_players_from_team(team, soup)) 
    return process_data(players)


def solve(players_df: pd.DataFrame) -> None:
    II_DIR.mkdir(parents=True, exist_ok=True)

    players_df.to_csv(II_DIR / 'results.csv', na_rep='N/a', encoding='utf-8')
    print('Output results.csv')