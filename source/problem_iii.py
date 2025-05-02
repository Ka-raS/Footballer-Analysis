import numpy as np
import numpy.typing as npt
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


N_CLUSTERS_OPTIMAL = 8

def process_data(players_df: pd.DataFrame) -> npt.NDArray[np.number]:
    df = players_df.select_dtypes('number').fillna(0)
    scaled = StandardScaler().fit_transform(df)
    return scaled

def _find_gap(X: np.ndarray, kmeans: KMeans) -> float:
    inertia = kmeans.inertia_
    ref_count = 10
    inertia_refs = []

    for _ in range(ref_count):
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
    inertias = [] # inertias elbow 
    scores = [] # silhouette scores 
    gaps = [] # gap statistics 

    for k in k_values:
        kmeans = KMeans(k, random_state=37).fit(X)
        inertias.append(kmeans.inertia_)
        scores.append(silhouette_score(X, kmeans.labels_))
        gaps.append(_find_gap(X, kmeans))

    # plot graphs
    fig, axes = plt.subplots(1, 3, figsize=(16, 9))
    xticks = k_values[::2]

    evals = (inertias, scores, gaps)
    ylabels = ('ineria', 'score', 'gap')
    titles = (
        'inertias elbow method', 
        'silhouette scores method', 
        'gap statistics method'
    )

    for ax, eval, ylabel, title in zip(axes, evals, ylabels, titles):
        ax: plt.Axes
        ax.plot(k_values, eval, marker='.', color='black')

        ax.set_title(title)
        ax.set_xticks(xticks)
        ax.set_xlabel('n clusters')
        ax.set_ylabel(ylabel)

    fig.tight_layout()
    return fig

def grouping_players(X: npt.NDArray[np.number], names: npt.NDArray[np.str_]) -> pd.DataFrame:
    """param 'names' is 1 dimention"""
    kmeans = KMeans(N_CLUSTERS_OPTIMAL, random_state=37)
    clusters = kmeans.fit_predict(X)
    return pd.DataFrame({
        'name': names, 
        'cluster': clusters
    })

def scatter_clusters_2d(X: npt.NDArray[np.number], clusters: npt.NDArray[np.int_]) -> plt.Figure:
    """param 'clusters' is 1 dimention"""
    fig = plt.figure(figsize=(16, 9))
    pca = PCA(2).fit_transform(X)

    plt.scatter(pca[:, 0], pca[:, 1], c=clusters)
    plt.title('2D cluster of the data points')
    plt.tight_layout()
    return fig
