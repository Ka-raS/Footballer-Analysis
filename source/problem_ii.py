import pandas
import numpy

def find_highest3_lowest3(players: pandas.DataFrame) -> pandas.DataFrame:
    """Return DataFrame: 
    - index=stat_ids (players.columns)
    - columns=['1st highest', '2nd highest', '3rd highest', '1st lowest', '2nd lowest', '3rd lowest']
    - each row is 6 player: name - stat
    - row = numpy.nan if players_column.dtype == object
    """

    print('Finding The 3 Highest And 3 Lowest Players Of Each Statistic...')
    
    # list[[name - stat] * 6]
    result: list[list[str | float]] = []
    names = players['name']
    columns = ['1st highest', '2nd highest', '3rd highest', '1st lowest', '2nd lowest', '3rd lowest']

    for stat_id, stats_column in players.items():
        if stats_column.dtype == object:
            result.append([numpy.nan] * 6)
            continue

        stats = list(stats_column.nlargest(3).items()) + list(stats_column.nsmallest(3).items())
        result.append([
            f'{names.loc[i]} - {stat}' if stat is not numpy.nan
            else numpy.nan
            for i, stat in stats
        ])

    return pandas.DataFrame(result, index=players.columns, columns=columns)

def find_median_mean_standard_attrs(players: pandas.DataFrame) -> pandas.DataFrame:
    pass