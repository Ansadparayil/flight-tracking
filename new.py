from bokeh.plotting import figure, show
from bokeh.tile_providers import get_provider

# Importing your other modules
from bokeh.models import HoverTool, LabelSet, ColumnDataSource
from main import lon_min, lat_min, lon_max, lat_max, Flight_DataFrame
import numpy as np

def wgs84_web_mercator_point(lon, lat):
    k = 6378137
    x = lon * (k * np.pi / 180)
    y = np.log(np.tan((90 + lat) * np.pi / 360)) * k
    return x, y

def wgs84_to_web_mercator(df, lon="long", lat="lat"):
    k = 6378137
    df['x'] = df[lon] * (k * np.pi / 180)
    df['y'] = np.log(np.tan((90 + df[lat]) * np.pi / 360)) * k
    return df

# Rest of your code
xy_min = wgs84_web_mercator_point(lon_min, lat_min)
xy_max = wgs84_web_mercator_point(lon_max, lat_max)
wgs84_to_web_mercator(Flight_DataFrame)
Flight_DataFrame['rot_angle'] = Flight_DataFrame['true_track'] * -1
icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Red_Arrow_Left.svg/1200px-Red_Arrow_Left.svg.png'
Flight_DataFrame['url'] = icon_url

x_range, y_range = ([xy_min[0], xy_max[0]], [xy_min[1], xy_max[1]])
p = figure(x_range=x_range, y_range=y_range, x_axis_type='mercator', y_axis_type='mercator', sizing_mode='scale_width', height=300)

flight_source = ColumnDataSource(Flight_DataFrame)

# Use OpenStreetMap (OSM) tile provider
tile_provider = get_provider('OSM')
p.add_tile(tile_provider)

p.image_url(url='url', x='x', y='y', source=flight_source, anchor='center', angle_units='deg', angle='rot_angle', h_units='screen', w_units='screen', w=40, h=40)
p.scatter('x', 'y', source=flight_source, fill_color='red', hover_fill_color='yellow', size=10, fill_alpha=0.8, line_width=0)

hover = HoverTool()
hover.tooltips = [('Call sign', '@callsign'), ('Origin Country', '@origin_country'), ('velocity(m/s)', '@velocity'), ('Altitude(m)', '@baro_altitude'),('vertical(m)','@vertical_rate')]
labels = LabelSet(x='x', y='y', text='callsign', level='glyph',
                  x_offset=5, y_offset=5, source=flight_source, background_fill_color='white', text_font_size='8pt')
p.add_tools(hover)
p.add_layout(labels)
show(p)
