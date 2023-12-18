from typing import List
import numpy as np


class Network:
    """Network class representing a network of stations and connections.

    Attributes
    ----------
    matrix : List[List[int]]
        Adjacency matrix of the network.
    """

    def __init__(self, *args):
        """
        Construct a Network object.

        Parameters
        ----------
        n_stations : int
            Number of stations.
        list_of_edges : list of tuples (int, int, int)
            List of edges between nodes, where each tuple is (v1, v2, weight).
        """
        if len(args) == 1:
            self.matrix = args[0]
        elif len(args) == 2:
            n_stations = args[1]
            list_of_edges = args[2]
            adjacency_matrix = np.empty((n_stations, n_stations), dtype=int)
            for n in range(n_stations):
                adjacency_matrix[list_of_edges[0], list_of_edges[1]] = list_of_edges[2]
            self.matrix = adjacency_matrix

    @classmethod
    def from_adjacency_matrix(cls, matrix):
        return cls(matrix)

    @property
    def n_nodes(self) -> int:
        """
        Return the number of nodes in the network.

        Returns
        -------
        int
            Number of nodes in the network.
        """
        return len(self.matrix)

    @property
    def adjacency_matrix(self) -> List[List[int]]:
        """
        Generate and return the adjacency matrix of the network.

        Returns
        -------
        list of list of int
            Adjacency matrix of the network.
        """
        return self.matrix

    def __add__(self, other):
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
        array1 = self.matrix
        array2 = other.matrix

        mask = (array1 != 0) & (
            array2 != 0
        )  # when there is an edge between, it is True

        result1 = np.minimum(
            array1, array2
        )  # when there is an edge, set the time the shorter one
        result2 = array1 + array2  # when there is no edge, set it the nozero one

        result = np.where(mask, result1, result2)

        return self.from_adjacency_matrix(result)

    def add_delay(self, node1, node2, delay):
        """Adding delay to a specific edge between two nodes

        Parameters
        ----------
        node1 : int
            index of start node
        node2 : int
            index of destination node
        """
        normal = self.matrix[node1, node2]
        self.matrix[node1, node2] = delay * normal
        self.matrix[node2, node1] = delay * normal

    def remove_edges(self, node):
        """Remove all edges connected to the given node

        Parameters
        ----------
        node : int
            index of a given node
        """
        self.matrix[node, 0 : node + 1] = np.zeros(node + 1)
        self.matrix[0 : node + 1, node] = np.zeros(node + 1)


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
        #Breadth-first search for nth order neighbours:
        dim = len(self.matrix)
        visited = [False for i in range(dim)]
        queue = [v]
        distance = [float('inf') for i in range(dim)]

        visited[v] = True
        distance[v] = 0
        while queue:
            node = queue.pop(0)
            for i in range(dim):
                if not visited[i] and adjacency_matrix[node][i] > 0:
                    visited[i] = True
                    distance[i] = distance[node] + 1
                    queue.append(i)
        return [j for j, x in enumerate(distance) if 0 < x <= n]

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
