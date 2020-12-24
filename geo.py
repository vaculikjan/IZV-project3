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
    df = df.loc[df["region"] == "JHM"]
    df = df.dropna(subset=['d', 'e'])
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs = "EPSG:5514")
    return gdf

def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):

    gdf = gdf.to_crs("epsg:3857")

    vob = gdf.loc[gdf["p5a"] == 1]
    nob = gdf.loc[gdf["p5a"] == 2]

    fig, ax = plt.subplots(1,2, figsize=(13,8))

    x1, y1, x2, y2 = gdf.geometry.total_bounds
    
    ax[0].set_xlim(x1 + (x2-x1)/5.5, x2)
    ax[0].set_ylim(y1 - (y2-y1)/50, y2)

    ax[1].set_xlim(x1 + (x2-x1)/5.5, x2)
    ax[1].set_ylim(y1 - (y2-y1)/50, y2)

    vob.plot(markersize = 0.5, ax = ax[1]) 
    ctx.add_basemap(ax[1], crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite)

    nob.plot(markersize = 0.5, ax = ax[0], color = "r") 
    ctx.add_basemap(ax[0], crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite)

    for col in ax:
        col.set_xticks([])
        col.set_yticks([])

    ax[0].title.set_text('Nehody mimo obec [JHM]')
    ax[1].title.set_text('Nehody v obci [JHM]')

    plt.tight_layout()
    
    if fig_location is not None:
        plt.savefig(fig_location)
    
    if show_figure:
        plt.show()

def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """



if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)

