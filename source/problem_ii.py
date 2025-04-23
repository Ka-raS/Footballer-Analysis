from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec


def _output_top_3_txt(players: pd.DataFrame, output_dir: Path) -> None:
    """write to top_3.txt from DataFrame: 
    - each row is a data-stat
    - 1st column: data-stat names
    - 2nd-7th column: (player name + data) of 3 highests and 3 lowests
    - skip non numeric data-stats (name, team, nationality...) 
    """
    print('Finding the 3 Highests and 3 Lowests of each Data-Stat...')
    
    # list[6 players of each data-stat]
    result: list[list[str | None]] = []
    names = players['name']
    num_dstats = players.select_dtypes('number').columns
    
    for dstat in num_dstats:
        column = players[dstat]
        series = pd.concat([column.nlargest(3), column.nsmallest(3)])
        result.append([dstat] + [
            np.nan if np.isnan(data)
            else f'{names.loc[i]} - {data}'
            for i, data in series.items()
        ])

    columns = ['data-stat', '1st highest', '2nd highest', '3rd highest', '1st lowest', '2nd lowest', '3rd lowest']
    result_df = pd.DataFrame(result, columns=columns)
    with open(output_dir / 'top_3.txt', 'w', encoding='utf-8') as top_3:
        top_3.write(result_df.to_string(na_rep='N/a'))
    print('Output to top_3.txt')

def _output_results2_csv(players: pd.DataFrame, output_dir: Path) -> None:
    """write to results2.csv from DataFrame:
    - each row is a team (1st row is all team)
    - 1st column: team names
    - 2nd-nth columns: mean1, median1, std1...mean_n, median_n, std_n (for n data-stats)
    """
    print('Finding Means, Medians and Stds...')

    # result[i] = [team i, median1, mean1, std1...median_n, mean_n, std_n]
    result: list[list[float, str]] = []
    # all team + each teams
    data_frames = [('all', players)] + list(players.groupby('team'))
    num_dstats = players.select_dtypes('number').columns
    
    for group, df in data_frames:
        data: list[str | float] = [group]
        for dstat in num_dstats:
            column: pd.Series = df[dstat]
            data.extend([
                column.median(),
                column.mean(),
                column.std(),
            ])
        result.append(data)

    columns = ['team'] + [
        f'{label} of {dstat}'
        for dstat in num_dstats
            for label in ['Median', 'Mean', 'Std']
    ]
    result_df = pd.DataFrame(result, columns=columns)
    result_df.to_csv(output_dir / 'results2.csv', na_rep='N\a', encoding='utf-8')
    print('Output to results2.csv')

def _output_histograms(players: pd.DataFrame, output_dir: Path) -> None:
    """save a .svg for each data-stat
    each .svg has a histogram of all player + histograms of each team
    """
    print('Plotting Histograms...')

    hists_dir = output_dir / 'histograms'
    hists_dir.mkdir(exist_ok=True)
    team_dfs = list(players.groupby('team'))
    num_dstats = players.select_dtypes('number').columns
    count = len(num_dstats)

    for i, dstat in enumerate(num_dstats):
        print(f'\r[{i}/{count}] Data-Stat: {dstat}                 ', end='')
        with plt.style.context('dark_background'):
            fig = plt.figure(figsize=(18, 9))
        rows = cols = 5
        gs = gridspec.GridSpec(rows, cols, figure=fig)

        # 'all' histogram

        ax_all = fig.add_subplot(gs[0, 1:4])
        ax_all.hist(players[dstat], color='white', edgecolor='black')
        ax_all.set_title('all')

        # teams histograms

        # skip r = 0
        specs = [
            gs[r + 1, c]
            for r, c in np.ndindex(rows - 1, cols)
        ]
        is_ax0 = True
        for spec, (team, df) in zip(specs, team_dfs):
            if is_ax0:
                is_ax0 = False
                ax = ax0 = fig.add_subplot(spec)
            else:
                ax = fig.add_subplot(spec, sharex=ax0, sharey=ax0)
            ax.hist(df[dstat], color='white', edgecolor='black')
            ax.tick_params(color='white')
            ax.set_title(team)
            
        fig.tight_layout()
        fig.savefig(hists_dir / f'{dstat}.svg')
        plt.close(fig)

    print(f'\r[{count}/{count}] Done                                   ')
    print('Output to histograms/*svg')

def solve(players: pd.DataFrame, output_dir: Path) -> None:
    _output_top_3_txt(players, output_dir)
    _output_results2_csv(players, output_dir)
    _output_histograms(players, output_dir)