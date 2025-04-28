from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup

def _find_tranfer_values(names: pd.Series) -> dict[str, float]:
    for i in range(1000):
        print(i)
        url = 'https://www.footballtransfers.com/'
        response = requests.get(url)
        response.raise_for_status()
    return
    soup = BeautifulSoup(response.content, 'html.parser')

    with open('text.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    return
    i = 0
    for tr in soup.select('tbody'):
        i += 1
        # print(tr.prettify())
    print(i)
    return 0


def solve(players_df: pd.DataFrame, output_dir: Path) -> None:
    names = players_df.loc[players_df['minutes'] > 900, 'name']
    tranfer_values = _find_tranfer_values(names)