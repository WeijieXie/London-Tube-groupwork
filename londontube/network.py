class Network:
    """Network class
    
    attributes:
    n_stations: int: number of nodes in the network
    list_of_edges: [(int,int,int)]: list of edges in the network, a edge consists of two indexes of nodes and a weight between nodes.
    adjacency_matrix: [[int]]: the adjacency matrix of the network
    """
    
    def __init__(self, n_stations, list_of_edges):
        """construct a Network obejcts

        :param n_stations: number of stations
        :type n_stations: int
        :param list_of_edges: list of edges between v1 to v2 with weight w
        :type list_of_edges: [(int,int,int)]
        """
        self.n_stations = n_stations
        self.list_of_edges = list_of_edges
    
    @property
    def n_nodes(self) -> int:
        """return the number of nodes in the network

        :return: number of nodes in the network
        :rtype: int
        """
        pass
    
    @property
    def adjacency_matrix(self) -> [[int]]:
        """generate and return adjacency_matrix of the network

        :return: adjacency matrix
        :rtype: [[int]]
        """
        pass
    
    def distant_neighbours(self, n, v) -> [int]:
        """find the n-distant neighbours of a particular node

        :param n: n-distant
        :type n: int
        :param v: index of a ndoe
        :type v: int
        :return: list of indexes of nodes
        :rtype: [int]
        """
        pass
    
    def dijkstra(self, start_node, dest_node) -> [int]:
        """find the shortest path from start node to destination node using given network

        :param start_node: index of start node
        :type start_node: int
        :param dest_node: index of destination node
        :type dest_node: int
        :return: list of indexes of nodes
        :rtype: [int]
        """
        pass
    
    def __add__(self, other) -> Network:
        """support the "+" operation for Network

        :param other: the Network to be added
        :type other: Network
        :return: combined Network
        :rtype: Network
        """
        pass