from climate_signals.noaa.source import NOAASource 
import pandas as pd
import pytest
import os 

@pytest.fixture
def source():
    return NOAASource(os.environ.get("NOAA_TOKEN"))

def test_get_stations(source):
    # Test with test_fetch=True
    test_stations_df = source.get_stations(test_fetch=True)
    assert isinstance(test_stations_df, pd.DataFrame)
    assert not test_stations_df.empty
    assert len(test_stations_df) == 5  # Since test_fetch is True, only 5 stations should be fetched

def test_get_stations_data(source):
    test_station_ids = ["AEM00041194", "AEM00041217"]

    # Test with default parameters
    stations_data_df = source.get_stations_data(stations=test_station_ids)
    assert isinstance(stations_data_df, pd.DataFrame)
    assert not stations_data_df.empty

    # Test with custom start_date and end_date
    custom_dates_df = source.get_stations_data(
        stations=test_station_ids, start_date="2022-01-01", end_date="2022-12-31"
    )
    assert isinstance(custom_dates_df, pd.DataFrame)
    assert not custom_dates_df.empty