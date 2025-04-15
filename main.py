from pathlib import Path

import pandas

from source import (
    constants,
    fbref
) 

def main() -> None:
    # Problem I
    print('Problem I:')

    players = fbref.get_premier_league_players()
    data_frame = pandas.DataFrame(players, columns=constants.STATS)
    data_frame.replace('', 'N/a', inplace=True)

    results_csv = Path.cwd() / 'results.csv'
    data_frame.to_csv(results_csv)
    print(f'Output Players To {results_csv}')

    print('---------')
    # Problem II
    print('Problem II:')

    

if __name__ == '__main__':
    main()