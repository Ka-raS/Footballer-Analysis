import time
from collections.abc import ValuesView

import bs4
import requests
import pandas as pd


# list[tuple[table id, list[data-stat]]]
TABLES_STATS = [
    ('stats_standard_9', [
        'nationality',
        'position',
        'age', 
        'games',
        'games_starts',
        'minutes',
        'goals',
        'assists',
        'cards_yellow',
        'cards_red',
        'xg',
        'xg_assist',
        'progressive_carries',
        'progressive_passes',
        'progressive_passes_received',
        'goals_per90',
        'assists_per90',
        'xg_per90',
        'xg_assist_per90'
    ]),
    ('stats_keeper_9', [
        'gk_goals_against_per90',
        'gk_save_pct',
        'gk_clean_sheets_pct',
        'gk_pens_save_pct'
    ]), 
    ('stats_shooting_9', [
        'shots_on_target_pct',
        'shots_on_target_per90',
        'goals_per_shot',
        'average_shot_distance'
    ]),
    ('stats_passing_9', [
        'passes_completed',
        'passes_pct',
        'passes_total_distance',
        'passes_pct_short',
        'passes_pct_medium',
        'passes_pct_long',
        'assisted_shots',
        'passes_into_final_third',
        'passes_into_penalty_area',
        'crosses_into_penalty_area'
    ]),
    ('stats_gca_9', [
        'sca',
        'sca_per90',
        'gca',
        'gca_per90'
    ]),
    ('stats_defense_9', [
        'tackles',
        'tackles_won',
        'challenges',
        'challenges_lost',
        'blocks',
        'blocked_shots',
        'blocked_passes',
        'interceptions'
    ]),
    ('stats_possession_9', [
        'touches',
        'touches_def_pen_area',
        'touches_def_3rd',
        'touches_mid_3rd',
        'touches_att_3rd',
        'touches_att_pen_area',
        'take_ons',
        'take_ons_won_pct',
        'take_ons_tackled_pct',
        'carries',
        'carries_progressive_distance',
        'carries_into_final_third',
        'carries_into_penalty_area',
        'miscontrols',
        'dispossessed',
        'passes_received'
    ]),
    ('stats_misc_9', [
        'fouls',
        'fouled',
        'offsides',
        'crosses',
        'ball_recoveries',
        'aerials_won',
        'aerials_lost',
        'aerials_won_pct'
    ])
]

Data = int | float | str

def _convert_dtype(text: str) -> Data:
    if text == '':
        return pd.NA
    formatted = text.replace(',', '') # format 123,456,789.123 -> 123456789.123
    for dtype in (int, float):
        try:
            return dtype(formatted)
        except ValueError:
            pass
    return text

def _get_players_from_team(team: str, url: str, minutes_minimum: int) -> ValuesView[list[Data]]:
    """return players data-stats in TABLES_STATS"""

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Status Code {response.status_code} From {url}')
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    response.close()

    # str: name
    players: dict[str, list[Data]] = {}

    # filter player with minutes > minutes_minimum
    for tr in soup.select(f'table#stats_playing_time_9 > tbody > tr'):
        name = tr.th.text
        td = tr.select_one('td[data-stat="minutes"]')
        minutes = _convert_dtype(td.text)
        if pd.notna(minutes) and minutes > minutes_minimum:
            players[name] = [name, team]
    
    # find remaining players data-stats
    data_count = 2 # [name, team]
    for table_id, data_stats_target in TABLES_STATS:
        data_count += len(data_stats_target)

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
                _convert_dtype(data_found[data_stat])
                for data_stat in data_stats_target
            )

        # players not in table
        for data_list in players.values():
            missing = data_count - len(data_list)
            data_list.extend([pd.NA] * missing)

    return players.values()

def _get_team_name_and_urls() -> list[tuple[str, str]]:
    """return list[tuple[team, url]]"""

    url = 'https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Status Code {response.status_code} From {url}')
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    response.close()

    # Premier League Table
    selector = 'table#results2024-202591_overall > tbody > tr > td[data-stat="team"] > a'
    return [
        (a.text, 'https://fbref.com' + a['href'])
        for a in soup.select(selector)
    ]

def get_premier_league_players() -> pd.DataFrame:
    """return DataFrame:
    - each row is a player
    - each column is a data-stat
    - cell = numpy.nan if empty or not found
    """

    request_sleep = 6.0
    print("Scraping fbref.com...")
    print(f'Sleep / Request: {request_sleep} Seconds')

    players: list[list[Data]] = []
    team_infos = _get_team_name_and_urls()
    time.sleep(request_sleep)
    team_count = len(team_infos)
    minutes_minimum = 90

    for count, (team, url) in enumerate(team_infos):
        print(f"[{count}/{team_count}] Team: {team}")
        players.extend(_get_players_from_team(team, url, minutes_minimum))
        time.sleep(request_sleep) 

    # sort by name
    players.sort()
    columns = ['name', 'team'] + [
        data_stat
        for _, data_stats in TABLES_STATS
            for data_stat in data_stats
    ]
    return pd.DataFrame(players, columns=columns)