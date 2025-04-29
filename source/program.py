from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from . import (
    problem_i,
    problem_ii,
    problem_iii,
    # problem_iv,
)


OUTPUT_DIR = Path('output')
I_DIR = OUTPUT_DIR / 'problem_i'
II_DIR = OUTPUT_DIR / 'problem_ii'
III_DIR = OUTPUT_DIR / 'problem_iii'
IV_DIR = OUTPUT_DIR / 'problem_iv'
HISTS_DIR = II_DIR / 'histograms'


def _solve_problem_i(players_df: pd.DataFrame) -> None:
    players_df.to_csv(I_DIR / 'results.csv', na_rep='N/a', encoding='utf-8')
    print('Output results.csv')

def _solve_problem_ii(players_df: pd.DataFrame) -> None:
    print('Finding The Top 3 And Bottom 3 For Each Statistic...')
    top_3 = problem_ii.find_top3_bottom3(players_df)
    with open(II_DIR / 'top_3.txt', 'w', encoding='utf-8') as txt:
        txt.write(top_3.to_string(na_rep='N/a'))
    print('Output top_3.txt')

    print('Finding Teams Mean, Median And Std For Each Statistic...')
    teams_values = problem_ii.find_teams_mean_median_std(players_df)
    teams_values.to_csv(II_DIR / 'results2.csv', na_rep='N/a', encoding='utf-8')
    print('Output results2.csv')

    print('Plotting Teams Histograms For Each Statistic...')
    for stat, figure in problem_ii.plot_teams_histograms(players_df):
        figure.savefig(HISTS_DIR / f'{stat}.svg')
    print('Output histograms/*svg')

    print('Finding The Best Teams For Each Statistic And The Best Preforming Team...')
    best_teams_df = problem_ii.find_best_teams(players_df)
    best_teams_df.to_csv(II_DIR / 'best_teams.csv', na_rep='N/a', encoding='utf-8')
    print('Output best_teams.csv')

    best_team = best_teams_df.iloc[-1]['team']
    print(f'The Best Performing Team Is {best_team}')

    plt.close('all')

def _solve_problem_iii(players_df: pd.DataFrame) -> None: 
    X = problem_iii.normalize_data(players_df)

    print('Plotting Clusters Evaluation Graphs...')
    graphs = problem_iii.plot_clusters_evaluation_graphs(X)
    graphs.savefig(III_DIR / 'clusters_evaluation.svg')
    print('Output clusters_evaluation.svg')

    print('Grouping Players To N Clusters...')
    player_groups = problem_iii.grouping_players(X, players_df['name'])
    player_groups.to_csv(III_DIR / 'player_groups.csv')
    print('Output player_groups.csv')
    
    print('Plotting 2D Cluster Of The Data Points...')
    clusters_2d = problem_iii.find_clusters_2d(X)
    clusters_2d.savefig(III_DIR / 'clusters_2d.svg')
    print('Output clusters_2d.svg')

    plt.close('all')

def _solve_problem_iv(players_df: pd.DataFrame) -> None: ...

def run() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    I_DIR.mkdir(exist_ok=True)
    II_DIR.mkdir(exist_ok=True)
    III_DIR.mkdir(exist_ok=True)
    IV_DIR.mkdir(exist_ok=True)
    HISTS_DIR.mkdir(exist_ok=True)

    print('Problem I:')
    print('Scraping Premier League Players...')
    players_df = problem_i.get_premier_league_players()
    _solve_problem_i(players_df)

    print('\nProblem II:')
    _solve_problem_ii(players_df)

    print('\nProblem III:')
    _solve_problem_iii(players_df)
    
    print('\nProblem IV:')
    # _solve_problem_iv(players_df)

    print('Program Completed Successfully')