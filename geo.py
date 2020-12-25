#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzeze pridat vlastni knihovny


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:

    """Take Pandas DataFrame and return GeoDataFrame."""

    df = df.loc[df["region"] == "JHM"]
    df = df.dropna(subset=['d', 'e'])

    gdf = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(
            df["d"],
            df["e"]),
        crs="EPSG:5514")

    return gdf


def plot_geo(
        gdf: geopandas.GeoDataFrame,
        fig_location: str = None,
        show_figure: bool = False):

    """Plot geographical data of accidents in a chosen region (JHM).

    Keyword arguments:
    gdf -- GeoDataFrame with data needed for plotting
    fig_location -- location saying where to store the plotted figure
    show_figure -- whether the plotted figure is shown
    """

    # change crs to get a less blurry map
    gdf = gdf.to_crs("epsg:3857")

    # prep 2 geo data frames for 2 subplots
    vob = gdf.loc[gdf["p5a"] == 1]
    nob = gdf.loc[gdf["p5a"] == 2]

    # plotting
    _, ax = plt.subplots(1, 2, figsize=(13, 8))

    # setting boundaries for subplots to be the same for a prettier result
    x1, y1, x2, y2 = gdf.geometry.total_bounds

    ax[0].set_xlim(x1 + (x2-x1)/5.5, x2)
    ax[0].set_ylim(y1 - (y2-y1)/50, y2)

    ax[1].set_xlim(x1 + (x2-x1)/5.5, x2)
    ax[1].set_ylim(y1 - (y2-y1)/50, y2)

    # creating subplots and setting params for them
    vob.plot(markersize=0.5, ax=ax[1])
    ctx.add_basemap(
        ax[1],
        crs=gdf.crs.to_string(),
        source=ctx.providers.Stamen.TonerLite)

    nob.plot(markersize=0.5, ax=ax[0], color="r")
    ctx.add_basemap(
        ax[0],
        crs=gdf.crs.to_string(),
        source=ctx.providers.Stamen.TonerLite)

    for col in ax:
        col.set_xticks([])
        col.set_yticks([])

    ax[0].title.set_text('Nehody mimo obec [JHM]')
    ax[1].title.set_text('Nehody v obci [JHM]')

    plt.tight_layout()

    # checking whather to save and show the plot
    if fig_location is not None:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


def plot_cluster(
        gdf: geopandas.GeoDataFrame,
        fig_location: str = None,
        show_figure: bool = False):

    """Plot clustered accident data.

    Keyword arguments:
    gdf -- GeoDataFrame with data needed for plotting
    fig_location -- location saying where to store the plotted figure
    show_figure -- whether the plotted figure is shown"""

    # drop one accident that is far outside of the region
    # and is messing with clustering
    gdf = gdf.drop(gdf[gdf.geometry.x < -700000].index)
    gdf = gdf.to_crs("epsg:3857")

    # cluster accident data
    coords = np.dstack([gdf.geometry.x, gdf.geometry.y]).reshape(-1, 2)
    model = sklearn.cluster.MiniBatchKMeans(n_clusters=20).fit(coords)

    # add column to identify clusters
    gdf_clstrd = gdf.copy()
    gdf_clstrd["cluster"] = model.labels_

    # aggregate to get count of accidents in each cluster
    gdf_clstrd = gdf_clstrd.dissolve(
        by="cluster",
        aggfunc={"p1": "count"}).rename(columns={"p1": "cnt"})

    # get center points from cluster polygons
    gdf_coords = geopandas.GeoDataFrame(
        geometry=geopandas.points_from_xy(
            model.cluster_centers_[:, 0],
            model.cluster_centers_[:, 1]))
    gdf_clstrd = gdf_clstrd.merge(
        gdf_coords,
        left_on="cluster",
        right_index=True).set_geometry("geometry_y")

    # plotting
    plt.figure(figsize=(13, 8))
    ax = plt.gca()

    # 2 plots; first one for clusters and second one for all accidents

    gdf.plot(ax=ax, color="grey", markersize=0.1)
    gdf_clstrd.plot(
        ax=ax,
        markersize=gdf_clstrd["cnt"] / 10,
        column="cnt",
        alpha=0.6,
        legend=True)

    # add map
    ctx.add_basemap(
        ax,
        crs=gdf.crs.to_string(),
        source=ctx.providers.Stamen.TonerLite)

    # set params for the plot
    ax.set_xticks([])
    ax.set_yticks([])
    ax.title.set_text('Nehody v JHM kraji')
    plt.tight_layout()

    # checking whather to save and show the plot
    if fig_location is not None:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    # plot_geo(gdf, "geo1.png", True)
    # plot_cluster(gdf, "geo2.png", True)
