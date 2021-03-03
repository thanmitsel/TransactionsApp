# Pandas for data management
import pandas as pd
import numpy as np

# os methods for manipulating paths
import os
from os.path import dirname, join

# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Each tab is drawn by one script
from scripts.overview import overview_tab
from scripts.expenses import expenses_tab
from scripts.date_view import date_view_tab


def read_files(app_dir, data_dir):
    df = pd.DataFrame()
    for afile in os.listdir(join(app_dir,data_dir)):
        if '-' in afile:
            path_file = join(dirname(__file__), data_dir, afile)
            temp_df = pd.read_csv(path_file)
            df = df.append(temp_df)
    return df

def get_first_word(val):
    out = val.split()[0]
    return out

# Define the parameters for plotting on one card
x_name_gr = 'Category' # existing col
measure_gr = 'Amount' # existing col
date_name_gr = 'Posted date' # existing col

# Define the parameters for plotting on the other card
x_name_uk = 'Transaction description' # existing col
measure_uk = 'Debit Amount' # existing col
date_name_uk = 'Transaction date' # existing col

# columns names for metrics
y_name = 'Total'
t_count = 'count'

# Read inial file
in_name = 'transactions.csv'
data_dir = 'data'
app_dir = 'bokeh_app'

gr_trans = pd.read_csv(join(dirname(__file__), data_dir, in_name))

uk_trans = read_files(app_dir, data_dir)
uk_trans[x_name_uk] = uk_trans[x_name_uk].apply(get_first_word)


# Convert to datetime
gr_trans[date_name_gr] = pd.to_datetime(gr_trans[date_name_gr], format = "%d/%m/%Y")
uk_trans[date_name_uk] = pd.to_datetime(uk_trans[date_name_uk], format = "%Y-%m-%d")
print(uk_trans)
# print(np.issubdtype(uk_trans[date_name_uk], np.datetime64))
# Segment to deposits and expenses
dep = gr_trans.loc[gr_trans[measure_gr] > 0].copy()
exp = gr_trans.loc[gr_trans[measure_gr] < 0].copy()
exp[measure_gr] = exp[measure_gr].abs()

# Create each of the tabs
tab1 = overview_tab(gr_trans, x_name_gr, date_name_gr, measure_gr)
tab2 = expenses_tab(exp, x_name_gr, y_name, measure_gr, t_count)
tab3 = date_view_tab(uk_trans, x_name_uk, y_name, measure_uk, t_count)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1, tab2, tab3])

# Put the tabs in the current document for display
curdoc().add_root(tabs)

