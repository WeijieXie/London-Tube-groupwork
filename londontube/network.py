from typing import List


class Network:
    """Network class representing a network of stations and connections.

    Attributes
    ----------
    n_stations : int
        Number of nodes in the network.
    list_of_edges : list of tuples
        List of edges in the network, where each edge consists of two indexes of nodes and a weight between nodes.
    """

    def __init__(self, n_stations, list_of_edges):
        """
        Construct a Network object.

        Parameters
        ----------
        n_stations : int
            Number of stations.
        list_of_edges : list of tuples (int, int, int)
            List of edges between nodes, where each tuple is (v1, v2, weight).
        """
        self.n_stations = n_stations
        self.list_of_edges = list_of_edges

    @property
    def n_nodes(self) -> int:
        """
        Return the number of nodes in the network.

        Returns
        -------
        int
            Number of nodes in the network.
        """
        return self.n_stations

    @property
    def adjacency_matrix(self) -> List[List[int]]:
        """
        Generate and return the adjacency matrix of the network.

        The adjacency matrix is a 2D list where each element represents
        the connection between nodes in the network. The value at a
        specific row and column indicates the weight of an edge between two nodes.

        Returns
        -------
        List[List[int]]
            Adjacency matrix of the network. Each inner list represents
            a row in the matrix, and each integer in the inner list
            represents the edge weight between nodes.
        """
        adjacency_matrix = [
            [0 for _ in range(self.n_stations)] for _ in range(self.n_stations)
        ]

        for connection in self.list_of_edges:
            adjacency_matrix[connection[0]][connection[1]] = connection[2]
            adjacency_matrix[connection[1]][connection[0]] = connection[2]

        return adjacency_matrix

    def distant_neighbours(self, n, v) -> List[int]:
        """
        Find the n-distant neighbours of a particular node.

        Parameters
        ----------
        n : int
            N-distant parameter.
        v : int
            Index of a node.

        Returns
        -------
        list of int
            List of indexes of nodes that are n-distant neighbours.
        """
        pass

    def dijkstra(self, start_node, dest_node) -> [int]:
        """
        Find the shortest path from the start node to the destination node using the given network.

        Parameters
        ----------
        start_node : int
            Index of the start node.
        dest_node : int
            Index of the destination node.

        Returns
        -------
        list of int
            List of indexes of nodes forming the shortest path.
        """
        pass

    def __add__(self, other) -> "Network":
        """
        Support the "+" operation for Network, combining two networks.

        Parameters
        ----------
        other : Network
            The Network to be added.

        Returns
        -------
        Network
            Combined Network.
        """
        pass
