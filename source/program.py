from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from . import (
    problem_i,
    problem_ii,
    problem_iii,
    problem_iv,
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
    top_3 = problem_ii.find_top3_bottom3(players_df)
    with open(II_DIR / 'top_3.txt', 'w', encoding='utf-8') as txt:
        txt.write(top_3.to_string(na_rep='N/a'))
    print('Output top_3.txt')

    teams_values = problem_ii.find_teams_mean_median_std(players_df)
    teams_values.to_csv(II_DIR / 'results2.csv', na_rep='N/a', encoding='utf-8')
    print('Output results2.csv')

    team_dfs = [('All', players_df)] + list(players_df.groupby('team'))
    for team, df in team_dfs:
        fig = problem_ii.make_histograms(df)
        fig.savefig(HISTS_DIR / f'{team}.svg')
        plt.close(fig)
    print('Output histograms/*.svg')

    best_teams_df = problem_ii.find_best_teams(players_df)
    best_teams_df.to_csv(II_DIR / 'best_teams.csv', na_rep='N/a', encoding='utf-8')
    print('Output best_teams.csv')

def _solve_problem_iii(players_df: pd.DataFrame) -> None: 
    X = problem_iii.process_data(players_df)

    graphs = problem_iii.plot_clusters_evaluation_graphs(X)
    graphs.savefig(III_DIR / 'clusters_evaluation.svg')
    print('Output clusters_evaluation.svg')

    groups = problem_iii.grouping_players(X, players_df['name'].to_numpy())
    groups.to_csv(III_DIR / 'player_groups.csv')
    print('Output player_groups.csv')

    pca_2d = problem_iii.scatter_clusters_2d(X, groups['cluster'].to_numpy())
    pca_2d.savefig(III_DIR / 'pca_clusters_2d.svg')
    print('Output pca_clusters_2d.svg')

    plt.close('all')

def _solve_problem_iv(players_df: pd.DataFrame, transfer_values: pd.DataFrame) -> None: 
    features = problem_iv.select_features(players_df, transfer_values)
    
    model = problem_iv.make_transfers_eval_model()
    

def run(from_archives: bool) -> None:
    for dir in [OUTPUT_DIR, I_DIR, II_DIR, III_DIR, IV_DIR, HISTS_DIR]:
        dir.mkdir(exist_ok=True)

    players_df = problem_i.scrape_premier_league_players(from_archives)
    _solve_problem_i(players_df)
    _solve_problem_ii(players_df)
    _solve_problem_iii(players_df)
    
    transfer_values = problem_iv.scrape_players_transfer_values(players_df, from_archives)
    _solve_problem_iv(players_df, transfer_values)