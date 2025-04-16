from pathlib import Path

from source import (
    problem_i,
    problem_ii,
    # problem_iii,
    # problem_iv
) 

def main() -> None:
    output_dir = Path.cwd() / 'output'
    output_dir.mkdir(exist_ok=True)
    print(f'Output To {output_dir}')

    print('Problem I:')

    players = problem_i.get_premier_league_players()
    players.to_csv(output_dir / 'results.csv', na_rep='N/a', encoding='utf-8')
    print('Output results.csv')

    print('\nProblem II:')

    highest3_lowest3 = problem_ii.find_highest3_lowest3(players)
    with open(output_dir / 'top_3.txt', 'w', encoding='utf-8') as txt:
        txt.write(highest3_lowest3.to_string(na_rep='N/a'))
    print('Output top_3.txt')

    # results2 = problem_ii.find_median_mean_standard_attrs(players)
    # results2.to_csv(output_dir / 'results2.csv', na_rep='N/a', encoding='utf-8')
    # print('Output results2.csv')

    # print('\nProblem III:')


    # print('\nProblem IV:')    

if __name__ == '__main__':
    main()