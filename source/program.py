from . import (
    problem_i,
    problem_ii,
    problem_iii,
    problem_iv,
)


def run(from_archives: bool) -> None:
    players_df = problem_i.scrape_premier_league_players(from_archives)
    problem_i.solve(players_df)
    problem_ii.solve(players_df)
    problem_iii.solve(players_df)
    
    transfer_values = problem_iv.scrape_players_transfer_values(players_df, from_archives)
    problem_iv.solve(players_df, transfer_values)