from typing import List
import numpy as np
import math
from queue import Queue
import heapq


class Network:
    """
    Network class representing a network of stations and connections.

    Attributes
    ----------
    matrix : list[list[int]]
        Adjacency matrix of the network.

    edge: list[tuple()]
        Each edge information in a network is stored as a tuple in a list.
        The content of a tuple is (edge[0], edge[1], w, id) where station1 and station2 are two stations,
        w is the weight(travel time) between them and id is what line this edge belongs to.

    edges_record : dict[tuple[int, int], list[tuple(int, int)]
        Dictionary where:
            - Keys are tuples representing (station1, station2) pairs.
            - Values are lists of tuples representing (travel time, line_id) pairs.
    """

    def __init__(self, n_stations, list_of_edges):
        # The adjacency matrix
        self.matrix = np.zeros((n_stations, n_stations), dtype=int)
        # List of edges
        self.edges = []
        # This dictionary is used to record all edges
        self.edges_record = {}
        for edge in list_of_edges:
            self.edges.append(
                (edge[0], edge[1], edge[2], edge[3])
            )  # edge[3] is the identifier of a line
            self.matrix[edge[0], edge[1]] = edge[2]
            self.matrix[edge[1], edge[0]] = edge[2]
            # Make sure that we store the edges
            self.edges_record.setdefault((edge[0], edge[1]), []).append(
                (edge[2], edge[3])
            )
            self.edges_record.setdefault((edge[1], edge[0]), []).append(
                (edge[2], edge[3])
            )

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
        integrated_network.edges_record = self.edges_record.copy()

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
                        # Replace it with faster one
                        integrated_network.edges[i] = other_edge
                        integrated_network.matrix[other_edge[0]][
                            other_edge[1]
                        ] = other_edge[2]
                        integrated_network.matrix[other_edge[1]][
                            other_edge[0]
                        ] = other_edge[2]
                    same_found = True
                    break
            if not same_found:
                # New edge is added when no matching
                integrated_network.edges.append(other_edge)
                integrated_network.matrix[other_edge[0]][other_edge[1]] = other_edge[2]
                integrated_network.matrix[other_edge[1]][other_edge[0]] = other_edge[2]

        # Update the edges_record attribute from 'other' matrix
        for edge_key, time_and_lineid in other.edges_record.items():
            if edge_key in integrated_network.edges_record:
                # Add new tuple to exsiting edge_key's value
                integrated_network.edges_record[edge_key].extend(time_and_lineid)
                integrated_network.edges_record[edge_key].sort(
                    key=lambda i: i[0]
                )  # Sort by the travel time
            else:
                integrated_network.edges_record[edge_key] = time_and_lineid

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

                # Update the corresponding edge in edge_record with new weight
                self.edges_record[(edge[0], edge[1])] = [
                    (updated_weight, edge[3]) if line == edge[3] else (weight, line)
                    for weight, line in self.edges_record.get((edge[0], edge[1]), [])
                ]
                self.edges_record[(edge[1], edge[0])] = [
                    (updated_weight, edge[3]) if line == edge[3] else (weight, line)
                    for weight, line in self.edges_record.get((edge[1], edge[0]), [])
                ]

        # Find alternative paths that do not use the disrupted station as an endpoint
        for (station1, station2), time_plus_lineid in self.edges_record.items():
            if station_idx not in (station1, station2):
                continue

            # Get the edges that are not affected by delay
            not_affected_edges = [
                (weight, line) for weight, line in time_plus_lineid if line != line_idx
            ]
            if not not_affected_edges:
                continue

            # Choose the fastest alternative edge which is not from the disrupted line
            fastest_alternative = min(not_affected_edges, key=lambda tuple: tuple[0])

            # Update the matrix and edges list with the fastest alternative
            # If the fastest alternative is better than the affected travel time
            if self.matrix[station1][station2] > fastest_alternative[0]:
                self.matrix[station1][station2] = fastest_alternative[0]
                self.matrix[station2][station1] = fastest_alternative[0]
                for i, edge in enumerate(self.edges):
                    if {edge[0], edge[1]} == {station1, station2}:
                        self.edges[i] = (
                            station1,
                            station2,
                            fastest_alternative[0],
                            fastest_alternative[1],
                        )

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

                # Update edges_record with the new weight
                if (edge[0], edge[1]) in self.edges_record:
                    self.edges_record[(edge[0], edge[1])] = [
                        (updated_weight, edge[3]) if line == edge[3] else (weight, line)
                        for weight, line in self.edges_record[(edge[0], edge[1])]
                    ]
                if (edge[1], edge[0]) in self.edges_record:
                    self.edges_record[(edge[1], edge[0])] = [
                        (updated_weight, edge[3]) if line == edge[3] else (weight, line)
                        for weight, line in self.edges_record[(edge[1], edge[0])]
                    ]

        # Re-evaluate the edges after delay is applied

        # Get the edges that has the connection between station1 and 2
        related_edges = self.edges_record.get(
            (station1_idx, station2_idx), []
        ) + self.edges_record.get((station2_idx, station1_idx), [])

        # Get the edges that are not affected by this specific line delay
        not_affected_edges = [
            (weight, line) for weight, line in related_edges if line != line_idx
        ]

        if not_affected_edges:
            # Choose the fastest alternative edge
            fastest_alternative = min(not_affected_edges, key=lambda tuple: tuple[0])

            # Update the matrix and edges list if fastest alternative is better
            if self.matrix[station1_idx][station2_idx] > fastest_alternative[0]:
                self.matrix[station1_idx][station2_idx] = fastest_alternative[0]
                self.matrix[station2_idx][station1_idx] = fastest_alternative[0]
                for i, (v1, v2, _, _) in enumerate(self.edges):
                    if {v1, v2} == {station1_idx, station2_idx}:
                        self.edges[i] = (
                            station1_idx,
                            station2_idx,
                            fastest_alternative[0],
                            fastest_alternative[1],
                        )

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

        for stations, time_plus_lineid in self.edges_record.items():
            if station_idx in stations:
                self.edges_record[stations] = [
                    (weight * delay_multiplier, line)
                    for weight, line in self.edges_record[stations]
                ]

        # Re-evaluate the edges after delay is applied

        for (station1, station2), time_plus_lineid in self.edges_record.items():
            if station_idx in (station1, station2):
                # Find the fast alternative
                fastest_alternative = min(time_plus_lineid, key=lambda tuple: tuple[0])

                # Update the matrix if fastest_alternative is better
                if self.matrix[station1][station2] > fastest_alternative[0]:
                    self.matrix[station1][station2] = fastest_alternative[0]
                    self.matrix[station2][station1] = fastest_alternative[0]

                    # Update edge list
                    for i, edge in enumerate(self.edges):
                        if {edge[0], edge[1]} == {station1, station2}:
                            self.edges[i] = (
                                station1,
                                station2,
                                fastest_alternative[0],
                                fastest_alternative[1],
                            )

        # Re-evaluate the edges after delay is applied
        for (station1, station2), time_plus_lineid in self.edges_record.items():
            if station_idx in (station1, station2):
                fastest_alternative = min(time_plus_lineid, key=lambda tuple: tuple[0])
                # Update the matrix if a better path is found
                if self.matrix[station1][station2] > fastest_alternative[0]:
                    self.matrix[station1][station2] = fastest_alternative[0]
                    self.matrix[station2][station1] = fastest_alternative[0]
                    for i, edge in enumerate(self.edges):
                        if {edge[0], edge[1]} == {station1, station2}:
                            self.edges[i] = (
                                station1,
                                station2,
                                fastest_alternative[0],
                                fastest_alternative[1],
                            )

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

        edge_keys = [(station1_idx, station2_idx), (station2_idx, station1_idx)]
        for edge_key in edge_keys:
            if edge_key in self.edges_record:
                self.edges_record[edge_key] = [
                    (weight * delay_multiplier, line)
                    for weight, line in self.edges_record[edge_key]
                ]

        # Re-evaluate the edges after delay is applied

        # Combine edges
        related_edges = self.edges_record.get(
            (station1_idx, station2_idx), []
        ) + self.edges_record.get((station2_idx, station1_idx), [])

        fastest_alternative = min(related_edges, key=lambda tuple: tuple[0])

        # Update the matrix and edges list with the best alternative if it is better than the current connection
        if self.matrix[station1_idx][station2_idx] > fastest_alternative[0]:
            self.matrix[station1_idx][station2_idx] = fastest_alternative[0]
            self.matrix[station2_idx][station1_idx] = fastest_alternative[0]
            for i, edge in enumerate(self.edges):
                if {edge[0], edge[1]} == {station1_idx, station2_idx}:
                    self.edges[i] = (
                        station1_idx,
                        station2_idx,
                        fastest_alternative[0],
                        fastest_alternative[1],
                    )

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
            N-distant parameter, must be greater than 0.
        v : int
            Index of a node.

        Returns
        -------
        neighbours : list of int
            List of indexes of nodes that are n-distant neighbours.

        Raises
        ------
        IndexError
            if v does not satisfy 0 <= v < n_nodes
        ValueError
            if n <= 0

        Notes
        -------
        This method uses the well-known Breadth-First Search (BFS) to find nth-order neighbors in the network.

        A queue is used to 'visit' first the initial node, then its neighbours and their neighbors, and so on iteratively,
        until all n-th order neighbor nodes have been found. Visited nodes are tracked to not double back through the network.

        This method stops when all n-distant neighbor nodes have been found, to save computation time.
        """
        # Check v in range
        if not 0 <= v < self.n_nodes:
            raise IndexError(f"v must satisfy 0 <= v < n_nodes ({self.n_nodes})")

        # Check n > 0
        if n <= 0:
            raise ValueError("n must be > 0")

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
        return sorted(neighbours)

    def dijkstra(self, start_node, end_node):
        """
        Find the shortest path between the start and destination nodes using Dijkstra's algorithm.

        This method calculates the shortest path in terms of travel time between the specified start and destination nodes in the network.
        It uses Dijkstra's algorithm, which is an algorithm for finding the shortest paths between nodes in a graph.

        Parameters
        ----------
        start_node : int
            Index of the start node in the network.
        end_node : int
            Index of the destination node in the network.

        Returns
        -------
        path : list of int
            The shortest path from the start node to the destination node as a list of node indices. Returns `None` if no path is found.
        total_cost : float
            The total travel time of the shortest path. Returns `None` if no path is found.

        Raises
        ------
        IndexError
            if start_node or end_node does not satisfy 0 <= v < n_nodes

        Notes
        -----
        The algorithm works by first initializing the distance to all nodes as infinity, except for the start node, which is set to 0.
        It then iteratively relaxes the distances to the nodes by considering all unvisited neighbors of the current node.
        The process continues until all nodes are visited or the destination node's shortest path is determined.

        Examples
        --------
        >>> n_stations = 4
        >>> list_of_edge = [(0, 1, 3),
                            (1, 2, 3),
                            (1, 3, 4),
                            (2, 3, 5)]
        >>> network = Network(n_stations, list_of_edge)
        >>> network.dijkstra(0, 2)
        ([0, 1, 2], 5)
        >>> network.dijkstra(0, 3)
        ([0, 1, 3], 7)
        """
        if not all(0 <= node < self.n_nodes for node in [start_node, end_node]):
            raise IndexError(f"start_node and end_node must satisfy 0 <= v < n_nodes ({self.n_nodes})")

        nodes_num = self.n_nodes  # number of nodes
        visited_list = [False] * nodes_num
        # Set the tentative cost
        tentative_costs = [math.inf] * nodes_num
        tentative_costs[start_node] = 0
        predecessor = [None] * nodes_num

        # Use priority_queue to track smallest tentative cost
        priority_queue = [(0, start_node)]

        while priority_queue:
            smallest_cost, pop_node = heapq.heappop(priority_queue)

            # If one node has already been visited skip it
            if visited_list[pop_node]:
                continue

            visited_list[pop_node] = True

            # When the destination appears
            if pop_node == end_node:
                break

            # Check the connected nodes of the popped node
            for connected_node, travel_cost in enumerate(self.matrix[pop_node]):
                # Make sure there is a connection
                if travel_cost > 0 and not visited_list[connected_node]:
                    sum_cost = smallest_cost + travel_cost
                    # When the shorter path to this connected node is found
                    if sum_cost < tentative_costs[connected_node]:
                        tentative_costs[connected_node] = sum_cost
                        predecessor[connected_node] = pop_node
                        heapq.heappush(priority_queue, (sum_cost, connected_node))

        if tentative_costs[end_node] == math.inf:
            return None, None  # Indicates that no path was found
        else:
            return (
                self.construct_path(predecessor, start_node, end_node),
                tentative_costs[end_node],
            )

    def construct_path(self, predecessor, start_node, end_node):
        """
        Construct the shortest path from the start node to the destination node.

        Parameters
        ----------
        predecessor : list of int
            Array containing the index of the preceding node in the shortest path for each node in the network.
        start_node : int
            Index of the start node in the network.
        end_node : int
            Index of the destination node in the network.

        Returns
        -------
        path_list : list of int
            The constructed shortest path from the start node to the destination node as a list of node indices.

        Notes
        -----
        This method is used as a helper for Dijkstra's algorithm.
        It backtracks from the destination node using the `predecessor` array to construct the shortest path.

        Examples
        --------
        >>> predecessor = [None, 0, 1, 5, 1, 2]
        >>> construct_path(predecessor, 0, 3)
        [0, 1, 2, 5, 3]

        >>> predecessor = [None, 0, 0]
        >>> construct_path(predecessor, 0, 4)
        [0, 4]
        """
        path_list = []
        added_note = end_node  # Locate the predecessor of the added_note

        # The predecessor of the start node is None
        while added_note is not None:
            path_list.append(added_note)
            added_note = predecessor[added_note]

        # The end node is at the start in the path list
        path_list.reverse()

        if path_list[0] == start_node:
            return path_list
        else:
            return []
