## TODO


import pandas as pd
import numpy as np
from datetime import datetime

from bokeh.plotting import figure
from bokeh.models import (ColumnDataSource, HoverTool, Panel, DatetimeTickFormatter)
from bokeh.models.widgets import (DataTable, TableColumn, DateRangeSlider, CheckboxGroup, PreText)

from bokeh.layouts import row, WidgetBox
from bokeh.palettes import viridis

# Function to make an overview of categories of expenses
def overview_tab(df, x_name, date_name, measure):

    def make_dataset(category_list, range_start, range_end):
        reduced = pd.DataFrame()
        for cat in category_list:
            subset = df[df[x_name] == cat]
            if (type(range_start) == int) or (type(range_start) == float):
                range_start = datetime.fromtimestamp(range_start / 1000)
                range_end = datetime.fromtimestamp(range_end / 1000)
            print(range_start, range_end)
            subset = subset[(subset[date_name] > range_start) & (subset[date_name] < range_end)]
            reduced = reduced.append(subset)
        temp = pd.DataFrame(zip(viridis(len(category_list)), category_list), columns=['color', x_name])
        reduced = pd.merge(reduced, temp, on = x_name)
        reduced = reduced.sort_values(by=date_name, ascending=True)
        return ColumnDataSource(reduced)

    def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'

        # Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'

        p.xaxis.formatter = DatetimeTickFormatter(
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"]
        )
        # Names in Angles
        p.xaxis.major_label_orientation = np.pi / 4
        return p

    def make_plot(src):
        # Create the blank plot
        p = figure(plot_width=1200, plot_height=700,
                   title=measure + ' vs ' + date_name,
                   x_axis_label=date_name, y_axis_label=measure)

        # p.line(src.data[date_name], src.data[measure], line_width=0.9, line_color='grey')
        # p.circle(src.data[date_name], src.data[measure], fill_color='grey', line_color= 'black')

        p.line(x = date_name, y = measure, source = src, line_width=0.9, line_color='grey')
        p.circle(x = date_name, y = measure, source = src, size = 10, fill_color='color', fill_alpha=0.75, line_color='black',
                 hover_fill_alpha=1.0, hover_fill_color='green')

        # Hover tool referring to our own data field using @ and
        # a position on the graph using $
        h = HoverTool(tooltips=[(x_name, '@' + x_name),
                                (measure, '@' + measure)])

        # Add the hover tool to the graph
        p.add_tools(h)

        # Style the plot
        p = style(p)
        return p

    def update(attr, old, new):
        categories_to_plot = [category_selection.labels[i] for i in category_selection.active]
        new_src = make_dataset(categories_to_plot, range_select.value[0], range_select.value[1])
        src.data.update(new_src.data)

    df = df.sort_values(by = date_name, ascending= True)

    available_categories = list(set(df[x_name]))

    category_selection = CheckboxGroup(labels=available_categories,
                                       active=[i for i in range(len(available_categories))])

    category_selection.on_change('active', update)

    # Initial categories and data source
    initial_categories = [category_selection.labels[i] for i in category_selection.active]

    # categories and colors
    range_select = DateRangeSlider(start=df[date_name].iloc[0], end=df[date_name].iloc[-1],
                                   value=(df[date_name].iloc[0], df[date_name].iloc[-1]),
                                    step=1, title='Time Window')
    range_select.on_change('value', update)

    # Initial categories and data source
    src = make_dataset(initial_categories, range_start = range_select.value[0], range_end = range_select.value[1])

    p = make_plot(src)


    # Put controls in a single element
    controls = WidgetBox(category_selection, range_select)
    # Create a row layout
    layout = row(controls, p)

    # Make a tab with the layout
    tab = Panel(child = layout, title = 'Overview')

    return tab
