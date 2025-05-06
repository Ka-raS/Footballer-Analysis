from pathlib import Path

import numpy as np
import numpy.typing as npt
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


III_DIR = Path('output/problem_iii')

def process_data(players_df: pd.DataFrame) -> npt.NDArray[np.number]:
    df = players_df.select_dtypes('number')
    df = df.fillna(0)
    scaled = StandardScaler().fit_transform(df)
    return scaled

# Problem III.1

GAP_REF_COUNT = 10

def find_gap(X: np.ndarray, kmeans: KMeans) -> float:
    inertia = kmeans.inertia_
    inertia_refs = []

    for _ in range(GAP_REF_COUNT):
        random_X = np.random.uniform(low=X.min(axis=0), high=X.max(axis=0), size=X.shape)
        kmeans.fit(random_X)
        inertia_refs.append(kmeans.inertia_)

    gap = np.log(np.mean(inertia_refs)) - np.log(inertia)
    return gap

def plot_clusters_evaluation_graphs(X: npt.NDArray[np.number]) -> plt.Figure:
    """plot 3 graphs:
    - Inertias Elbow
    - Silhouette Scores
    - Gap Statistics
    """
    k_values = range(2, 21)
    inertias = []  
    scores = []  
    gaps = [] 

    for k in k_values:
        kmeans = KMeans(k, random_state=37).fit(X)
        inertias.append(kmeans.inertia_)
        scores.append(silhouette_score(X, kmeans.labels_))
        gaps.append(find_gap(X, kmeans))
    
    # plot graphs
    fig, axes = plt.subplots(1, 3, figsize=(16, 9))
    xticks = k_values[::2]

    evals = [inertias, scores, gaps]
    ylabels = ['ineria', 'score', 'gap']
    titles = ['inertias elbow method', 'silhouette scores method', 'gap statistics method']

    for ax, eval, ylabel, title in zip(axes, evals, ylabels, titles):
        ax: plt.Axes
        ax.plot(k_values, eval, marker='.', color='black')

        ax.set_title(title)
        ax.set_xticks(xticks)
        ax.set_xlabel('n clusters')
        ax.set_ylabel(ylabel)
        for ax, eval in zip(axes, evals):
            ax.plot() 

    fig.tight_layout()
    return fig

# Problem III.2

N_CLUSTERS_OPTIMAL = 3

def grouping_players(X: npt.NDArray[np.number], names: npt.NDArray[np.str_]) -> pd.DataFrame:
    """param 'names' is 1 dimention"""
    kmeans = KMeans(N_CLUSTERS_OPTIMAL, random_state=37)
    clusters = kmeans.fit_predict(X)
    return pd.DataFrame({
        'name': names, 
        'cluster': clusters
    })

# Problem III.3

def scatter_clusters_2d(X: npt.NDArray[np.number], clusters: npt.NDArray[np.int_]) -> plt.Figure:
    """param 'clusters' is 1 dimention"""
    fig = plt.figure(figsize=(16, 9))
    pca = PCA(2).fit_transform(X)

    plt.scatter(pca[:, 0], pca[:, 1], c=clusters)
    plt.title('2D cluster of the data points')
    plt.tight_layout()
    return fig


def solve(players_df: pd.DataFrame) -> None: 
    X = process_data(players_df)

    graphs = plot_clusters_evaluation_graphs(X)
    graphs.savefig(III_DIR / 'clusters_evaluation.svg')
    print('Output clusters_evaluation.svg')

    groups = grouping_players(X, players_df['name'].to_numpy())
    groups.to_csv(III_DIR / 'player_groups.csv')
    print('Output player_groups.csv')

    pca_2d = scatter_clusters_2d(X, groups['cluster'].to_numpy())
    pca_2d.savefig(III_DIR / 'pca_clusters_2d.svg')
    print('Output pca_clusters_2d.svg')

    plt.close('all')