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
    def adjacency_matrix(self) -> [[int]]:
        """
        Generate and return the adjacency matrix of the network.

        Returns
        -------
        list of list of int
            Adjacency matrix of the network.
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
        if not isinstance(other, Network):
            raise TypeError("The inputs should both be a network object ")

        # Copy the current network's edges
        new_edges = self.list_of_edges.copy()

        for other_edge in other.list_of_edges:
            # Check if they get same edge
            same_edge = False

            for i, self_edge in enumerate(new_edges):
                # Check if they get same edge in bi-directional condition
                if (
                    self_edge[0] == other_edge[0] and self_edge[1] == other_edge[1]
                ) or (self_edge[0] == other_edge[0] and self_edge[1] == other_edge[1]):
                    # Replace edge with smaller travel time if both have a same edge
                    if self_edge[2] > other_edge[2]:
                        new_edges[i] = other_edge
                    same_edge = True
                    break
            # If an other edge is a new edge then just append it to current edge list
            if not same_edge:
                new_edges.append(other_edge)

        return Network(self.n_nodes, new_edges)

    def distant_neighbours(self, n, v) -> [int]:
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
