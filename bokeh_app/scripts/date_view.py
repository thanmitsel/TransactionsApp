## TODO

import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import (ColumnDataSource, HoverTool, Panel, LinearAxis, Range1d, DateFormatter)
from bokeh.models.widgets import (DataTable, TableColumn, Dropdown)


from bokeh.layouts import (WidgetBox, row, column)
from bokeh.transform import cumsum
from bokeh.palettes import viridis



# Function to make an overview of categories of expenses
def date_view_tab(df, x_name, y_name, measure, t_count):

    def make_dataset(category_list):
        details = pd.DataFrame()
        for cat in category_list:
            subset = df[df[x_name] == cat]
            details = details.append(subset)
        by_category = details.groupby(x_name)[measure].agg(['sum', 'count']).reset_index()\
            .rename(columns={'sum': y_name}).sort_values(by=y_name, ascending=False)
        by_category['Percentage'] = by_category[y_name]/by_category[y_name].sum()
        by_category['angle'] = by_category['Percentage'] * 2 * np.pi
        by_category['Percentage'] = by_category['Percentage'] * 100
        by_category['color'] = viridis(len(category_list))
        return ColumnDataSource(by_category), ColumnDataSource(details)

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

        # Vertical Names
        p.xaxis.major_label_orientation = np.pi / 4
        return p

    def make_plot(src):
        # Create the blank plot
        p = figure(x_range=src.data[x_name], plot_width=1000, plot_height=600,
                   title=x_name + ' vs ' + y_name,
                   x_axis_label=x_name, y_axis_label=y_name)

        # Setting the second y axis range name and range
        p.extra_y_ranges = {"Occurance": Range1d(start=0, end=src.data['count'].max())}

        # Adding the second axis to the plot.
        p.add_layout(LinearAxis(y_range_name="Occurance"), 'right')

        p.vbar(source=src, x=x_name,
               bottom=0, top=y_name, width=0.9,
               fill_color='color', line_color='black', fill_alpha=0.75,
               hover_fill_alpha=1.0, hover_fill_color='grey')

        p.line(x = x_name, y = t_count, source = src, line_width=1.2, line_color='black', y_range_name = "Occurance")

        # Hover tool referring to our own data field using @ and
        # a position on the graph using $
        h = HoverTool(tooltips=[(y_name, '@' + y_name),
                                ('Count of transactions', '@' + t_count)])

        # Add the hover tool to the graph
        p.add_tools(h)

        # Style the plot
        p = style(p)
        return p

    def make_table(tbl_src):
        # columns = [TableColumn(field=col, title=col, formatter = DateFormatter(format="yy-m-d") if 'date' in col.lower() else None) for col in list(tbl_src.data.keys())]
        columns = [TableColumn(field=col, title=col, formatter = DateFormatter(format="%Y-%m-%d")) if 'date' in col.lower() else TableColumn(field=col, title=col) for col in list(tbl_src.data.keys())[1:]]
        data_table = DataTable(source=tbl_src, columns=columns, editable=True, width=600, height=600)
        return data_table

    def make_pie_chart(src):
        # Create the blank plot
        pie = figure(plot_height=600, title="Percentage per "+x_name, toolbar_location=None,
                   tools="hover", x_range=(-0.5, 1.0))

        pie.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                legend=x_name, source=src, fill_color='color', line_color = 'black', fill_alpha = 0.75,
                hover_fill_alpha=1.0, hover_fill_color='grey')

        pie.axis.axis_label = None
        pie.axis.visible = False
        pie.grid.grid_line_color = None

        h = HoverTool(tooltips=[('Percentage', '@Percentage'),
                                (y_name, '@' + y_name),
                                ('Count of transactions', '@' + t_count)])

        # Add the hover tool to the graph
        pie.add_tools(h)

        # Style the plot
        pie = style(pie)
        return pie


    # def update(attr, old, new):
    def update(event):
        categories_to_plot = event.item# dropdown.value

        new_src, new_tbl_src = make_dataset([categories_to_plot])

        # src.data.update(new_src.data)
        tbl_src.data.update(new_tbl_src.data)

    # categories and colors
    available_categories = list(set(df[x_name]))

    dropdown = Dropdown(label="Category", button_type="warning", menu=available_categories)
    # dropdown.on_change('value', update)
    dropdown.on_click(update)

    # Initial categories and data source
    src, tbl_src = make_dataset(available_categories)

    p = make_plot(src)

    pie = make_pie_chart(src)

    data_table = make_table(tbl_src)


    # Put controls in a single element
    controls = WidgetBox(dropdown)
    # Create a row layout
    # layout = column(p, controls, data_table)
    # right = column(controls, data_table)
    # left = column(pie, p)
    right = column(p)
    left = column(pie, controls, data_table)
    layout = row(left, right)


    # Make a tab with the layout
    tab = Panel(child = layout, title = 'Date View')

    return tab
