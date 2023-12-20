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


def apply_disruptions(network, disruptions):
    """
    This function is used to apply disruptions to the entired network gained 
    from get_entire_network() function

    Parameters
    ----------
    network : Network
        The network here is the entire network combined by each line of sub networks
    disruptions : dictionary
        The disruption information
    """
    
    pass
  
def get_entire_network():
    """
    Combine each sub network of each line to a full London network which can change 
    based on disruption information

    Returns
    -------
    Network
        An entire underground network of London
    """
    
    # Query the information of the network
    query_total_info = (
        f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/index/query"
    )
    response = requests.get(query_total_info)
    total_info = response.json()
    
    # The number of lines
    n_lines = int(total_info['n_lines'])
    
    # Set the first line's network as the entire one
    entire_network = connectivity_of_line(0)

    # Combine the network of each subsequent line
    for line_idx in range(1, n_lines):
        line_network = connectivity_of_line(line_idx)
        entire_network = entire_network + line_network
    
    return entire_network

def network_of_given_day(date):
    """
    Retrieve the whole information of the given day and construct a Network object based on the 
    disruption information.

    Parameters
    ----------
    date : str
        Given day.

    Returns
    -------
    Network
        Network representation of londontube.
    """
    
    entire_network = get_entire_network()
    disruptions = disruption_info(date)
    changed_network = apply_disruptions(entire_network, disruptions)
    
    return changed_network


def query_station_to_index(list_of_stations):
    """
    Query the web service to get the index of each of the stations.

    Parameters
    ----------
    list_of_stations : List[str]
        A list of station names. Each element in the list is a string representing the name of a station.

    Returns
    -------
    List[int]
        A list of integers representing the indices of the given stations.
    List[str]
        A list of strings representing the names of the given stations.
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


