from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, power_transform
from sklearn.metrics import (
    silhouette_score, 
    calinski_harabasz_score, 
    davies_bouldin_score
)


III_DIR = Path('output/problem_iii')

# Problem III.1

GK_STATS = [
    'gk_goals_against_per90', 'gk_save_pct', 'gk_clean_sheets_pct', 'gk_pens_save_pct'
]

def process_data(players_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]: 
    """fillna, yeo-johnson unskew, standardize
        return processed data and skewness before unskewing
    """

    df = players_df.copy()

    # fillna mean for goal keepers' goal keeper stats
    df.loc[df['position'] == 'GK', GK_STATS].fillna(df[GK_STATS].mean(), inplace=True)
    df = players_df.select_dtypes('number')

    # fillna 0 for outfielder's goal keeper stats
    df[GK_STATS] = df[GK_STATS].fillna(0)
    df = df.fillna(df.mean())
    skew_before = df.skew()

    data = power_transform(df, method='yeo-johnson') # unskew
    data = StandardScaler().fit_transform(data)
    return pd.DataFrame(data, columns=df.columns), skew_before

# Problem III.2

def plot_clusters_evaluation_graphs(X: pd.DataFrame) -> plt.Figure:
    """plot 3 graphs:
    - Inertias Elbow
    - Silhouette Scores
    - Gap Statistics
    """
    k_values = range(2, 21)
    inertias = []  
    silhouettes = []  
    harabaszs = [] 
    bouldins = []

    for k in k_values:
        kmeans = KMeans(k, random_state=37).fit(X)
        inertias.append(kmeans.inertia_)
        silhouettes.append(silhouette_score(X, kmeans.labels_))
        harabaszs.append(calinski_harabasz_score(X, kmeans.labels_))
        bouldins.append(davies_bouldin_score(X, kmeans.labels_))
    
    # plot graphs
    fig, axes = plt.subplots(2, 2, figsize=(16, 9))

    evals = [inertias, silhouettes, harabaszs, bouldins]
    ylabels = ['ineria', 'score', 'score', 'score']
    titles = [
        'Inertias Elbow Method', 'Silhouette Scores Method', 
        'Calinski Harabasz Score Method', 'Davies Bouldin Score Method'
    ]

    for ax, eval, ylabel, title in zip(axes.flat, evals, ylabels, titles):
        ax: plt.Axes
        ax.plot(k_values, eval, marker='.', color='black')
        ax.set_title(title)
        ax.set_xticks(k_values)
        ax.set_xlabel('n clusters')
        ax.set_ylabel(ylabel)

    fig.suptitle('Clusters Evaluation')
    fig.tight_layout()
    return fig

# Problem III.3

N_CLUSTERS_OPTIMAL = 4

def grouping_players(X: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    kmeans = KMeans(N_CLUSTERS_OPTIMAL, random_state=37)
    clusters = kmeans.fit_predict(X)
    centers_df = pd.DataFrame(kmeans.cluster_centers_, columns=X.columns)
    return clusters, centers_df

def scatter_pca_clusters_2d(X: pd.DataFrame, clusters: np.ndarray, centers_df: pd.DataFrame) -> plt.Figure:
    pca = PCA(2)
    X_pca = pca.fit_transform(X)
    centers_pca = pca.transform(centers_df)

    plt.figure(figsize=(16, 9))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='tab10', s=100)
    plt.scatter(centers_pca[:, 0], centers_pca[:, 1], c='black', s=1000, alpha=0.5)
    plt.title('2D Clusters Of Data Points')
    plt.tight_layout()
    return plt.gcf()


def solve(players_df: pd.DataFrame) -> None: 
    III_DIR.mkdir(parents=True, exist_ok=True)
    dataset_csv = III_DIR / 'dataset.csv'
    stats_skews_csv = III_DIR / 'stats_skews.csv'
    clusters_evaluation_svg = III_DIR / 'clusters_evaluation.svg'
    player_groups_csv = III_DIR / 'player_groups.csv'
    pca_clusters_2d_svg = III_DIR / 'pca_clusters_2d.svg'
    print('\nProblem III:')

    X, skew_before = process_data(players_df)
    X.to_csv(dataset_csv, encoding='utf-8') # no nan
    print(dataset_csv)

    stats_skews = pd.DataFrame({'skew before': skew_before, 'skew after': X.skew()}).reset_index(names='statistic')
    stats_skews.to_csv(stats_skews_csv, encoding='utf-8')
    print(stats_skews_csv)

    graphs = plot_clusters_evaluation_graphs(X)
    graphs.savefig(clusters_evaluation_svg)
    print(clusters_evaluation_svg)

    clusters, centers_df = grouping_players(X)

    clusters_df = pd.DataFrame({'name': players_df['name'], 'cluster': clusters})
    clusters_df.to_csv(player_groups_csv)
    print(player_groups_csv)

    pca_2d = scatter_pca_clusters_2d(X, clusters, centers_df)
    pca_2d.savefig(pca_clusters_2d_svg)
    print(pca_clusters_2d_svg)

    plt.close('all')