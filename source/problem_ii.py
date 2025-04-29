from collections.abc import Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec


HIST_STATS = [
    'goals_per90', 'assists_per90', 'xg_per90', 'blocks', 'blocked_shots', 'blocked_passes'
]
NEUTRAL_STATS = [
    'age', 'games', 'games_starts', 'minutes', 'fouled'
]
BAD_STATS = [
    'cards_yellow', 'cards_red', 'gk_goals_against_per90', 'challenges_lost',
    'take_ons_tackled_pct', 'miscontrols', 'dispossessed', 'fouls', 'offsides', 'aerials_lost'
]


def find_top3_bottom3(players_df: pd.DataFrame) -> pd.DataFrame:
    """return DataFrame: 
    - 6 columns for top 3 and bottom 3 players
    - each row is a stat
    """
    names = players_df['name']

    def find_6players(series: pd.Series) -> list[str]:
        players6 = pd.concat([series.nlargest(3), series.nsmallest(3)])
        return [
            np.nan if pd.isna(data)
            else f'{names.loc[i]} - {data}'
            for i, data in players6.items()
        ]

    numeric_df = players_df.select_dtypes('number')
    result = numeric_df.apply(find_6players).T
    result.columns = ['top 1st', 'top 2nd', 'top 3rd', 'bottom 1st', 'bottom 2nd', 'bottom 3rd']
    result.reset_index(names='statistic', inplace=True)
    return result


def find_teams_mean_median_std(players_df: pd.DataFrame) -> pd.DataFrame:
    """return DataFrame:
    - 3 columns each is a mean, median, std of a stat
    - each row is a team
    - the first row is all team combined
    """
    values = ['median', 'mean', 'std']
    numeric_df = players_df.select_dtypes('number')
    numeric_stats = numeric_df.columns

    # each team medians, means, stds
    teams_values: pd.DataFrame = players_df.groupby('team', dropna=False)[numeric_stats].agg(values)
    # all team combined medians, means, stds 
    combined_values: pd.Series = numeric_df.agg(values).T.stack(future_stack=True) # .stack(dropna=False)
    combined_values.name = 'All'
    
    # insert combined_values at 1st row of teams_values
    result = pd.concat([pd.DataFrame([combined_values]), teams_values])
    result.columns = [
        f'{value} of {stat}'
        for stat in numeric_stats
            for value in values
    ]
    result.reset_index(names='team', inplace=True)
    return result


def _config_axe(axe: plt.Axes, data: pd.Series, bins: Iterable[float]) -> None:
    axe.hist(data, bins, color='white', edgecolor='black')
    axe.set_facecolor('black')
    for side in ('bottom', 'left'):
        axe.spines[side].set_color('white')
    axe.tick_params(colors='white')

def _make_histograms_figure(combined_data: pd.Series, teams_data: list[str, pd.Series]) -> plt.Figure:
    # 20 teams hists + all hist = 21
    rows = cols = 5
    figure = plt.figure(figsize=(16, 9), facecolor='black')
    grid_spec = gridspec.GridSpec(rows, cols, figure)
    bins = np.histogram_bin_edges(combined_data)

    # combined_data hist in 1st row
    axe_combined = figure.add_subplot(grid_spec[0, cols // 2])
    axe_combined.set_title('All', color='white')
    _config_axe(axe_combined, combined_data, bins)

    # teams_data hists in remain rows
    # skip r = 0
    coords = [
        (r + 1, c)
        for r, c in np.ndindex(rows - 1, cols)
    ]
    is_axe0 = True
    for (r, c), (team, data) in zip(coords, teams_data):
        if is_axe0:
            is_axe0 = False
            axe = axe0 = figure.add_subplot(grid_spec[r, c]) 
        else:
            axe = figure.add_subplot(grid_spec[r, c], sharex=axe0, sharey=axe0)
        axe.set_title(team, color='white')
        _config_axe(axe, data, bins)

    figure.suptitle('x: value, y: frequency', color='white')
    figure.tight_layout()
    return figure

def plot_teams_histograms(players_df: pd.DataFrame) -> list[tuple[str, plt.Figure]]:
    """return list of (stat, figure)
    - each figure is for a stat
    - in figure: multiple histograms for each individual team and all team combined
    """
    result: list[tuple[str, plt.Figure]] = []
    for stat in HIST_STATS:
        combined_data = players_df[stat]
        teams_data = players_df.groupby('team', dropna=False)[stat]
        figure = _make_histograms_figure(combined_data, teams_data)
        result.append((stat, figure))
    return result


def find_best_teams(players_df: pd.DataFrame) -> pd.DataFrame:
    """"return DataFrame
    - 2 columns: 'team' and 'statistic'
    - each row is a team name
    - last row is the best team out of all
    """
    numeric_stats = players_df.select_dtypes(include='number').columns
    team_scores = players_df.groupby('team', dropna=False)[numeric_stats].mean()
    for stat in BAD_STATS:
        team_scores[stat] *= -1

    # best teams of each stat
    stat_best_teams = team_scores.idxmax()

    # find best team of all
    essential_stats = list(set(numeric_stats) - set(NEUTRAL_STATS))
    best_team = team_scores[essential_stats].sum(axis='columns').idxmax()
    stat_best_teams['all'] = best_team

    result = pd.DataFrame(stat_best_teams, columns=['team'])
    result.reset_index(names='statistic', inplace=True)
    return result