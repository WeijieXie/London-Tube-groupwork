""" Module handling creation and manipulation of Network class """
from typing import List
import math
from queue import Queue
import heapq
import numpy as np


class Network:
    """
    Network class representing a network of stations and connections.

    Attributes
    ----------
    matrix : list[list[int]]
        Adjacency matrix of the network.

    edges : dict[tuple(int, int), list[tuple(int, int)]
        Dictionary where:
            - Keys are tuples representing (station1, station2) pairs.
            - Values are lists of lists representing [travel time, line_id] pairs.
    """

    def __init__(self, n_stations, edges):
        """
        Constructor for Network class.

        Params
        ------
        n_stations : int
            Number of stations for the Network.

        edges: list[tuple(int, int, int, int)] or list[list[int, int, int, int]]
            edge information provided as (station1, station2, weight, line) where:
                station1&2 - stations the edge represents travel between
                w - the weight, in this case travel time of the journey
                line - the line the journey belongs to

        Raises
        ------
        TypeError
            If the types of the params are not correct

        Examples
        --------
        >>> network = Network(4, [(0, 1, 5, 1), (1, 2, 3, 1), (2, 3, 4, 2)])
        >>> network.matrix.tolist()
        [[0, 5, 0, 0], [5, 0, 3, 0], [0, 3, 0, 4], [0, 0, 4, 0]]
        >>> sorted(network.edges.items())
        [((0, 1), [(5, 1)]), ((0, 2), []), ((0, 3), []), ((1, 2), [(3, 1)]), ((1, 3), []), ((2, 3), [(4, 2)])]
        """
        # Type checks on inputs
        if any([not isinstance(n_stations, int), isinstance(n_stations, bool)]):
            raise TypeError("Parameter n_stations must be of type int")
        if not all(
            all(
                isinstance(value, int) and not isinstance(value, bool) for value in edge
            )
            for edge in edges
        ):
            raise TypeError("Edge parameters must be of type int")
        if not all(len(edge) == 4 for edge in edges):
            raise TypeError("Edges must have 4 parameters")

        # Check no edge weights are negative
        if not all(edge[2] >= 0 for edge in edges):
            raise ValueError("Edges must have non-negative weights")

        # Check the edge stations are between 0 and n_stations
        if not all(0 <= station < n_stations for edge in edges for station in edge[:2]):
            raise ValueError("Edge stations must satisfy 0 <= station < n_stations")

        # The adjacency matrix
        self.matrix = np.zeros((n_stations, n_stations), dtype=int)

        # This dictionary is used to record all edges
        # We always use x < y in the key which allows easy assigning to matrix values
        self.edges = {
            key: [] for key in [((x, y)) for y in range(n_stations) for x in range(y)]
        }

        for edge in edges:
            self.add_edge(edge)

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

        Raises
        ------
        Value Error
            If the Networks are of different sizes
        """
        if self.n_nodes != other.n_nodes:
            raise ValueError(
                f"Networks cannot be combined with n_nodes {self.n_nodes} and {other.n_nodes}"
            )

        # Combined network
        integrated_network = Network(self.n_nodes, [])
        integrated_network.matrix = self.matrix.copy()
        integrated_network.edges = self.edges.copy()

        for key, all_lines in other.edges.items():
            for edge_line in all_lines:
                integrated_network.add_edge(key + tuple(edge_line))

        return integrated_network

    def add_edge(self, edge):
        """
        Adds an edge to the dict edges:
            - if an edge with the same line and stations already exists
                - it is replaced if the new edge is faster
                - the edge is not added otherwise
            - keeping the first edge in the stations list as the fastest
            - simply adding the edge if there are no edges yet between the stations

        Parameters
        ----------
        edge: tuple(int, int, int, int)
            A standard edge consisting of (station1, station2, weight, line)

        Examples
        --------
        >>> network = Network(3, [])
        >>> network.add_edge((0, 1, 10, 1))
        >>> network.edges
        {(0, 1): [(10, 1)], (0, 2): [], (1, 2): []}
        >>> network.add_edge((1, 2, 5, 2))
        >>> network.edges
        {(0, 1): [(10, 1)], (0, 2): [], (1, 2): [(5, 2)]}
        """
        # Ensure x < y
        pair = tuple(sorted(edge[:2]))
        value = edge[2:]
        all_lines = self.edges[pair]

        # If the new edge is 0, there is nothing to do
        if edge[2] == 0:
            return

        for i, edge_line in enumerate(all_lines):
            # If the line exists..
            if edge_line[1] == edge[3]:
                # If the new edge is faster..
                if edge[2] < edge_line[0]:
                    # Delete the existing edge
                    all_lines.pop(i)
                    break

                # Return if we reach here, since the new edge is slower
                return

        # Insert the edge into position 0 and update the matrix if it's the new fastest
        if all_lines == [] or edge[2] < all_lines[0][0]:
            all_lines.insert(0, value)

            self.matrix[pair] = edge[2]
            self.matrix[pair[::-1]] = edge[2]
        else:
            all_lines.append(value)

    def apply_delay(self, delay, station_idx, other_station_idx=None, line_idx=None):
        """
        Apply delay to multiplying the weight of all edges connected to the station.
        If other_station_idx is provided, the delay is only applied to edges between the two station.
        If line_idx is provided, the delay is only applied to edges with that line.

        Parameters
        ----------
        delay : int
            The travel time(weight) is multiplied by this factor
        station_idx : int
            The index of the affect station
        other_station_idx : int, optional
            The index of the other station (default is None)
        line_idx : int, optional
            The index of the delayed line (default is None)

        Raises
        ------
        ValueError
            If station_idx == other_station_idx
        """
        if station_idx == other_station_idx:
            raise ValueError(
                "Parameters station_idx and other_station_idx cannot be the same"
            )

        # Assemble station_pairs to apply delay to - (station, other_station) or all others if no other provided
        station_pairs = [
            tuple(sorted((station_idx, other)))
            for other in range(self.n_nodes)
            if other_station_idx in [None, other] and station_idx != other
        ]

        for pair in station_pairs:
            # Continue if no edges
            if self.edges[pair] == []:
                continue

            # Update weights of edges on the line, or all edges if no line provided
            self.edges[pair] = [
                (weight * delay if line_idx in [None, line] else weight, line)
                for weight, line in self.edges[pair]
            ]

            # Remove edges with weight 0
            self.edges[pair] = [edge for edge in self.edges[pair] if edge[0] != 0]

            # If no edges remain, set the matrix points to 0 and continue
            if self.edges[pair] == []:
                self.matrix[pair] = 0
                self.matrix[pair[::-1]] = 0
                continue

            # Move the fastest to the front
            fastest = []
            for i, edge in enumerate(self.edges[pair]):
                # If new fastest and non-zero then move to front
                if not fastest or edge[0] < fastest[0]:
                    fastest = [edge[0], i]

            self.edges[pair].insert(0, self.edges[pair].pop(fastest[1]))

            # Assign to the matrix
            self.matrix[pair] = self.edges[pair][0][0]
            self.matrix[pair[::-1]] = self.edges[pair][0][0]

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
        -----
        This method uses the well-known Breadth-First Search (BFS) to find nth-order neighbors in the network.

        A queue is used to 'visit' first the initial node, then its neighbours and their neighbors, and so on iteratively,
        until all n-th order neighbor nodes have been found.
        Visited nodes are tracked to not double back through the network.

        This method stops when all n-distant neighbor nodes have been found, to save computation time.

        Examples
        --------
        >>> network = Network(9, [])
        >>> matrix = np.array([
        ...     [0, 1, 0, 0, 0, 0, 0, 0, 0],
        ...     [1, 0, 2, 0, 4, 0, 0, 0, 0],
        ...     [0, 2, 0, 8, 0, 0, 0, 0, 0],
        ...     [0, 0, 8, 0, 1, 0, 0, 0, 0],
        ...     [0, 4, 0, 1, 0, 0, 0, 0, 0],
        ...     [0, 0, 0, 0, 0, 0, 5, 9, 0],
        ...     [0, 0, 0, 0, 0, 5, 0, 2, 0],
        ...     [0, 0, 0, 0, 0, 9, 2, 0, 0],
        ...     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ... ])
        >>> network.matrix = matrix
        >>> network.n_nodes = 9

        # Test for 1-distant neighbors
        >>> network.distant_neighbours(1, 0)
        [1]
        >>> network.distant_neighbours(1, 1)
        [0, 2, 4]

        # Test for 2-distant neighbors
        >>> network.distant_neighbours(2, 0)
        [1, 2, 4]

        # Test for nodes with no neighbors
        >>> network.distant_neighbours(1, 8)
        []

        # Test for isolated sub-network
        >>> network.distant_neighbours(1, 5)
        [6, 7]

        # Error handling: n <= 0
        >>> network.distant_neighbours(-1, 0)
        Traceback (most recent call last):
            ...
        ValueError: n must be > 0

        # Error handling: v out of range
        >>> network.distant_neighbours(1, 10)
        Traceback (most recent call last):
            ...
        IndexError: v must satisfy 0 <= v < n_nodes (9)
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

    @classmethod
    def dijkstra(cls, network, start_node, end_node):
        """
        Find the shortest path between the start and destination nodes using Dijkstra's algorithm.

        This method calculates the shortest path in terms of travel time between the specified start and destination nodes.
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
            The shortest path from the start node to the destination node as a list of node indices.
            Returns `None` if no path is found.
        total_cost : float
            The total travel time of the shortest path. Returns `None` if no path is found.

        Raises
        ------
        IndexError
            if start_node or end_node does not satisfy 0 <= v < n_nodes

        Notes
        -----
        The algorithm works by first initializing the distance to all nodes as infinity, except the start which is set to 0.
        It then iteratively relaxes the distances to the nodes by considering all unvisited neighbors of the current node.
        The process continues until all nodes are visited or the destination node's shortest path is determined.

        Examples
        --------
        >>> network = Network(4, [(0, 1, 1, 1), (1, 2, 2, 1), (2, 3, 3, 1)])
        >>> network.dijkstra(0, 3)
        ([0, 1, 2, 3], 6)
        >>> network.dijkstra(1, 3)
        ([1, 2, 3], 5)
        >>> network.dijkstra(0, 2)
        ([0, 1, 2], 3)
        """
        if not all(0 <= node < network.n_nodes for node in [start_node, end_node]):
            raise IndexError(
                f"start_node and end_node must satisfy 0 <= v < n_nodes ({network.n_nodes})"
            )

        nodes_num = network.n_nodes  # number of nodes
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
            for connected_node, travel_cost in enumerate(network.matrix[pop_node]):
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

        return (
            cls.construct_path(predecessor, start_node, end_node),
            tentative_costs[end_node],
        )

    @classmethod
    def construct_path(cls, predecessor, start_node, end_node):
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

        return []
