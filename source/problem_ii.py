import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
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
            else names.loc[i]
            for i, data in players6.items()
        ]

    numeric_df = players_df.select_dtypes('number')
    result = numeric_df.apply(find_6players).T
    result.columns = ['top 1', 'top 2', 'top 3', 'bottom 1', 'bottom 2', 'bottom 3']
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


def _make_histograms_figure(df: pd.DataFrame) -> plt.Figure:
    # len(HIST_STATS) = 6
    rows = 2
    cols = 3

    for i, (stat, data) in enumerate(df.items(), start=1):
        plt.subplot(rows, cols, i)
        plt.hist(data)
        plt.title(stat)

    return plt.gcf()

def plot_stats_histograms(players_df: pd.DataFrame) -> list[tuple[str, plt.Figure]]:
    """return list of (team name, figure)
    - each figure is for a team (first figure is all team combined)
    - in figure: histograms for each stat
    """
    result: list[tuple[str, plt.Figure]] = []
    all_player = _make_histograms_figure(players_df[HIST_STATS])
    result.append(('All', all_player))

    for team, df in players_df.groupby('team'):
        figure = _make_histograms_figure(df[HIST_STATS])
        result.append((team, figure))
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