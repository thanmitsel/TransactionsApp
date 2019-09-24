# Pandas for data management
import pandas as pd

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Each tab is drawn by one script
from scripts.overview import overview_tab
from scripts.expenses import expenses_tab

# Read inial file
in_name = 'transactions.csv'
data_dir = 'data'
trans = pd.read_csv(join(dirname(__file__), data_dir, in_name))

# Define the parameters for plotting
x_name = 'Category' # existing col
measure = 'Amount' # existing col
date_name = 'Posted date' # existing col
y_name = 'Total'
t_count = 'count'


# Convert to datetime
trans[date_name] = pd.to_datetime(trans[date_name], format = "%d/%m/%Y")

# Segment to deposits and expenses
dep = trans.loc[trans[measure] > 0].copy()
exp = trans.loc[trans[measure] < 0].copy()
exp[measure] = exp[measure].abs()

# Create each of the tabs
tab1 = overview_tab(trans, x_name, date_name, measure)
tab2 = expenses_tab(exp, x_name, y_name, measure, t_count)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1, tab2])

# Put the tabs in the current document for display
curdoc().add_root(tabs)

