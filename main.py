import requests
import json
import pandas as pd

lon_min,lat_min = -0.51,51.28
lon_max,lat_max = 0.33,51.69
username = ''
password = ''
urldata='https://'+username+':'+password+'@opensky-network.org/api/states/all?'+'lamin='+str(lat_min)+'&lomin='+str(lon_min)+'&lamax='+str(lat_max)+'&lomax='+str(lon_max)
response = requests.get(urldata).json()
column_names = ['icao24','callsign','origin_country','time_position','last_contact','long','lat','baro_altitude','on_ground','velocity','true_track','vertical_rate','sensors','geo_altitude','squawk','spi','position_source']
Flight_DataFrame = pd.DataFrame(response['states'])
Flight_DataFrame=Flight_DataFrame.loc[:,0:16]
Flight_DataFrame.columns = column_names
Flight_DataFrame=Flight_DataFrame.fillna('NO DATA')
Flight_DataFrame.head()
print(Flight_DataFrame.head())
Flight_DataFrame.to_csv('flight_data2.csv', index=False)                   #use this to save the data into a csv file

