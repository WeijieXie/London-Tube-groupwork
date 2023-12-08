

def connectivity_of_line(line_index) -> Network:
    """query the web service for information about a particular line, and contruct a Network object that represent this line.

    :param line_index: index of the line
    :type line_index: int
    :return: Network of the line
    :rtype: Network
    """
    pass

def disruption_info(date):
    """retrive disruption info from web services

    :param date: given day
    :type date: str
    :return: dictionary of disruption information
    :rtype: dict()
    """
    pass

def network_of_given_day(date) -> Network:
    """retrieve the whole information of the given day and construct a Network object from this.

    :param date: given day
    :type date: str
    :return: Network representation of londontube
    :rtype: Network
    """
    pass