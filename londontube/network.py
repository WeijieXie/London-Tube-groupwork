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
                (edge[0], edge[1], edge[2], edge[3])
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
        
        integrated_network_edges = self.edges.copy()
        integrated_network = Network(self.n_nodes, integrated_network_edges)

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

    # The first disruption type
    def delay_to_specific_line_one_station(
        self, line_idx, station_idx, delay_multiplier
    ):
        """
        It is one type of disruptions that one station in a line is delayed.
        Thus, all stations that connected to this station in the line are delayed.

        Parameters
        ----------
        line_idx : int
            The index here is the number that represents the delayed line
        station_idx : int
            The index of one affected station
        delay_multiplier : int
            The travel time(weight) is multiplied by this factor
        """

        for i, edge in enumerate(self.edges):
            # Check which edge in the network correspond to this line and the affected statioin
            if edge[3] == line_idx and (
                edge[0] == station_idx or edge[1] == station_idx
            ):
                updated_weight = int(edge[2] * delay_multiplier)
                self.edges[i] = (edge[0], edge[1], updated_weight, edge[3])
                self.matrix[edge[0], edge[1]] = updated_weight
                self.matrix[edge[1], edge[0]] = updated_weight

    # The second disruption type
    def delay_to_specific_line_between_stations(
        self, line_idx, station1_idx, station2_idx, delay_multiplier
    ):
        """
        This function is applied to a situation where connection between two stations on a line is delayed.
        Thus the travel time between these two stations on that line increases.

        Parameters
        ----------
        line_idx : int
            The index of the line
        station1_idx : int
            The index of the station1
        station2_idx : int
            The index of the station2
        delay_multiplier : int
            The travel time(weight) is multiplied by this factor
        """

        for i, edge in enumerate(self.edges):
            if edge[3] == line_idx and (
                (edge[0] == station1_idx and edge[1] == station2_idx)
                or (edge[0] == station2_idx and edge[1] == station1_idx)
            ):
                updated_weight = int(edge[2] * delay_multiplier)
                self.edges[i] = (edge[0], edge[1], updated_weight, edge[3])
                self.matrix[edge[0], edge[1]] = updated_weight
                self.matrix[edge[1], edge[0]] = updated_weight

    # The third disruption type
    def delay_to_entire_one_station(self, station_idx, delay_multiplier):
        """
        This function is applied to a situation where one station is delayed for the entire network.
        Thus the connections of each line that contains this station is delayed.


        Parameters
        ----------
        station_idx : int
            The index of the affected station
        delay_multiplier : int
            The travel time(weight) is multiplied by this factor
        """

        for i, edge in enumerate(self.edges):
            if edge[0] == station_idx or edge[1] == station_idx:
                updated_weight = int(edge[2] * delay_multiplier)
                self.edges[i] = (edge[0], edge[1], updated_weight, edge[3])
                self.matrix[edge[0], edge[1]] = updated_weight
                self.matrix[edge[1], edge[0]] = updated_weight

    # The fourth disruption type
    def delay_to_entire_between_stations(
        self, station1_idx, station2_idx, delay_multiplier
    ):
        """
        This function is applied to a situation where connection between two stations for entire network is delayed.
        Thus the travel time between these two stations for every line that contains this connection increases.

        Parameters
        ----------
        station1_idx : int
            The index of the first affected station
        station2_idx : int
            The index of the second affected station
        delay_multiplier : int
            The travel time(weight) is multiplied by this factor
        """
        
        for i, edge in enumerate(self.edges):
            if (edge[0] == station1_idx and edge[1] == station2_idx) or (
                edge[0] == station2_idx and edge[1] == station1_idx
            ):
                updated_weight = int(edge[2] * delay_multiplier)
                self.edges[i] = (edge[0], edge[1], updated_weight, edge[3])
                self.matrix[edge[0], edge[1]] = updated_weight
                self.matrix[edge[1], edge[0]] = updated_weight

    # The fifth disruption type
    def delay_to_closure(self, station_list):
        """
        When the delay multiplier is 0, that means the station is closed, which affects the whole network.

        Parameters
        ----------
        station_list : List
            A list of closed stations
        """


        # Keep the edges that are not affected
        self.edges = [
            edge
            for edge in self.edges
            if edge[0] not in station_list and edge[1] not in station_list
        ]

        # Set all the weight connected to stations in station to 0
        for affected_station in station_list:
            self.matrix[affected_station, :] = 0
            self.matrix[:, affected_station] = 0
            



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
        visited = [0 for _ in range(self.matrix.shape[0])]
        visited[v] = 1
        visiting_queue = Queue()
        visiting_queue.put((v, 0))
        neighbours = []
        while not visiting_queue.empty():
            current_node, depth = visiting_queue.get()
            if depth > n:
                return neighbours
            if depth > 0:
                neighbours.append(current_node)
            for i in range(self.matrix.shape[0]):
                if self.matrix[current_node, i] != 0 and not visited[i]:
                    visited[i] = 1
                    visiting_queue.put((i, depth + 1))
        return neighbours


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
