from pathlib import Path
 
from source import (
    problem_i,
    problem_ii,
    # problem_iii,
    # problem_iv
) 


def main() -> None:
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    print('Problem I:')
    players = problem_i.get_premier_league_players()
    problem_i.solve(players, output_dir)

    print('\nProblem II:')
    problem_ii.solve(players, output_dir)

    # problem_iii.solve(players, output_dir)
    
    # problem_iv.solve(players, output_dir)

if __name__ == '__main__':
    main()