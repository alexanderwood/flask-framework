#!/usr/bin/env python3
# @author: Alexander Wood

import requests
import os
from io import StringIO
import sys

import numpy
import pandas as pd

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.embed import components

#from config import *  # DEVELOPMENT ONLY
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
app = Flask(__name__)


def query_alpha_vantage(ticker_symbol, date_slice):
    '''Query alpha vantage for one month of stock data.'''
    json_query = ('https://www.alphavantage.co/query?' +
        'function=TIME_SERIES_INTRADAY_EXTENDED' +
        '&symbol=' + ticker_symbol +
        '&interval=15min' +
        '&slice=' + date_slice +
        '&apikey=' + ALPHA_VANTAGE_API_KEY)

    page = requests.get(json_query)
    
    data = StringIO(page.content.decode('utf-8'))
    
    df = pd.read_csv(data)

    df = df[['time', 'close']]
    df['time'] = df['time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

    return df
    

def plot_stock(ticker_symbol, month, year):
    '''Plot one month of stock closing data'''
    date_slice = 'year' + year + 'month' + month
    df = query_alpha_vantage(ticker_symbol, date_slice)

    strout = ticker_symbol + ' stock closing prices'
    f = figure(x_axis_type='datetime',
               aspect_ratio = 2,
               title = strout)
    
    source = ColumnDataSource(df)
    
    f.line('time', 'close', source=source, color='navy')
    
    f.ygrid.grid_line_color = None
    f.ygrid.band_fill_color = 'navy'
    f.ygrid.band_fill_alpha = 0.05
    f.yaxis.axis_label = 'Price'
    f.xaxis.axis_label = 'Date'
    
    return f


@app.route('/')
def index():
    return render_template('index.html')
    
    
@app.route('/', methods=['POST'])
def index_post():
    year = request.form['year']
    month = request.form['month']
    ticker_symbol = request.form['stock']

    f = plot_stock(ticker_symbol, month, year)

    return h

@app.route('/response', methods=['POST'])
def response():
    year = request.form['year']
    month = request.form['month']
    ticker_symbol = request.form['stock']

    f = plot_stock(ticker_symbol, month, year)
    
    script, div = components(f)
    return render_template('response.html', div=div, script=script)
    

if __name__ == '__main__':
    app.run(port=5000)
