from londontube.network import Network
import requests
import csv
from io import StringIO
import pandas as pd


def connectivity_of_line(line_index):
    """
    Query the web service for information about a particular line, and
    contruct a Network object that represent this line.

    Parameters
    ----------
    line_index : int
        Index of the line.

    Returns
    -------
    Network
        Network of a line.
    """
    query_total_info = (
        f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/index/query"
    )
    response = requests.get(query_total_info)
    total_info = response.json()

    query_web = f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/line/query?line_identifier={line_index}"
    response = requests.get(query_web).content.decode("utf-8")
    # Store line csv information
    connectivity_info = csv.reader(StringIO(response))
    # List to store edges
    list_of_edges = []
    # Set to get station indices

    for each_connectity in connectivity_info:
        if each_connectity:
            # Store each row's information
            station1, station2, travel_time = map(int, each_connectity)
            list_of_edges.append((station1, station2, travel_time))

    line_network = Network(int(total_info["n_stations"]), list_of_edges)
    return line_network


def disruption_info(date=None):
    """
    Retrieve disruption info from web services.

    Parameters
    ----------
    date : str
        The date of disruption, by default None

    Returns
    -------
    List
        A list of dictionary contains disruption information
    """

    # Return today's disruption information if not date provided
    if date == None:
        query_web = f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/disruptions/query"
    else:
        query_web = f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/disruptions/query?date={date}"

    response = requests.get(query_web)
    disruption_info = response.json()

    return disruption_info


def query_station_to_index(list_of_stations):
    """query the web service to get the index of each of the stations

    list_of_stations: List[str]: str is the name of station

    return: List[int],List[str]: the index of the given stations and the name of the given stations
    """

    if list_of_stations == []:
        response = requests.get(
            "https://rse-with-python.arc.ucl.ac.uk/londontube-service/stations/query?id=all"
        )
    else:
        list_str = ",".join(map(str, list_of_stations))
        requests_str = (
            "https://rse-with-python.arc.ucl.ac.uk/londontube-service/stations/query?id="
            + list_str
        )
        response = requests.get(requests_str)
    df = pd.read_csv(StringIO(response.text))
    return df["station index"].tolist(), df["station name"].tolist()


