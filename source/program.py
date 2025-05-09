from . import (
    task_i,
    task_ii,
    task_iii,
    task_iv,
)


def run(from_archives: bool) -> None:
    players_df = task_i.scrape_premier_league_players(from_archives)
    task_i.solve(players_df)
    task_ii.solve(players_df)
    task_iii.solve(players_df)
    
    transfer_values_df = task_iv.scrape_players_transfer_values(players_df, from_archives)
    task_iv.solve(players_df, transfer_values_df)