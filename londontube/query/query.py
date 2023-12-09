from londontube.network import Network
import requests
import csv
from io import StringIO


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
    query_web = f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/line/query?line_identifier={line_index}"
    response = requests.get(query_web).content.decode("utf-8")
    # Store line csv information
    connectivity_info = csv.reader(StringIO(response))
    # List to store edges
    list_of_edges = []
    # Set to get station indices
    stations = set()

    for each_connectity in connectivity_info:
        if each_connectity:
            # Store each row's information
            station1, station2, travel_time = map(int, each_connectity)
            list_of_edges.append((station1, station2, travel_time))
            stations.add(station1)
            stations.add(station2)
    n_stations = len(stations)
    line_network = Network(n_stations, list_of_edges)
    return line_network


def disruption_info(date):
    """
    Retrieve disruption info from web services.

    Parameters
    ----------
    date : str
        Given day.

    Returns
    -------
    dict
        Dictionary of disruption information.
    """
    pass


def network_of_given_day(date):
    """
    Retrieve the whole information of the given day and construct a Network object from this.

    Parameters
    ----------
    date : str
        Given day.

    Returns
    -------
    Network
        Network representation of londontube.
    """
    pass
