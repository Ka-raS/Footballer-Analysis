import time
from pathlib import Path
from collections.abc import ValuesView

import requests
import pandas as pd
from bs4 import BeautifulSoup


# list[tuple[table id, list[data-stat]]]
TABLES_DATA_STATS = [
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

Data = int | float | str | None

def _convert_type(text: str) -> Data:
    if not text:
        return None
    formatted = text.replace(',', '') # format 123,456,789.123 -> 123456789.123
    for t in (int, float):
        try:
            return t(formatted)
        except ValueError:
            pass
    return text

def _get_players_from_team(team: str, url: str, minutes_minimum: int) -> ValuesView[list[Data]]:
    """return players data-stats in TABLES_DATA_STATS"""

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    response.close()

    # str: name
    players: dict[str, list[Data]] = {}

    # filter player with minutes > minutes_minimum
    for tr in soup.select(f'table#stats_playing_time_9 > tbody > tr'):
        name = tr.th.text
        td = tr.select_one('td[data-stat="minutes"]')
        minutes = _convert_type(td.text)
        if minutes and minutes > minutes_minimum:
            players[name] = [name, team]
    
    # find remaining players data-stats
    ds_count = 2 # [name, team]
    for table_id, dstats_target in TABLES_DATA_STATS:
        ds_count += len(dstats_target)

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
                _convert_type(data_found[dstat])
                for dstat in dstats_target
            )

        # players not in table
        for data_list in players.values():
            missing = ds_count - len(data_list)
            data_list.extend([None] * missing)

    return players.values()

def _get_team_name_and_urls() -> list[tuple[str, str]]:
    """return list[tuple[team, url]]"""

    url = 'https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
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
    """

    request_sleep = 6.0
    print('Scraping fbref.com...')
    print(f'Sleep / Request: {request_sleep} seconds')

    players: list[list[Data]] = []
    minutes_minimum = 90
    team_infos = _get_team_name_and_urls()
    time.sleep(request_sleep)
    count = len(team_infos)

    for i, (team, url) in enumerate(team_infos):
        print(f'\r[{i}/{count}] Team: {team}         ', end='')
        players.extend(_get_players_from_team(team, url, minutes_minimum))
        time.sleep(request_sleep)
    print(f'\r[{count}/{count}] Done                 ')

    # sort by name
    players.sort()
    columns = ['name', 'team'] + [
        dstat
        for _, dstats in TABLES_DATA_STATS
            for dstat in dstats
    ]
    return pd.DataFrame(players, columns=columns)

def solve(players: pd.DataFrame, output_dir: Path) -> None:
    players.to_csv(output_dir / 'results.csv', na_rep='N/a', encoding='utf-8')
    print('Output to results.csv')