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
         
        nodes_num = self.n_nodes # number of nodes
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
            return self.construct_path(predecessor, start_node, end_node), tentative_costs[end_node]
        
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
        added_note = end_node # Locate the predecessor of the added_note
        
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
        
        
        
