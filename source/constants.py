# dict[table id, list[stat id]]
TABLES_STATS = {
    'stats_standard_9': [
        'nationality',
        'position',
        'age', 
        'games',
        'games_starts',
        'minutes',
        'goals',
        'assists',
        'cards_yellow',
        'cards_red',
        'xg',
        'xg_assist',
        'progressive_carries',
        'progressive_passes',
        'progressive_passes_received',
        'goals_per90',
        'assists_per90',
        'xg_per90',
        'xg_assist_per90'
    ],
    'stats_keeper_9': [
        'gk_goals_against_per90',
        'gk_save_pct',
        'gk_clean_sheets_pct',
        'gk_pens_save_pct'
    ],
    'stats_shooting_9': [
        'shots_on_target_pct',
        'shots_on_target_per90',
        'goals_per_shot',
        'average_shot_distance'
    ],
    'stats_passing_9': [
        'passes_completed',
        'passes_pct',
        'passes_total_distance',
        'passes_pct_short',
        'passes_pct_medium',
        'passes_pct_long',
        'assisted_shots',
        'passes_into_final_third',
        'passes_into_penalty_area',
        'crosses_into_penalty_area',
        'progressive_passes'
    ],
    'stats_gca_9': [
        'sca',
        'sca_per90',
        'gca',
        'gca_per90'
    ],
    'stats_defense_9': [
        'tackles',
        'tackles_won',
        'challenges',
        'challenges_lost',
        'blocks',
        'blocked_shots',
        'blocked_passes',
        'interceptions'
    ],
    'stats_possession_9': [
        'touches',
        'touches_def_pen_area',
        'touches_def_3rd',
        'touches_mid_3rd',
        'touches_att_3rd',
        'touches_att_pen_area',
        'take_ons',
        'take_ons_won_pct',
        'take_ons_tackled_pct',
        'carries',
        'carries_progressive_distance',
        'progressive_carries',
        'carries_into_final_third',
        'carries_into_penalty_area',
        'miscontrols',
        'dispossessed',
        'passes_received',
        'progressive_passes_received'
    ],
    'stats_misc_9': [
        'fouls',
        'fouled',
        'offsides',
        'crosses',
        'ball_recoveries',
        'aerials_won',
        'aerials_lost',
        'aerials_won_pct'
    ],
}

STATS = ['name', 'team'] + [
    stat_id
    for stat_list in TABLES_STATS.values()
        for stat_id in stat_list
]