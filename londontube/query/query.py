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
    query_total_info = f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/index/query"
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
