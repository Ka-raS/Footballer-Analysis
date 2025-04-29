from collections.abc import Iterable

import bs4
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


FBREF_PREMIER_URL = 'https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats'
TEAM_TABLE_ID = 'results2024-202591_overall'
MINUTES_PLAYED_ABOVE = 90

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


def _get_team_name_and_urls(driver: WebDriver) -> list[tuple[str, str]]:
    """return list of (team_name, team_url)"""

    driver.get(FBREF_PREMIER_URL)
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')

    # Premier League Table
    selector = f'table#{TEAM_TABLE_ID} > tbody > tr > td[data-stat="team"] > a'
    return [
        (a.text, 'https://fbref.com' + a['href'])
        for a in soup.select(selector)
    ]

def _get_players_from_team(team: str, url: str, driver: WebDriver) -> Iterable[list[str]]:
    """return team members data in TABLES_STATS"""

    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    players: dict[str, list[str]] = {} # str: name

    # add players with minutes > minutes_minimum
    for tr in soup.select(f'table#stats_playing_time_9 > tbody > tr[data-row]:not([class])'):
        name = tr.th.text
        td = tr.select_one('td[data-stat="minutes"]')
        minutes = int('0' + td.text.replace(',', '')) # '1,234' -> '01234'
        if minutes > MINUTES_PLAYED_ABOVE:
            players[name] = [name, team]
    
    # find data-stats
    stat_count = 2 # [name, team]
    for table_id, stat_targets in TABLES_STATS:
        stat_count += len(stat_targets)

        # players in table
        for tr in soup.select(f'table#{table_id} > tbody > tr'):
            name = tr.th.text
            if name not in players:
                continue
            data_found = {
                td['data-stat']: td.text
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

def _process_data(players: list[list[str]]) -> pd.DataFrame:
    # sort by name
    players.sort()
    columns = ['name', 'team'] + [
        stat
        for _, stat_list in TABLES_STATS
            for stat in stat_list 
    ]
    df = pd.DataFrame(players, columns=columns)
    df.replace('', np.nan)
    
    # '23-123' -> 23.337
    def convert_age(age: str) -> float:
        years, days = map(int, age.split('-'))
        return round(years + days / 365, ndigits=3)
    
    df['age'] = df['age'].apply(convert_age)
    df['minutes'] = df['minutes'].str.replace(',', '') # '1,234 -> 1234'
    df['nationality'] = df['nationality'].str[-3:] # 'eng ENG' -> 'ENG'


    def to_numeric(series: pd.Series) -> pd.Series:
        try:
            return pd.to_numeric(series)
        except Exception:
            return series
    df = df.apply(to_numeric)
    return df

def get_premier_league_players() -> pd.DataFrame:
    """scrape data from fbref.com.
    - each row is a player
    - each column is a stat
    """
    players: list[list[str]] = []

    try:
        driver = webdriver.Firefox()
    except Exception:
        driver = webdriver.Chrome()

    team_infos = _get_team_name_and_urls(driver)
    for team, url in team_infos:
        players.extend(_get_players_from_team(team, url, driver))
    driver.close()

    df = _process_data(players)
    return df