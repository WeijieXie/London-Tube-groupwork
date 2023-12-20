from typing import List
import numpy as np
import math
from queue import Queue


class Network:
    """
    Network class representing a network of stations and connections.

    Attributes
    ----------
    matrix : List[List[int]]
        Adjacency matrix of the network.

    edge: List[tuple()]
        Each edge information in a network is stored as a tuple in a list.
        The content of a tuple is (v1, v2, w, id) where v1 and v2 are two stations,
        w is the weight(travel time) between them and id is what line this edge belongs to.
    """

    def __init__(self, n_stations, list_of_edges):
        # The adjacency matrix
        self.matrix = np.zeros((n_stations, n_stations), dtype=int)
        # List of edges
        self.edges = []
        for edge in list_of_edges:
            self.edges.append(
                edge[0], edge[1], edge[2], edge[3]
            )  # edge[3] is the identifier of a line
            self.matrix[edge[0], edge[1]] = edge[2]
            self.matrix[edge[1], edge[0]] = edge[2]

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

        # Combined network
        integrated_network = Network()
        integrated_network.edges = self.edges.copy()

        for other_edge in other.edges:
            same_found = False
            for i, self_edge in enumerate(integrated_network.edges):
                # The graph is bidirectional.
                # Check for two conditions where the same edge appears.
                if (self_edge[0], self_edge[1]) == (other_edge[0], other_edge[1]) or (
                    self_edge[0],
                    self_edge[1],
                ) == (other_edge[1], other_edge[0]):
                    if self_edge[2] > other_edge[2]:
                        integrated_network.edges[i] = other_edge
                    same_found = True
                    break
            if not same_found:
                integrated_network.edges.append(other_edge)

        integrated_network.matrix = np.where(
            (self.matrix != 0) & (other.matrix != 0),
            np.minimum(self.matrix, other.matrix),
            self.matrix + other.matrix,
        )

        return integrated_network

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

        # Breadth-first search for nth order neighbours:
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
        visited = [False for _ in range(self.matrix.shape[0])]
        tentative_costs = [math.inf for _ in range(self.matrix.shape[0])]
        tentative_costs[start_node] = 0
        previous = [start_node for _ in range(self.matrix.shape[0])]
        while not all(visited):
            current = None
            minimum = math.inf
            for i in range(len(visited)):
                if not visited[i] and tentative_costs[i] <= minimum:
                    minimum = tentative_costs[i]
                    current = i
            visited[current] = True
            for i in range(self.matrix.shape[0]):
                if self.matrix[current, i] != 0 and not visited[i]:
                    proposed_cost = tentative_costs[current] + self.matrix[current, i]
                    if tentative_costs[i] > proposed_cost:
                        tentative_costs[i] = proposed_cost
                        previous[i] = current

        return self.reconstruct_path(previous, start_node, dest_node)

    def reconstruct_path(self, previous, start_node, dest_node):
        path = []
        current = dest_node
        while True:
            path.append(current)
            current = previous[current]
            if current == start_node:
                path.append(start_node)
                return path[::-1]
