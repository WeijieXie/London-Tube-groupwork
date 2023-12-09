from londontube.network import Network
import requests


def connectivity_of_line(line_index):
    """
    Query the web service for information about a particular line, and contruct a Network object that represent this line.

    Parameters
    ----------
    line_index : int
        Index of the line.

    Returns
    -------
    Network
        Network of the line.
    """
    pass


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
