import time
from collections.abc import ValuesView

import bs4
import requests
import numpy 
import pandas


TABLES_STATS = {
    'stats_standard_9': [
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
    ],
    'stats_keeper_9': [
        'gk_goals_against_per90',
        'gk_save_pct',
        'gk_clean_sheets_pct',
        'gk_pens_save_pct'
    ],
    'stats_shooting_9': [
        'shots_on_target_pct',
        'shots_on_target_per90',
        'goals_per_shot',
        'average_shot_distance'
    ],
    'stats_passing_9': [
        'passes_completed',
        'passes_pct',
        'passes_total_distance',
        'passes_pct_short',
        'passes_pct_medium',
        'passes_pct_long',
        'assisted_shots',
        'passes_into_final_third',
        'passes_into_penalty_area',
        'crosses_into_penalty_area',
        'progressive_passes'
    ],
    'stats_gca_9': [
        'sca',
        'sca_per90',
        'gca',
        'gca_per90'
    ],
    'stats_defense_9': [
        'tackles',
        'tackles_won',
        'challenges',
        'challenges_lost',
        'blocks',
        'blocked_shots',
        'blocked_passes',
        'interceptions'
    ],
    'stats_possession_9': [
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
        'progressive_carries',
        'carries_into_final_third',
        'carries_into_penalty_area',
        'miscontrols',
        'dispossessed',
        'passes_received',
        'progressive_passes_received'
    ],
    'stats_misc_9': [
        'fouls',
        'fouled',
        'offsides',
        'crosses',
        'ball_recoveries',
        'aerials_won',
        'aerials_lost',
        'aerials_won_pct'
    ],
}

STATS = ['name', 'team'] + [
    stat_id
    for stat_list in TABLES_STATS.values()
        for stat_id in stat_list
]


def _convert_dtype(text: str) -> int | float | str:
    if text == '':
        return numpy.nan
    formatted = text.replace(',', '') # format 123,456,789.123 -> 123456789.123
    for dtype in [int, float]:
        try:
            return dtype(formatted)
        except ValueError:
            pass
    return text

def _get_players_from_team(team: str, url: str, minutes_minimum: int) -> ValuesView[list[int | float | str]]:
    """Return Iterable[player] (or dict_values...)"""

    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    response.close()

    # dict[name, stats]
    players: dict[str, list[int | float | str]] = {}

    # choose player with minutes > minutes_minimum
    for tr in soup.select(f'table#stats_playing_time_9 > tbody > tr'):
        name = tr.select_one('th').text
        minutes = _convert_dtype(tr.select_one('td[data-stat="minutes"]').text)
        if minutes is not numpy.nan and minutes > minutes_minimum:
            players[name] = [name, team]

    # find all players' stats
    stat_count = 2 # [name, team]
    for table_id, stat_id_targets in TABLES_STATS.items():
        stat_count += len(stat_id_targets)

        # player in table
        for tr in soup.select(f'table#{table_id} > tbody > tr'):
            name = tr.select_one('th').text
            if name not in players:
                continue

            # dict[stat id, value]
            stats_found = {
                td['data-stat']: td.text 
                for td in tr.select('td[data-stat]')
            }
            players[name].extend(
                _convert_dtype(stats_found[stat_id])
                for stat_id in stat_id_targets
            )

        # player not in table
        for stats in players.values():
            if len(stats) < stat_count:
                stats.extend([numpy.nan] * (stat_count - len(stats)))

    return players.values()

def _get_team_name_and_urls() -> list[tuple[str, str]]:
    """Return list[team, url]"""

    url = 'https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    response.close()

    # Premier League Table
    selector = 'table#results2024-202591_overall > tbody > tr > td[data-stat="team"] > a'
    return [
        (a.text, 'https://fbref.com' + a['href'])
        for a in soup.select(selector)
    ]

def get_premier_league_players() -> pandas.DataFrame:
    """Return DataFrame
    - index=default
    - columns=configs.STATS.
    - each row is a player
    """

    request_sleep = 6.0
    print("Scraping fbref.com...")
    print(f'Sleep / Request: {request_sleep} Seconds')

    # list[player]
    players: list[list[int | float | str]] = []

    minutes_minimum = 90
    team_infos = _get_team_name_and_urls()
    time.sleep(request_sleep)

    for count, (team, url) in enumerate(team_infos):
        print(f"[{count}/{len(team_infos)}] Team: {team}")
        players.extend(_get_players_from_team(team, url, minutes_minimum))
        time.sleep(request_sleep) 

    players.sort()
    return pandas.DataFrame(players, columns=STATS)