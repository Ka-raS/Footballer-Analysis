import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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


# Problem II.1

def find_top3_bottom3(players_df: pd.DataFrame) -> pd.DataFrame:
    """return DataFrame: 
    - 6 columns for top 3 and bottom 3 players
    - each row is a numeric stat
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
    result.reset_index(names='statistic', inplace=True) # current index is stats
    return result

# Problem II.2

def find_teams_mean_median_std(players_df: pd.DataFrame) -> pd.DataFrame:
    """return DataFrame:
    - 3 columns each is a mean, median, std of a numeric stat
    - each row is a team
    - the first row is all team combined
    """
    values = ['median', 'mean', 'std']
    numeric_df = players_df.select_dtypes('number')
    numeric_stats = numeric_df.columns

    # each team medians, means, stds
    teams_values: pd.DataFrame = players_df.groupby('team')[numeric_stats].agg(values)
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
    result.reset_index(names='team', inplace=True) # current index is teams
    return result

# Problem II.3

def make_histograms(df: pd.DataFrame) -> plt.Figure:
    """figure of histograms for each stat"""
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, (stat, data) in zip(axes.flat, df[HIST_STATS].items()):
        ax: plt.Axes
        ax.hist(data, color='black', edgecolor='white')
        ax.set_title(stat)
    fig.tight_layout()
    return fig

# Problem II.4

def find_best_teams(players_df: pd.DataFrame) -> pd.DataFrame:
    """"return DataFrame
    - 2 columns: 'team' and numeric 'statistic'
    - each row is a team name
    - last row is the best team out of all
    """
    numeric_stats = players_df.select_dtypes(include='number').columns
    team_scores = players_df.groupby('team')[numeric_stats].mean()
    for stat in BAD_STATS:
        team_scores[stat] *= -1

    # best teams of each stat
    stat_best_teams = team_scores.idxmax()

    # find best team of all
    essential_stats = list(set(numeric_stats) - set(NEUTRAL_STATS))
    best_team = team_scores[essential_stats].sum(axis='columns').idxmax()
    stat_best_teams['all'] = best_team

    result = pd.DataFrame(stat_best_teams, columns=['team'])
    result.reset_index(names='statistic', inplace=True) # current index is stats
    return result