from londontube.network import Network

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
