from download import DataDownloader
import matplotlib.pyplot as plt
import os, sys, argparse, collections

#create parser for args from command line
parser = argparse.ArgumentParser(description="Get plot of the number of accidents in all of the regions in Czechia")
parser.add_argument('--fig_location',type=str,metavar='directory', default=None)
parser.add_argument('--show_figure', type=bool,metavar='(True/False)', default=False)
args = parser.parse_args()

def plot_stat(data_source, fig_location = None, show_figure = False):

    #if optional arg fig_location given, look for directory and create if doesn't exist
    if fig_location is not None:
        if not os.path.exists(fig_location):
            try:
                os.makedirs(fig_location)
            except:
                print("{} is an invalid path and directory couldn't be created".format(fig_location), file=sys.stderr)
                exit(-1)

    #save relevant data for plotting into nested dict
    regions = dict()
    
    for date, region in zip(data_source[1][3], data_source[1][-1]):
        if region not in regions:
            regions[region] = dict()
        if str(date.astype(object).year) not in regions[region]:
            
            regions[region][str(date.astype(object).year)] = 1
        else:
            
            regions[region][str(date.astype(object).year)] += 1
    
    #plotting

    plt.style.use('fivethirtyeight')
    
    x = list()
    for region in regions:
        x.append(region)
    
    x_pos = [i for i, _ in enumerate(x)]
    
    _, ax = plt.subplots(nrows = 5, ncols=1, figsize=(6,8), sharey=True)

    #creating subplots
    for col, year in zip(ax,sorted(list(list(regions.items())[2][1].keys()))):
       
        accident_values = list()
        order = dict()
        ordered = collections.OrderedDict()

        #get order for annotations
        for region in x:
            accident_values.append(regions[region][year])
            order[region] = regions[region][year]
        order = sorted(list(order.items()), key=lambda z:z[1], reverse=True)
        
        for i in order:
            ordered[i[0]] = i[1]

        #setting up parameters and appearance of subplot
        values = col.bar(x_pos, accident_values, width = 0.35)
        col.set_title(year, fontsize = 11)
        col.set_xticks(x_pos)
        col.set_xticklabels(x)
        col.tick_params(axis='x', labelsize=7)
        col.tick_params(axis='y', labelsize = 7)
        col.grid(b=None, axis='x')

        #annotations
        for value,region in zip(values, regions):
            col.annotate(str(list(ordered.keys()).index(region) + 1) + '.', xy=(value.get_x() + value.get_width() / 2, value.get_height()), xytext = (0,2), textcoords = "offset points", ha="center", fontsize=6)
    plt.tight_layout()

    #arg handling
    if fig_location is not None:
        plt.savefig(fig_location + '/' + "figure1.png")
    if show_figure:
        plt.show()


if __name__ == "__main__":

    plot_stat(data_source = DataDownloader().get_list(),fig_location=args.fig_location, show_figure=args.show_figure)
        

