import requests
import json
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, LabelSet, ColumnDataSource
from bokeh.tile_providers import STAMEN_TERRAIN
import numpy as np
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler


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


lon_min, lat_min = -0.51, 51.28
lon_max, lat_max = 0.33, 51.69

xy_min = wgs84_web_mercator_point(lon_min, lat_min)
xy_max = wgs84_web_mercator_point(lon_max, lat_max)

x_range, y_range = ([xy_min[0], xy_max[0]], [xy_min[1], xy_max[1]])
username = ''
password = ''
urldata = 'https://' + username + ':' + password + '@opensky-network.org/api/states/all?' + 'lamin=' + str(lat_min) + '&lomin=' + str(lon_min) + '&lamax=' + str(lat_max) + '&lomax=' + str(lon_max)


def flight_tracking(doc):
    flight_source = ColumnDataSource({
        'icao24': [], 'callsign': [], 'origin_country': [],
        'time_position': [], 'last_contact': [],
        'long': [], 'lat': [], 'baro_altitude': [], 'on_ground': [], 'velocity': [], 'true_track': [],
        'vertical_rate': [], 'sensors': [], 'geo_altitude': [], 'squawk': [], 'spi': [], 'position_source': [],
        'rot_angle': [], 'url': [], 'x': [], 'y': []
    })

    def update():
        response = requests.get(urldata).json()
        column_names = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'long', 'lat',
                        'baro_altitude', 'on_ground', 'velocity', 'true_track', 'vertical_rate', 'sensors',
                        'geo_altitude', 'squawk', 'spi', 'position_source']
        Flight_Data = response['states']
        Flight_Dataframe = pd.DataFrame(Flight_Data, columns=column_names)
        wgs84_to_web_mercator(Flight_Dataframe)
        Flight_Dataframe = Flight_Dataframe.fillna('no data')
        Flight_Dataframe['rot_angle'] = Flight_Dataframe['true_track'] * -1
        icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Red_Arrow_Left.svg/1200px-Red_Arrow_Left.svg.png'
        Flight_Dataframe['url'] = icon_url

        n_roll = len(Flight_Dataframe.index)
        flight_source.stream(Flight_Dataframe[['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact',
                                               'long', 'lat', 'baro_altitude', 'on_ground', 'velocity', 'true_track',
                                               'vertical_rate', 'sensors', 'geo_altitude', 'squawk', 'spi',
                                               'position_source', 'rot_angle', 'url', 'x', 'y']].to_dict(orient='list'), n_roll)

    doc.add_periodic_callback(update, 3000)
    p = figure(x_range=x_range, y_range=y_range, x_axis_type='mercator', y_axis_type='mercator', sizing_mode='scale_width', height=300)
    p.add_tile(STAMEN_TERRAIN)

    p.image_url(url='url', x='x', y='y', source=flight_source, anchor='center', angle_units='deg', angle='rot_angle', h_units='screen', w_units='screen', w=40, h=40)
    p.scatter('x', 'y', source=flight_source, fill_color='red', hover_color='yellow', size=10, fill_alpha=0.8, line_width=0)

    hover = HoverTool()
    hover.tooltips = [('Call sign', '@callsign'), ('Origin Country', '@origin_country'), ('velocity(m/s)', '@velocity'),
                      ('Altitude(m)', '@baro_altitude'), ('vertical(m)', '@vertical_rate')]
    labels = LabelSet(x='x', y='y', text='callsign', level='glyph',
                      x_offset=5, y_offset=5, source=flight_source, background_fill_color='white', text_font_size='8pt')
    p.add_tools(hover)
    p.add_layout(labels)

    doc.title = "Real-time tracking"
    doc.add_root(p)


apps = {'/': Application(FunctionHandler(flight_tracking))}
server = Server(apps, port=8000)
server.start()
server.io_loop.add_callback(server.show, "/")
server.io_loop.start()
