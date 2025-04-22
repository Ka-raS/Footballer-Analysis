from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core.groupby.generic import DataFrameGroupBy

def _find_highest3_lowest3(players: pd.DataFrame, numeric_data_stats: pd.Index) -> pd.DataFrame:
    """return DataFrame: 
    - each row is a data-stat
    - 1st column: data-stat names
    - 2nd-7th column: (player name + data) of 3 highests and 3 lowests
    - skip non numeric data-stats (name, team, nationality...) 
    """
    
    # list[6 players of each data-stat]
    result: list[list[str | None]] = []
    names = players['name']
    
    for data_stat in numeric_data_stats:
        column = players[data_stat]
        series = pd.concat([column.nlargest(3), column.nsmallest(3)])
        result.append([data_stat] + [
            np.nan if np.isnan(data)
            else f'{names.loc[i]} - {data}'
            for i, data in series.items()
        ])

    columns = ['data-stat', '1st highest', '2nd highest', '3rd highest', '1st lowest', '2nd lowest', '3rd lowest']
    return pd.DataFrame(result, columns=columns)

def _find_median_mean_stds(team_data_frames: list[tuple[str, pd.DataFrame]], numeric_data_stats: pd.Index) -> pd.DataFrame:
    """return DataFrame:
    - each row is a team (1st row is all team)
    - 1st column: team names
    - 2nd-nth columns: mean1, median1, std1...mean_n, median_n, std_n (for n data-stats)
    """

    # result[i] = [team i, median1, mean1, std1...median_n, mean_n, std_n]
    result: list[list[float, str]] = []
    
    for team, data_frame in team_data_frames:
        team_data: list[str | float] = [team]
        for data_stat in numeric_data_stats:
            column: pd.Series = data_frame[data_stat]
            team_data.extend([
                column.median(),
                column.mean(),
                column.std(),
            ])
        result.append(team_data)

    columns = ['team'] + [
        f'{label} of {data_stat}'
        for data_stat in numeric_data_stats
            for label in ['Median', 'Mean', 'Std']
    ]
    return pd.DataFrame(result, columns=columns)

def _plot_histogram(team_data_frames: list[tuple[str, pd.DataFrame]], data_stat: str) -> plt.Figure:
    """return subplots of teams for the data-stat"""

    axes: np.ndarray
    size = int(len(team_data_frames) ** 0.5) + 1
    fig, axes = plt.subplots(size, size)
    axes = axes.flatten()
    configs = {
        # 'color': 'black'
        # 'edgecolor': 'white'
    }

    for i, (team, data_frame) in enumerate(team_data_frames):
        ax: plt.Axes = axes[i]
        ax.hist(data_frame[data_stat], **configs)
        ax.set_title(team)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    fig.tight_layout()
    return fig

def solve(players: pd.DataFrame, output_dir: Path) -> None:
    team_data_frames = [('all', players)] + list(players.groupby('team'))
    numeric_data_stats = players.select_dtypes('number').columns

    print('Finding The 3 Highest And 3 Lowest Players Of Each Data-Stat...')
    highest3_lowest3 = _find_highest3_lowest3(players, numeric_data_stats)
    with open(output_dir / 'top_3.txt', 'w', encoding='utf-8') as top_3:
        top_3.write(highest3_lowest3.to_string(na_rep='N/a'))
    print('Output top_3.txt')

    print('Finding Median, Mean, Standard Of Each Statistic And Team...')
    median_mean_stds = _find_median_mean_stds(team_data_frames, numeric_data_stats)
    median_mean_stds.to_csv(output_dir / 'results2.csv', na_rep='N/a', encoding='utf-8')
    print('Output results2.csv')

    print('Plotting Histograms For Each Statistic Between Teams...')
    histograms_dir = output_dir / 'histograms'
    histograms_dir.mkdir(exist_ok=True)

    for data_stat in numeric_data_stats:
        histogram = _plot_histogram(team_data_frames, data_stat)
        histogram.savefig(histograms_dir / f'{data_stat}.svg')

    print('Output histograms/*.svg')