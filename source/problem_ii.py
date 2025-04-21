import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def find_highest3_lowest3(players: pd.DataFrame) -> pd.DataFrame:
    """return DataFrame: 
    - each row is a data-stat
    - 1st column: data-stat names
    - 2nd-7th column: (player name + data) of 3 highests and 3 lowests
    - skip non numeric data-stats (name, team, nationality...) 
    """
    print('Finding The 3 Highest And 3 Lowest Players Of Each Data-Stat...')
    
    # list[6 players of each data-stat]
    result: list[list[str | None]] = []
    names = players['name']
    numeric_data_stats = players.select_dtypes('number').columns

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

def find_median_mean_standard_each_teams(players: pd.DataFrame) -> pd.DataFrame:
    """return DataFrame:
    - each row is a team (1st row is all team)
    - 1st column: team names
    - 2nd-nth columns: mean1, median1, std1...mean_n, median_n, std_n (for n data-stats)
    - skip non numeric data-stat (name, team, nationality...)
    """
    print('Finding Median, Mean, Standard Of Each Statistic And Team...')

    # result[i] = [team i, median1, mean1, std1...median_n, mean_n, std_n]
    result: list[list[float, str]] = []
    # all + each team
    team_data_frames = [('all', players)] + list(players.groupby('team'))
    numeric_data_stats = players.select_dtypes('number').columns

    for team, data_frame in team_data_frames:
        team_data: list[str | float] = [team]
        for data_stat in numeric_data_stats:
            column = data_frame[data_stat]
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

def plot_histograms_each_stats_and_teams(players: pd.DataFrame) -> plt.Figure:
    """return Figure of subplots:
    - each row is a team (1st row is all team)
    - each column is a data-stat
    """
    print('Plotting Histogram Of Each Statistic And Each Team...')

    # all + each team
    team_data_frames = [('all', players)] + list(players.groupby('team'))
    numeric_data_stats = players.select_dtypes('number').columns

    ax: plt.Axes
    axes: np.ndarray
    fig, axes = plt.subplots(len(team_data_frames), len(numeric_data_stats))
    configs = {
        # 'color': 'black'
        # 'edgecolor': 'white'
    }

    for row, (_, data_frame) in enumerate(team_data_frames):
        for col, data_stat in enumerate(numeric_data_stats):
            ax = axes[row, col]
            ax.hist(data_frame[data_stat], **configs)

    # subplots column indices
    for ax, data_stat in zip(axes[0, :], numeric_data_stats):
        ax.set_title(data_stat)
    # subplots row indices
    for ax, (team, _) in zip(axes[:, 0], team_data_frames):
        ax.set_ylabel(team)

    return fig