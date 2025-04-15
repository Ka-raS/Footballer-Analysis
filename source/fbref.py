import time
from collections.abc import ValuesView

import bs4
import requests

from source import constants

def _get_players_from_team(team: str, url: str, minutes_minimum: int) -> ValuesView[list[str]]:
    """Scrape data from Premier League team
    - Player with minutes > minutes_minimum
    - return ValueView[list[stat]]
    - raise Exception if status code != 200
    """

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Status code {response.status_code} from {url}')
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    response.close()

    players: dict[str, list[str]] = {} # players.values(): return value

    # check minutes played + init values: [name, team]
    for tr in soup.select(f'table#stats_playing_time_9 > tbody > tr'):
        name = tr.select_one('th').text
        minutes = tr.select_one('td[data-stat="minutes"]').text
        if minutes == '':
            minutes = 0
        else:
            # format '123,456,789.123' -> '123456789.123'
            minutes = int(minutes.replace(',', '')) 
        if minutes > minutes_minimum:
            players[name] = [name, team]

    # find data-stats
    stat_count = 2 # ['name', 'team']
    for table_id, stats_target in constants.TABLES_STATS.items():
        stat_count += len(stats_target)

        # player in table
        for tr in soup.select(f'table#{table_id} > tbody > tr'):
            name = tr.select_one('th').text
            if name not in players:
                continue
            stats_found = {
                td['data-stat']: td.text 
                for td in tr.select('td[data-stat]')
            }
            for stat_id in stats_target:
                value = stats_found[stat_id]
                players[name].append(value)

        # player not in table
        for stats in players.values():
            if len(stats) < stat_count:
                stats.extend([''] * len(stats_target))

    try:
        # fix 'nationality': 'eng ENG' -> 'ENG'
        # but why
        pos = constants.STATS.index('nationality')
        for stats in players.values():
            stats[pos] = stats[pos][-3:]
    except ValueError:
        # 'nationality' not in STATS
        pass
    return players.values()

def _get_team_name_and_urls() -> list[tuple[str, str]]:
    """Scrape data from Premier League table
    - return list[team, url]
    - raise Exception if status code != 200
    """

    premier_url = 'https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats'
    response = requests.get(premier_url)
    if response.status_code != 200:
        raise Exception(f'Status code {response.status_code} from {premier_url}')
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    response.close()

    team_infos: list[tuple[str, str]] = [] # return value
    selector = f'table#results2024-202591_overall > tbody > tr > td[data-stat="team"] > a'
    for a in soup.select(selector):
        team = a.text
        url = 'https://fbref.com' + a['href']
        team_infos.append((team, url))
    return team_infos

def get_premier_league_players() -> list[list[str]]:
    """Scrape Premier League 2024-2025 Players Data From fbref.com
    - return list[player] sorted by player name
    - player: list[stat]
    - list[i][:2]: player i's [name, team]
    - list[i][2:]: player i's [*constants.STATS]
    - raise Exception If Status Code != 200
    """
    
    time_sleep = 6.0
    print("Scraping Premier League 2024-2025 Players' Data")
    print(f'Time Sleep Per Requests: {time_sleep} Seconds')

    players: list[list[str]] = [] # return value
    team_infos = _get_team_name_and_urls()
    time.sleep(time_sleep)
    minutes_minimum = 90

    for count, (team, url) in enumerate(team_infos):
        print(f"[{count}/{len(team_infos)}] Scraping Players From {team}...")
        players.extend(_get_players_from_team(team, url, minutes_minimum))
        time.sleep(time_sleep) 

    # players.sort()
    return players