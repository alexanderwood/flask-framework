import requests
import os
from io import StringIO
import sys

import numpy
import pandas as pd

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

from bokeh.plotting import figure
from bokeh.io import show
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.embed import file_html

#from config import *  # DEVELOPMENT ONLY
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')

app = Flask(__name__)


def query_alpha_vantage(ticker_symbol, date_slice):
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
    date_slice = 'year' + year + 'month' + month
    df = query_alpha_vantage(ticker_symbol, date_slice)
    return str(df.head())
    f = figure(x_axis_type='datetime')
    
    source = ColumnDataSource(df)
    
    f.line('time', 'close', source=source)
    f.ygrid.grid_line_color = None
    
    #f.title('Closing data for the month of x')
    
    return(f)


@app.route('/submit', methods=['POST'])
def submit():
    print("bar")
    return render_template('submit.html')
#  return render_template('about.html')
  
  
@app.route('/about', methods=['POST'])
def about():
    print('abc')
    return render_template('about.html')


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/', methods=['POST'])
def index_post():
    year = request.form['year']
    month = request.form['month']
    ticker_symbol = request.form['stock']

    f = plot_stock(ticker_symbol, month, year)
    return f
    #script, div = components(f)
    h = file_html(f,CDN,"my plot")
    return h
    return render_template('index.html', script=script, div=div)


if __name__ == '__main__':
    app.run(port=5000)
