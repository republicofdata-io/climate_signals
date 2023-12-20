# more info on columns https://www.ncei.noaa.gov/data/global-summary-of-the-month/doc/GSOMReadme-v1.0.3.txt
# NOAA api documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
import requests
import pandas as pd


class NOAASource:
    """
    Class for interacting with NOAA (National Oceanic and Atmospheric Administration) datasets.

    Attributes:
    - API_URL: Base URL for NOAA API v2.
    - V1_API_URL: Base URL for NOAA API v1 (legacy api, may be unnecessary in the future).
    - STATIONS_INFO_LIMIT: Maximum number of stations to retrieve in a single request.
    - STATIONS_DATA_LIMIT: Maximum number of stations to retrieve climate data in a single request.

    Methods:
    - __init__: Constructor for the NOAASource class.
    - request: Send an HTTP GET request and return the JSON response.
    - get_stations: Retrieve information about NOAA weather stations.
    - get_stations_data: Retrieve weather data for a list of NOAA weather stations.
    """

    API_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
    V1_API_URL = (
        "https://www.ncei.noaa.gov/access/services/data/v1"  # might be unnecessary!
    )

    STATIONS_INFO_LIMIT = 1000
    STATIONS_DATA_LIMIT = 50

    def __init__(self, noaa_token: str) -> None:
        """
        Constructor for the NOAASource class.

        Parameters:
        - ncdc_token: Token for accessing NOAA API (https://www.ncdc.noaa.gov/cdo-web/token).
        """

        self.token_header = {"token": noaa_token}

    def request(self, url) -> dict | None:
        """
        Send an HTTP GET request and return the JSON response.

        Parameters:
        - url: The URL for the HTTP GET request.

        Returns:
        The JSON response as a dictionary, or None if the request fails.
        """

        response = requests.get(url, headers=self.token_header)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def get_stations(self, dataset: str = "GSOM", test_fetch:bool=False) -> pd.DataFrame:
        """
        Retrieve information about NOAA weather stations.

        Parameters:
        - dataset: The dataset ID for weather stations (default is "GSOM").
        - test_fetch: If True, retrieves only 5 stations for testing purposes.

        Returns:
        A pandas DataFrame containing information about NOAA weather stations.
        """

        url = f"{self.API_URL}/stations?datasetid={dataset}&limit={5 if test_fetch else self.STATIONS_INFO_LIMIT}"
        data = self.request(url)

        num_stations = data["metadata"]["resultset"]["count"]
        stations_df = pd.DataFrame(data["results"])

        if not test_fetch:
            offset = self.STATIONS_INFO_LIMIT + 1
            while offset < num_stations:
                data = self.request(f"{url}&offset={offset}")
                if data:
                    stations_df = pd.concat(
                        [stations_df, pd.DataFrame(data["results"])], ignore_index=True
                    )
                    offset += self.STATIONS_INFO_LIMIT

        stations_df["id"] = stations_df["id"].str.replace("GHCND:", "")
        return stations_df

    def get_stations_data(
        self, *, dataset: str = "global-summary-of-the-month", stations: list[str], start_date: str = "0001-01-01", end_date="9996-12-31"
    ) -> pd.DataFrame:
        """
        Retrieve weather data for a list of NOAA weather stations.

        Parameters:
        - dataset: The dataset ID for weather data (default is "global-summary-of-the-month").
        - stations: List of NOAA weather station IDs.
        - start_date: The start date for data retrieval in the format "YYYY-MM-DD" (default is "0001-01-01").
        - end_date: The end date for data retrieval in the format "YYYY-MM-DD" (default is "9996-12-31").

        Returns:
        A pandas DataFrame containing weather data for the specified stations.
        """

        url = f"{self.V1_API_URL}?dataset={dataset}&startDate={start_date}&endDate={end_date}&format=json"
        stations_data = pd.DataFrame(
            self.request(f"{url}&stations={stations[0]}"))

        offset = 1
        while offset < len(stations):
            data = self.request(
                f"{url}&stations={','.join(stations[offset:offset+self.STATIONS_DATA_LIMIT])}"
            )
            if data:
                stations_data = pd.concat(
                    [stations_data, pd.DataFrame(data)], ignore_index=True
                )
                offset += self.STATIONS_DATA_LIMIT

        return stations_data
