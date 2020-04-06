import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os import listdir

# county population data https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-total.html
countypops = {county.split('County,')[0].strip('. ') : count for (index, county, count) in pd.read_csv('./data/2019-county-estimates.csv').itertuples()}
    
# JHU time series https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv
covidts = 'data/time_series_covid19_confirmed_US.csv'
covidtsx = pd.read_csv(covidts)


dates = list(covidtsx.columns[covidtsx.columns.get_loc('1/22/20'):])

# just arkansas state's data from the jhu sheet
statedata =  covidtsx[covidtsx['Province_State'].str.contains('Arkansas')]
statedata = statedata.drop(statedata[statedata['Admin2'] == 'Unassigned'].index)
statedata = statedata.drop(statedata[statedata['Admin2'] == 'Out of AR'].index)

# first data of any case in an arkansas county
firstdate = next(i for (i, c) in enumerate(list(statedata[dates].sum())) if c > 0)

# start plotting a couple of days before that
plotdates = dates[firstdate-2:]


def plotstate():
    y_pos = np.arange(len(plotdates))
    counts = list(statedata[plotdates].sum())
    m = max(counts)
    m = round(m*1.1)
    plt.ylim(0, m)
    plt.subplots_adjust(hspace=0, bottom=0.3)
    plt.plot(y_pos, counts)
    plt.title("State of Arkansas total")
    plt.xticks(y_pos, plotdates, rotation=70)
    plt.savefig('./arcounties/images/AR.png')
    plt.clf()

def plotstate_deltas():
    y_pos = np.arange(len(plotdates))
    counts = list(statedata[plotdates].sum())
    deltas = [max(x - y, 0) for (x, y)  in zip(counts, [0]+counts[:-1])]
    plt.ylim(0, round(max(deltas)*1.1))
    plt.subplots_adjust(hspace=0, bottom=0.3)
    plt.bar(y_pos, deltas)
    plt.title("State of Arkansas total")
    plt.xticks(y_pos, plotdates, rotation=70)
    plt.savefig('./arcounties/images/AR-deltas.png')
    plt.clf()
    

def get_deltas(cname):
    counts = list(statedata[statedata['Admin2'] == cname][plotdates].squeeze())
    return [max(x - y, 0) for (x, y)  in zip(counts, [0]+counts[:-1])]

all_deltas = {cname : get_deltas(cname) for cname in statedata['Admin2']}
max_delta = max([max(x) for x  in all_deltas.values()])


def plotcounty(cname):
    y_pos = np.arange(len(plotdates))
    counts = list(statedata[statedata['Admin2'] == cname][plotdates].squeeze())
    m = max(statedata[dates[-1]]) # largest county count on most recent day
    m = round(m*1.1)
    plt.ylim(0, m)
    plt.subplots_adjust(hspace=0, bottom=0.3)
    plt.plot(y_pos, counts)
    plt.title("%s county total" % (cname))
    #plt.bar(y_pos, counts, align='center', alpha=0.5)
    plt.xticks(y_pos, plotdates, rotation=70)
    plt.savefig('./arcounties/images/%s.png'  % (cname))
    plt.clf()

def plotcounty2(cname):
    y_pos = np.arange(len(plotdates))
    counts = list(statedata[statedata['Admin2'] == cname][plotdates].squeeze())
    deltas = get_deltas(cname)
    plt.ylim(0, round(max_delta*1.1))
    plt.subplots_adjust(hspace=0, bottom=0.3)
    plt.bar(y_pos, deltas)
    plt.title("%s county daily change" % (cname))
    plt.xticks(y_pos, plotdates, rotation=70)
    plt.savefig('./arcounties/images/%s-deltas.png'  % (cname))
    plt.clf()

    
def plotall():
    plotstate()
    plotstate_deltas()
    for c in list(statedata['Admin2']):
        plotcounty(c)
        plotcounty2(c)


def gen_jhu_html():
    return """<h2># confirmed covid-19 cases in Arkansas by county as of %s.<h2>
<br>
<h3>Covid-19 counts from 
<a href="https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv">2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE</a>
<br>
2019 county population estimates via <a href="https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-total.html">census.gov</a></h3><br>""" % (dates[-1])

def gen_image_html(cname):
    return """<div style="content" id="%s">
              <hr>
              %s (2019 est population: %s)
              <br>
              <img src="./arcounties/images/%s.png"/>
              <img src="./arcounties/images/%s-deltas.png"/>
              </div>""" % (cname.replace(' ', '_'), cname, countypops[cname], cname, cname)
def gen_head():
    return '<html><head><link rel="stylesheet" href="arcounties/style.css"/></head>'

def gen_state_images():
    return """<img src="./arcounties/images/AR.png"/>
              <img src="./arcounties/images/AR-deltas.png"/>')"""


def gen_nav(nav = 'index'):
    if nav == 'index':
        return '<h3>Alphabetical order | <a href="./index-by-cases.html"> Order by # cases</a> | <a href="./index-by-pop.html"> Order by county population</a></h3>'
    elif nav == 'case':
        return '<h3><a href="./index.html">Alphabetical order</a> | Order by # cases | <a href="./index-by-pop.html"> Order by county population</a></h3>'
    else:
        return '<h3><a href="./index.html">Alphabetical order</a> | <a href="./index-by-cases.html"> Order by # cases</a> | Order by county population'

def write_index(counties):
    with open('./index.html', 'w') as f:
        f.write(gen_head())
        f.write(gen_nav('index'))
        f.write(gen_jhu_html())
        f.write(gen_state_images())

        for cname in counties:
            f.write(gen_image_html(cname))
            
    with open('./index-by-cases.html', 'w') as f:
        f.write(gen_head())
        f.write(gen_nav('case'))
        f.write(gen_jhu_html())
        f.write(gen_state_images())        
        
        #TODO much cleaner way to do this in pandas 
        for cname in [c for (c, x) in sorted([(county, count) for (i, county, count) in statedata[['Admin2', '4/5/20']].itertuples()], key = lambda x : x[1], reverse=True)]:
            f.write(gen_image_html(cname))            

    with open('./index-by-pop.html', 'w') as f:
        f.write(gen_head())
        f.write(gen_nav('pop'))
        f.write(gen_jhu_html())
        f.write(gen_state_images())                

        #TODO much cleaner way to do this in pandas
        for cname in [c for (c,x) in sorted([(name, int(count.replace(',',''))) for (name, count) in countypops.items()], key = lambda x : x[1], reverse = True)]:
            f.write(gen_image_html(cname))
