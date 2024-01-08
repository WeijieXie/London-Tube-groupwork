""" Module handling queries to the disruption API """
import csv
from io import StringIO
import requests
import pandas as pd
from londontube.network import Network


def check_http_connection():
    """
    Check if the network is connected by trying to access a specific HTTP service.
    """
    try:
        response = requests.get("https://rse-with-python.arc.ucl.ac.uk/londontube-service", timeout=20)
        return response.status_code == 200
    except requests.RequestException:
        return False


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

    if check_http_connection() is False:
        raise requests.RequestException("poor connection, please check the network")

    query_total_info = (
        "https://rse-with-python.arc.ucl.ac.uk/londontube-service/index/query"
    )
    response = requests.get(query_total_info, timeout=120)
    total_info = response.json()

    query_web = f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/line/query?line_identifier={line_index}"
    response = requests.get(query_web, timeout=120).content.decode("utf-8")
    # Store line csv information
    connectivity_info = csv.reader(StringIO(response))
    # List to store edges
    list_of_edges = []
    # Set to get station indices

    for each_connectity in connectivity_info:
        if each_connectity:
            # Store each row's information
            station1, station2, travel_time = map(int, each_connectity)
            list_of_edges.append((station1, station2, travel_time, line_index))

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

    if check_http_connection() is False:
        raise requests.RequestException("poor connection, please check the network")

    # Return today's disruption information if not date provided
    if date is None:
        query_web = "https://rse-with-python.arc.ucl.ac.uk/londontube-service/disruptions/query"
    else:
        query_web = f"https://rse-with-python.arc.ucl.ac.uk/londontube-service/disruptions/query?date={date}"

    response = requests.get(query_web, timeout=120)
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

    for disruption in disruptions:
        # Not every disruption information have line or stations keyword
        line = disruption.get("line")
        stations_affected = disruption.get("stations", [])
        delay_multiplier = disruption["delay"]

        if stations_affected == []:
            return network

        # Stations is always len 1 or 2
        station1 = stations_affected[0]
        station2 = None if len(stations_affected) == 1 else stations_affected[1]

        network.apply_delay(delay_multiplier, station1, station2, line)

    return network


def get_entire_network():
    """
    Combine each sub network of each line to a full London network which can change
    based on disruption information

    Returns
    -------
    Network
        An entire underground network of London
    """
    if check_http_connection() is False:
        raise requests.RequestException("poor connection, please check the network")

    # Query the information of the network
    query_total_info = (
        "https://rse-with-python.arc.ucl.ac.uk/londontube-service/index/query"
    )
    response = requests.get(query_total_info, timeout=120)
    total_info = response.json()

    # The number of lines
    n_lines = int(total_info["n_lines"])
    n_stations = int(total_info["n_stations"])

    # Sum the Networks
    return sum([connectivity_of_line(line_ldx) for line_ldx in range(n_lines)], Network(n_stations, []))


def network_of_given_day(date=None):
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

    if date is not None:
        disruptions = disruption_info(date)
    else:
        disruptions = disruption_info()
    entire_network = get_entire_network()
    changed_network = apply_disruptions(entire_network, disruptions)

    return changed_network


def query_station_all_info():
    """

    Query station information for all stations.
    Return three types of dictionary, one is key of indices to value of station name,
    the second is from station name to indices, and the last one is getting longitude and latitude for
    each station.

    Returns
    -------
    dictionay
        The first dictionary gets station index as key and  station name as value.
        The second dictionary gets station name (in lowercase) as key and station index as value.
        The third dictionary gets station index as key and its position(latitude and longitude) as value.
    """

    if check_http_connection() is False:
        raise requests.RequestException("poor connection, please check the network")

    response = requests.get(
        "https://rse-with-python.arc.ucl.ac.uk/londontube-service/stations/query?id=all",
        timeout=300
    )
    station_info = pd.read_csv(StringIO(response.text))

    # dict(index, name)
    dict_indices_names = dict(
        zip(station_info["station index"], station_info["station name"])
    )

    # dic(name, index)
    # Set str.lowr() for consistent use
    dict_names_indices = dict(
        zip(station_info["station name"].str.lower(), station_info["station index"])
    )

    # dict({name, {latitude, longitude}})
    dict_position = station_info.set_index("station index")[
        ["latitude", "longitude"]
    ].to_dict("index")

    return dict_indices_names, dict_names_indices, dict_position


def convert_indices_to_names(station_indices):
    """
    Convert the station indices to corresponding names.

    Parameters
    ----------
    station_indices : list of int
        A list of station indices

    Returns
    -------
    list of str
        A list of corresponding names
    """

    dict_indices_names, _, _ = query_station_all_info()

    # Unexsited station is marked
    result = [
        dict_indices_names.get(index, "Unexisted station index")
        for index in station_indices
    ]

    return result


def convert_names_to_indices(station_names):
    """
    Convert a list of station names to corresponding indices

    Parameters
    ----------
    station_names : list of str
       A list of station names

    Returns
    -------
    list of int
       A list of corresponding indices
    """

    _, dict_names_indices, _ = query_station_all_info()
    # Unexisted station is marked as -1
    result = [dict_names_indices.get(name.lower(), -1) for name in station_names]

    return result
