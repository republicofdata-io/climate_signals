from climate_signals.noaa.source import NOAASource
import os

source = NOAASource(os.environ.get("NOAA_TOKEN"))

# get all stations for the Global Summary of the month dataset ( test_fetch limits stations fetched to 5)
stations = source.get_stations(dataset="GSOM", test_fetch=True)
print(stations)

# get provided stations climate data
stations_data = source.get_stations_data(stations=stations["id"].values)
print(stations_data)
