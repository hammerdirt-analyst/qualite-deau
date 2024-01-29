import pandas as pd
import datetime as dt
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO, WeekdayLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

location_markers = {"SVT":"o", "VNX":"s", "MRD":"X"}
location_colors = {"SVT":"dodgerblue", "VNX":"green", "MRD":"red"}

def report_data(data, y: str = None, locations: list = None, categories: list = None, years: list = None):
    mask_year = data["year"].astype("str").isin(years)
    mask_locations = data["location"].isin(locations)
    mask_label = data["label"].isin(categories)
    data['date'] = pd.to_datetime(data['date'])
    data['per/100ml'] = data['count'] * data.coef
    data['fail'] = data[y] > 100
    
    
    return data[(mask_year)].copy()

def format_df_for_display_mean_std(data_frame, category: str = None):
        
    groups = ["location", "date", "label"]
    d = data_frame[[*groups, "mean", "std"]][data_frame["label"] == category]
    s = d[[*groups, "mean", "std"]].copy()
    s["std +"] = s["std"] + s["mean"]
    s["std -"] = s["mean"] - s["std"]
    s["std -"] = s["std -"].where( s["std -"]>=0, 0)
    
    return s

def scatter_plot_with_std(data: pd.DataFrame=None, label: str = None, x: str = None, y_one: str = None, y_two: str = None, y_three: str = None, ax: matplotlib.axes = None, color: str = None, marker: str = None):
    ax.vlines(x=data[x], ymin=data[y_one], ymax=data[y_three], color=color, alpha=.2, linestyle= "-.")
    sns.scatterplot(data = data, x=x, y=y_two, color=color, marker=marker, label=label, ax=ax)
    sns.scatterplot(data = data, x=x, y=y_three, color=color, label="mean + std", marker=7, ax=ax)
    sns.scatterplot(data = data, x=x, y=y_one, color=color,label="mean - std", marker=6, ax=ax)
    
    return ax


def major_and_minor_ticks(ax, date_format):
    loc_major = WeekdayLocator(byweekday=MO, interval=1)
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))  
    ax.xaxis.set_major_locator(loc_major)
    ax.xaxis.set_major_formatter(date_format)
    ax.tick_params(axis='x', labelrotation = 45)
    ax.tick_params(axis='x', which='major', length=8, width=2, color='black')
    
    return ax

def rain_data_format(data, start, end):
    data['date'] = pd.to_datetime(data['date'])
    date_mask = (data["date"] >= start) & (data["date"] <= end)
    new_rd = data[date_mask].copy()
    
    return new_rd

def scatterplot_date_label(data, y, groups, title, project, date_range, date_format,  palette, year, figure_name):
    
    chart_data = data[data.label.isin(palette.keys())].groupby(groups, as_index=False)[y].mean()
    
    fig, ax = plt.subplots()    
    
    ax.axvspan(date_range[0], date_range[1], color="black", alpha=0.2, label="event")
    sns.scatterplot(data = chart_data, x="date", y=y, hue="label", palette=palette)
    
    ax = major_and_minor_ticks(ax, date_format)
    #ax.axvline(x=date_range[0], ymin=0, ymax=1)
    #ax.axvline(x=date_range[1], ymin=0, ymax=1)
    ax.set_ylabel("Colony forming units per 100mL", labelpad=20)
    ax.set_xlabel("")
    
    ax.set_title(f"{project}\n{title}", loc="left")
    ax.legend().set_title('')

    file_name = f"resources/charts/figure_one_{year[0]}.jpg"    

    plt.tight_layout()

    plt.savefig(file_name)

    plt.show()

def scatterplot_date_label_rain(data, rain_data, y,  date_range, date_format, groups, label, title, project, palette, year, figure_name):

    chart_data = data[data.label == label].groupby(groups, as_index=False)[y].mean()
    
    fig, ax= plt.subplots()    
    
    ax2 = ax.twinx()
    
    ax.axvspan(date_range[0], date_range[1], color="black", alpha=0.2, label="event")
    ax.scatter(data = chart_data, x="date", y=y, color="dodgerblue", label=label)
    ax2.bar(data=rain_data, x = "date", height="mm", color="b", alpha=.1, label="rain") 
    
    ax = major_and_minor_ticks(ax, date_format)
    # ax.axvline(x=date_range[0], ymin=0, ymax=1)
    # ax.axvline(x=date_range[1], ymin=0, ymax=1)
    ax.axhline(y=100, xmin=0, xmax=1, ls="--", label="limit", color="black")
    ax.set_ylabel("Colony forming units per 100mL", labelpad=20)
    ax2.set_ylabel("Millimeters of rain")
    ax.set_xlabel("")

    # format legend
    ax2h, ax2l = ax2.get_legend_handles_labels()
    rain_handle = ax2h[:1]
    rain_label = ["rain mm"]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([*handles, *rain_handle], [*labels, *rain_label], loc="upper right")
        
    ax.set_title(f"{project}\n{title}", loc="left")
    
    file_name = f"resources/charts/figure_two_{year[0]}.jpg"    

    plt.tight_layout()

    plt.savefig(file_name)

    plt.show()

def location_summary(data, y):    

    by_location = data.groupby(["location", "date", "label"], as_index=True).agg({y:"mean", "sample":"nunique", "fail":"sum"})
    std_locations = data.groupby(["location", "date", "label"], as_index=True).agg({y:"std"})
    by_location["std"] = by_location.index.map(lambda x: std_locations.loc[x, y ])
    by_location["weight"] = by_location["sample"]/by_location["sample"].sum()
    by_location["mean"] = by_location[y]
    by_location.reset_index(inplace=True, drop=False)
    
    return by_location

def location_summary_charts(data, date_range, date_format, locations, project, title, figure_name, file_name):

    fig, ax = plt.subplots()
    
    # the shaded area of the jazz
    ax.axvspan(date_range[0], date_range[1],  color="black", alpha=.1,  label="event")
    
    # the results from each location
    for site in locations:
        d = format_df_for_display_mean_std(data[data.location == site], category="Bioindicator")
        vars = dict(data=d, label=site, x="date", y_one="std -", y_two="mean", y_three="std +", ax=ax, color=location_colors[site], marker=location_markers[site])
        ax=scatter_plot_with_std(**vars)
      
    ax = major_and_minor_ticks(ax, date_format)
    ax.set_ylabel("Colony forming units per 100mL")
    ax.set_xlabel("")
    ax.axhline(y=100, xmin=0, xmax=1, ls="--", label="limit", color="black")
    
    
    legend_elements = [
        Line2D([0], [0], marker='o', markerfacecolor='dodgerblue', markeredgecolor=None, markersize=8, label="SVT", lw=0),
        Line2D([0], [0], marker='s', markerfacecolor='green', markeredgecolor=None, markersize=8, label='VNX', lw=0),
        Line2D([0], [0], marker='X', markerfacecolor='red', markeredgecolor=None, markersize=8, label='MRD', lw=0),
        Patch(facecolor='black', edgecolor=None, alpha=0.4, label='event')]
    
    ax.set_title(f"{project}\n{title}", loc="left")
   
    ax.legend(handles=legend_elements, loc="upper right", fontsize=10)
        
    plt.tight_layout()

    plt.savefig(file_name)

    plt.show()

def boxplots_before_during_after(data, project, title, figure_name, file_name):

    fig, ax = plt.subplots()

    ax.boxplot(data)
    ax.set_ylabel("Colony forming units per 100mL")
    ax.set_xticklabels(["before", "during", "after"])
    ax.axhline(y=100, xmin=0, xmax=1, ls="--", label="limit", color="black")
    ax.set_title(f"{project}\n{title}", loc="left")
    plt.tight_layout()

    plt.savefig(file_name)

    plt.show()
