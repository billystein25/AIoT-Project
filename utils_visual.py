import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


def plot_instance_time_domain(df: pd.DataFrame):
    """Visualizes the movement instance to a plot in time domain.

    Args:
        df: The DataFrame to be visualized in time domain.

    Returns:

    """
    df.plot(figsize=(20, 10), linewidth=2, fontsize=20).legend(fontsize=18)
    plt.xlabel('Sample', fontsize=20)
    plt.ylabel('Axes', fontsize=20)


def plot_instance_3d(
        df: pd.DataFrame,
        axes_list: tuple = ("acc_x", "acc_y", "acc_z")
):
    """Plots a 3-axes DataFrame in 3D graph.

    Args:
        df: The DataFrame to be plotted in 3D.
        axes_list: Tuple with the 3-axis values. For gyroscope axes should
            be: ("gyr_x", "gyr_y", "gyr_z")

    Returns:

    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # print the plot in 3D

    xs = df[axes_list[0]]
    ys = df[axes_list[1]]
    zs = df[axes_list[2]]

    ax.scatter(xs, ys, zs, color='green', s=50, alpha=0.6, edgecolors='w')

    ax.set_xlabel(axes_list[0])
    ax.set_ylabel(axes_list[1])
    ax.set_zlabel(axes_list[2])


def plot_np_instance(
        np_array: np.ndarray,
        columns_list: list
):
    """Plot NumPy instance using DataFrames (pandas). It first transforms the
        array into
    DataFrame with its corresponding columns naming, and then, it plots the
        DataFrame in time domain.

    Args:
        np_array: The NumPy array to be transformed.
        columns_list: The columns list that the DataFrame and the plot will
            have.

    Returns:

    """
    df = pd.DataFrame(np_array, columns=columns_list)
    df.plot(figsize=(20, 10), linewidth=2, fontsize=20)
    plt.xlabel('Sample', fontsize=20)
    plt.ylabel('Axes', fontsize=20)


def plot_heatmap(df: pd.DataFrame):
    """Visualizes the heatmap of the DataFrame's values.

    Args:
        df: A DataFrame.

    Returns:

    """
    plt.figure(figsize=(14, 6))
    sns.heatmap(df, cmap='plasma')


def plot_scatter_pca(
        df: pd.DataFrame,
        c_name: str,
        cmap_set: str = "plasma"
):
    """Visualizes the values of the component columns of the DataFrame
    according to its column that includes the labels.

    Args:
        df: The DataFrame that contains the transformed data after the PCA
            procedure.
        c_name: The name of the column that includes the labels.
        cmap_set: The format of the plot.

    Returns:

    """
    if len(df.columns) == 3:
        plt.style.use('classic')
        plt.figure(figsize=(16, 8))
        plt.scatter(df.iloc[:, 0], df.iloc[:, 1], c=df[c_name], cmap=cmap_set)
        plt.xlabel('First principal component')
        plt.ylabel('Second Principal Component')
    elif len(df.columns) == 4:
        plt.style.use('classic')
        fig = plt.figure(figsize=(16, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2], c=df[c_name], cmap=cmap_set)
        ax.set_xlabel('First principal component')
        ax.set_ylabel('Second Principal Component')
        ax.set_zlabel('Third Principal Component')
    else:
        print("The DataFrame has more than 4 columns.")

def plot_scatter_pca1(
        df: pd.DataFrame,
        c_name: str,
        cmap_set: str = "tab20",
        class_names: list = None
):
    """Visualizes the values of the component columns of the DataFrame
    according to its column that includes the labels.

    Args:
        df: The DataFrame that contains the transformed data after the PCA
            procedure. Must have 2 or 3 component columns plus the label column.
        c_name: The name of the column that includes the labels.
        cmap_set: The colormap to use. Defaults to 'tab20' for distinct colors.
        class_names: Optional list of class name strings for the legend.
            If provided, integer labels are mapped to activity names.

    Returns:

    """
    import matplotlib.cm as cm

    unique_labels = sorted(df[c_name].unique())
    colors = cm.get_cmap(cmap_set)(np.linspace(0, 1, len(unique_labels)))

    if len(df.columns) == 3:
        plt.style.use('classic')
        plt.figure(figsize=(16, 8))
        for label_int, color in zip(unique_labels, colors):
            mask = df[c_name] == label_int
            label_name = class_names[label_int] if class_names is not None else str(label_int)
            plt.scatter(df[mask].iloc[:, 0], df[mask].iloc[:, 1],
                        label=label_name, color=color, alpha=0.5, s=20)
        plt.xlabel('First principal component')
        plt.ylabel('Second Principal Component')
        plt.legend(bbox_to_anchor=(1.05, 1), fontsize=9)
        plt.tight_layout()

    elif len(df.columns) == 4:
        plt.style.use('classic')
        fig = plt.figure(figsize=(16, 8))
        ax = fig.add_subplot(111, projection='3d')
        for label_int, color in zip(unique_labels, colors):
            mask = df[c_name] == label_int
            label_name = class_names[label_int] if class_names is not None else str(label_int)
            ax.scatter(df[mask].iloc[:, 0], df[mask].iloc[:, 1], df[mask].iloc[:, 2],
                       label=label_name, color=color, alpha=0.5, s=20)
        ax.set_xlabel('First principal component')
        ax.set_ylabel('Second Principal Component')
        ax.set_zlabel('Third Principal Component')
        ax.legend(bbox_to_anchor=(1.05, 1), fontsize=9)

    else:
        print("The DataFrame has more than 4 columns.")