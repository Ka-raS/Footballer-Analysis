from pathlib import Path
from collections.abc import Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec


def _output_top_3_txt(all_df: pd.DataFrame, names: pd.Series, output_dir: Path) -> None:
    """write to top_3.txt: 
    - each row is a data-stat
    - each column: (player name + data) of 3 highests and 3 lowests
    - skip non-numeric data-stat (name, team, nationality...) 
    """
    print('Finding the 3 Highests and 3 Lowests of each Data-Stat...')

    def find_6players(series: pd.Series) -> list[str]:
        players6 = pd.concat([series.nlargest(3), series.nsmallest(3)])
        return [
            np.nan if np.isnan(data)
            else f'{names.loc[i]} - {data}'
            for i, data in players6.items()
        ]

    result = all_df.apply(find_6players).T
    result.columns = ['1st highest', '2nd highest', '3rd highest', '1st lowest', '2nd lowest', '3rd lowest']
    result.reset_index(names='data-stat', inplace=True)

    with open(output_dir / 'top_3.txt', 'w', encoding='utf-8') as txt:
        txt.write(result.to_string(na_rep='N/a'))
    print('Output to top_3.txt')


def _output_results2_csv(all_df: pd.DataFrame, team_dfs: Iterable[tuple[str, pd.DataFrame]], output_dir: Path) -> None:
    """write to results2.csv:
    - each row is a team (1st row is all team)
    - each column: mean1, median1, std1...mean_n, median_n, std_n (n data-stats)
    - skip non-numeric data-stats (name, team, nationality...) 
    """
    print('Finding Means, Medians and Stds...')

    values = ['median', 'mean', 'std']
    group_dfs = [('all', all_df)] + list(team_dfs)
    result = pd.DataFrame(
        df.agg(values)             # index = ['median', 'mean', 'std'], columns = data-stats
          .T                       # index = data-stats, columns = ['median', 'mean', 'std'] 
          .stack()                 # -> Series: median1, mean1, std1, median2...
          .reset_index(drop=True)  # remove index
        for _, df in group_dfs
    )
    result.columns = [
        f'{value} of {dstat}'
        for dstat in all_df.columns
            for value in values
    ]
    result.insert(0, 'team', [group for group, _ in group_dfs])

    result.to_csv(output_dir / 'results2.csv', na_rep='N/a', encoding='utf-8')
    print('Output to results2.csv')


def _config_ax(ax: plt.Axes, data: pd.Series) -> None:
    ax.hist(data, color='white', edgecolor='black')
    ax.set_facecolor('black')
    for side in ('bottom', 'left'):
        ax.spines[side].set_color('white')
    ax.tick_params(colors='white')

def _plot_figure(all_data: pd.Series, teams_data: Iterable[tuple[str, pd.Series]]) -> plt.Figure:
    """return Figure of subplots
    - 1st row: all_df hist
    - remain rows: team_dfs hists
    """
    
    # 20 teams hists + all hist = 21
    rows = cols = 5
    fig = plt.figure(figsize=(18, 9), facecolor='black')
    gs = gridspec.GridSpec(rows, cols, fig)

    # all_data
    ax_all = fig.add_subplot(gs[0, cols // 2])
    ax_all.set_title('all', color='white')
    _config_ax(ax_all, all_data)

    # teams_data
    is_ax0 = True
    for (r, c), (team, data) in zip(np.ndindex(rows - 1, cols), teams_data):
        # skip r = 0
        if is_ax0:
            is_ax0 = False
            ax = ax0 = fig.add_subplot(gs[r + 1, c]) 
        else:
            ax = fig.add_subplot(gs[r + 1, c], sharex=ax0, sharey=ax0)
        ax.set_title(team, color='white')
        _config_ax(ax, data)

    fig.tight_layout()
    return fig

def _output_histograms(all_df: pd.DataFrame, team_dfs: list[tuple[str, pd.DataFrame]], output_dir: Path) -> None:
    """save a .svg for each data-stat
    each .svg has a histogram of all player + histograms of each team
    skip non-numeric data-stats (name, team, nationality...) 
    """
    print('Plotting Histograms...')

    hists_dir = output_dir / 'histograms'
    hists_dir.mkdir(exist_ok=True)
    # dstats = all_df.columns
    dstats = ['goals_per90', 'assists_per90', 'xg_per90', 'blocks', 'blocked_shots', 'blocked_passes']
    count = len(dstats)

    # for i, dstat in enumerate(all_df.columns):
    for i, dstat in enumerate(dstats):
        print(f'\r[{i}/{count}] Data-Stat: {dstat}                 ', end='')
        teams_data = ((team, df[dstat]) for team, df in team_dfs)
        fig = _plot_figure(all_df[dstat], teams_data)
        fig.savefig(hists_dir / f'{i}. {dstat}.svg')
        plt.close(fig)

    print(f'\r[{count}/{count}] Done                                   ')
    print('Output to histograms/*svg')


BAD_DATA_STATS = {
    'cards_yellow',
    'cards_red',
    'gk_goals_against_per90'
    'challenges_lost',
    'take_ons_tackled_pct',
    'miscontrols',
    'dispossessed',
    'fouls',
    'offsides',
    'aerials_lost'
}

NEUTRAL_DATA_STATS = {
    'games',
    'games_starts',
    'minutes',
    'fouled'
}

def calc_score(series: pd.Series) -> float:
    if series.name in BAD_DATA_STATS:
        return -series.mean()
    return series.mean()

def _output_best_teams_txt(team_dfs: Iterable[tuple[str, pd.DataFrame]], output_dir: Path) -> None:
    """write a best_teams.txt
    - 1st column: data-stats
    - 2nd column: best team names
    - last row: the best team overall
    """
    print('Finding the Best Team for each Data-Stat and Overall...')

    scores_df = pd.DataFrame(
        df.apply(calc_score).rename(team) 
        for team, df in team_dfs
    )
    best_teams = scores_df.idxmax()
    score_sum = scores_df.drop(columns=NEUTRAL_DATA_STATS).sum(axis='columns')
    best_team = score_sum.idxmax()

    result = pd.DataFrame(
        zip(scores_df.columns, best_teams), 
        columns=['data-stat', 'team']
    )
    result.loc[len(result)] = ('overall', best_team)
    
    with open(output_dir / 'best_teams.txt', 'w', encoding='utf-8') as txt:
        txt.write(result.to_string())
    print('Output to best_teams.txt')
    print(f'The Best Performing Team is {best_team}')


def solve(players: pd.DataFrame, output_dir: Path) -> None:
    all_df = players.select_dtypes('number')
    team_dfs = players.groupby('team')[all_df.columns]

    _output_top_3_txt(all_df, players['name'], output_dir)
    _output_results2_csv(all_df, team_dfs, output_dir)
    _output_histograms(all_df, team_dfs, output_dir)
    _output_best_teams_txt(team_dfs, output_dir)