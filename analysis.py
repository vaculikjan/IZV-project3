#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import sys
import io
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

# Ukol 1: nacteni dat
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    if not os.path.exists(filename):
        print("{} is an invalid path to a file.".format(filename), file=sys.stderr)
        return
    df = pd.read_pickle(filename)

    if verbose is True:
        buf = io.StringIO()
        df.info(buf=buf, memory_usage = "deep")
        info = buf.getvalue()
        print("orig_size=" + info.split('\n')[-2].split(': ')[1])
    

    for column in df:
        try: 
            df[column] = df[column].astype(np.int64)
        except:
            try:
                df[column] = df[column].astype(np.float32)
            except:
                try:
                    df[column] = df[column].astype("category")
                except:
                    pass

    df["date"] = pd.to_datetime(df["p2a"]).astype('datetime64[ns]')
    
    if verbose is True:
        buf = io.StringIO()
        df.info(buf=buf, memory_usage = "deep")
        info = buf.getvalue()
        print("new_size=" + info.split('\n')[-2].split(': ')[1])

    return df

# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    df = df.melt(value_vars = ["date"], id_vars = ["region", "p13a", "p13b",  "p13c", "p1"])

    region_df = pd.DataFrame()
    
    for region in df["region"].unique().tolist():
        region_df[region] = df.loc[df["region"] == region].agg({"p13a" : "sum", "p13b" : "sum", "p13c" : "sum", "p1" :"size"})

    plt.style.use('fivethirtyeight')
    _, axes = plt.subplots(nrows=4, ncols=1, figsize=(6,8), constrained_layout = True)

    for row in axes:
        row.tick_params(axis='x', labelsize = 7)
        row.tick_params(axis='y', labelsize = 7)


    region_df = region_df.sort_values(by = "p13a", axis = 1, ascending = False)
    region_df.iloc[0].plot(kind="bar", ax=axes[0])
    axes[0].set_title("Úmrtí", fontsize = 11)

    region_df = region_df.sort_values(by = "p13b", axis = 1, ascending = False)
    region_df.iloc[1].plot(kind="bar", ax=axes[1])
    axes[1].set_title("Těžká zranění", fontsize = 11)

    region_df = region_df.sort_values(by = "p13c", axis = 1, ascending = False)
    region_df.iloc[2].plot(kind="bar", ax=axes[2])
    axes[2].set_title("Lehká zranění", fontsize = 11)

    region_df = region_df.sort_values(by = "p1", axis = 1, ascending = False)
    region_df.iloc[3].plot(kind="bar", ax=axes[3])
    axes[3].set_title("Celkový počet nehod", fontsize = 11)

    if fig_location is not None:
        plt.savefig(fig_location)
    
    if show_figure:
        plt.show()
    
# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    
    df["p53"] = (df["p53"]/10).astype(np.int64)

    df = df.melt(value_vars = ["p1"], id_vars = ["p12", "p53", "region"])
    df["cause"] = pd.cut(df["p12"], [np.NINF, 200,300,400,500,600,700], labels=["nezaviněná řidičem", 
                                                                                "nepřiměřená rychlost jízdy", 
                                                                                "nesprávné předjíždění", 
                                                                                "nedání přednosti v jízdě", 
                                                                                "nesprávný způsob jízdy", 
                                                                                "technická závada vozidla"])

    df["damage"] = pd.cut(df["p53"], [np.NINF, 49, 199, 499, 999, np.inf])
    
    print(df)
    
    df_agg = pd.DataFrame()

    for price in df["damage"].unique().tolist():
        for cause in df["cause"].unique().tolist():
            count = df.loc[df["damage"] == price].loc[df["cause"] == cause].loc[df["region"] == "PHA"].agg({"damage" : "count"})[0]
            df_agg = df_agg.append({"damage" : price, "cause" : cause, "count" : count, "region" : "PHA"}, ignore_index=True)

            count = df.loc[df["damage"] == price].loc[df["cause"] == cause].loc[df["region"] == "JHM"].agg({"damage" : "count"})[0]
            df_agg = df_agg.append({"damage" : price, "cause" : cause, "count" : count, "region" : "JHM"}, ignore_index=True)

            count = df.loc[df["damage"] == price].loc[df["cause"] == cause].loc[df["region"] == "OLK"].agg({"damage" : "count"})[0]
            df_agg = df_agg.append({"damage" : price, "cause" : cause, "count" : count, "region" : "OLK"}, ignore_index=True)

            count = df.loc[df["damage"] == price].loc[df["cause"] == cause].loc[df["region"] == "LBK"].agg({"damage" : "count"})[0]
            df_agg = df_agg.append({"damage" : price, "cause" : cause, "count" : count, "region" : "LBK"}, ignore_index=True)
    
    df_agg["count"] = df_agg["count"].astype(np.int64)

    
    
    fig, ax = plt.subplots(nrows = 2, ncols=3, figsize=(11,6), constrained_layout = True)
    
    sns.set_theme(style = "whitegrid")
    
    sns.barplot(
        data = df_agg.loc[df_agg["region"] == "PHA"].sort_values(by = "damage"),
        x = "damage", y = "count" , hue="cause", ci = "sd", palette="dark", alpha = .6,
        ax=ax[0][0]
    ).set_title("PHA", fontsize = 11)

    sns.barplot(
        data = df_agg.loc[df_agg["region"] == "JHM"].sort_values(by = "damage"),
        x = "damage", y = "count" , hue="cause", ci = "sd", palette="dark", alpha = .6,
        ax=ax[1][0]
    ).set_title("JHM", fontsize = 11)

    sns.barplot(
        data = df_agg.loc[df_agg["region"] == "OLK"].sort_values(by = "damage"),
        x = "damage", y = "count" , hue="cause", ci = "sd", palette="dark", alpha = .6,
        ax=ax[0][1]
    ).set_title("OLK", fontsize = 11)

    sns.barplot(
        data = df_agg.loc[df_agg["region"] == "LBK"].sort_values(by = "damage"),
        x = "damage", y = "count" , hue="cause", ci = "sd", palette="dark", alpha = .6,
        ax=ax[1][1]
    ).set_title("LBK", fontsize = 11)


    for col in ax:
        for row in col:
                row.tick_params(axis='x', labelsize = 8)
                row.tick_params(axis='y', labelsize = 8)
                row.set_yscale("log")
                row.legend().remove()
                row.set(xlabel = "Škoda [sto Kč]", ylabel = "Počet")
                row.set_xticklabels(["< 50", "50 - 200", "200 - 500", "500 - 1000", "> 1000"])

    handles, labels = ax[1][1].get_legend_handles_labels()

    ax[-1, -1].axis('off')
    ax[-2, -1].axis('off')
    
    
    fig.legend(handles, labels, loc = "center left", bbox_to_anchor=(0.7, 0.5))


    if fig_location is not None:
        plt.savefig(fig_location)
    
    if show_figure:
        plt.show()

# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):

    table = df.pivot_table(values="p1", index = ["p16", "date"], aggfunc="count")
    print(table["p1"].sum())


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni
    # funkce.
    df = get_dataframe("accidents.pkl.gz", verbose=True)
    #plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    #plot_damage(df, None, True)
    plot_surface(df, "03_stav.png", True)
