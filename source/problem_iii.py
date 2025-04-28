import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


N_CLUSTERS_OPTIMAL = 8


def normalize_data(players_df: pd.DataFrame) -> np.ndarray:
    df = players_df.select_dtypes(include='number')
    df.fillna(0, inplace=True)
    X = StandardScaler().fit_transform(df)
    return X


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

def plot_clusters_evaluation_graphs(X: np.ndarray) -> None:
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
        kmeans = KMeans(k, random_state=42).fit(X)
        inertias.append(kmeans.inertia_)
        scores.append(silhouette_score(X, kmeans.labels_))
        gaps.append(_find_gap(X, kmeans))

    # plot graphs
    figure, axes = plt.subplots(1, 3, figsize=(18, 9), sharex=True)
    titles = [
        'Inertias Elbow Method', 
        'Silhouette Scores Method', 
        'Gap Statistics Method'
    ]
    evals = [inertias, scores, gaps]
    ylabels = ['Ineria', 'Score', 'Gap']
    xticks = k_values[::2]

    axe: plt.Axes
    for axe, title, evals, ylabel in zip(axes, titles, evals, ylabels):
        axe.plot(k_values, evals, marker='.', color='white')

        axe.set_title(title, color='white')
        axe.set_xlabel('N Clusters', color='white')
        axe.set_ylabel(ylabel, color='white')
        axe.set_xticks(xticks)
        axe.tick_params(colors='white')
        axe.set_facecolor('black')
        for side in ['bottom', 'left']:
            axe.spines[side].set_color('white')

    figure.set_facecolor('black')
    figure.tight_layout()
    return figure


def grouping_players(X: np.ndarray, names: pd.Series) -> pd.DataFrame:
    kmeans = KMeans(N_CLUSTERS_OPTIMAL, random_state=42)
    clusters = kmeans.fit_predict(X)
    return pd.DataFrame({
        'Name': names, 
        'Cluster': clusters
    })


def find_clusters_2d(X: np.ndarray) -> plt.Figure:
    pca = PCA(2)
    result = pca.fit_transform(X)
    figure, axe = plt.subplots(figsize=(18, 9))
    axe.scatter(result[:, 0], result[:, 1])
    figure.tight_layout()
    return figure
