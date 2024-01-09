""" Tests for the network class """
from unittest.mock import MagicMock
import pytest
import numpy as np
from londontube.network import Network


@pytest.fixture()
def sample_edges_expected():
    """ Setup sample edges """
    yield {
        (0, 1): [(10, 0)],
        (0, 2): [(40, 1)],
        (1, 2): [(20, 0), (50, 2)],
        (1, 3): [(30, 2)]
    }


@pytest.fixture()
def sample_edges(sample_edges_expected):
    """ Setup sample edges """
    yield [key + tuple(value) for key, values in sample_edges_expected.items() for value in values]


@pytest.fixture()
def sample_matrix_expected():
    """ Setup sample expected adjacency matrix """
    yield np.array([
        [0, 10, 40, 0],
        [10, 0, 20, 30],
        [40, 20, 0, 0],
        [0, 30, 0, 0]
    ])


@pytest.fixture()
def sample_network(sample_edges):
    """ Setup sample network """
    # Setting up a small network to use in the tests
    yield Network(4, sample_edges)


class TestInit:
    """Test basic functionality of the Network class"""

    @pytest.mark.parametrize(
        "edges, matrix_expected, edges_expected",
        [
            (
                # All edges added with no replacements
                None,
                None,
                None
            ),
            (
                # Include two 0 weight edges, one added, one not
                [(0, 1, 0, 0), (0, 3, 0, 0)],
                None,
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(20, 0), (50, 2)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # One edge replaced
                [(1, 2, 10, 0)],
                np.array([
                    [0, 10, 40, 0],
                    [10, 0, 10, 30],
                    [40, 10, 0, 0],
                    [0, 30, 0, 0]
                ]),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(10, 0), (50, 2)],
                    (1, 3): [(30, 2)]
                }
            ),
        ]
    )
    def test_init_positive(
            self, sample_edges, sample_edges_expected, sample_matrix_expected, edges, edges_expected, matrix_expected
    ):
        """ Test positive case init """
        edges = sample_edges + (edges or [])
        edges_expected = edges_expected or sample_edges_expected
        matrix_expected = sample_matrix_expected if matrix_expected is None else matrix_expected

        network = Network(4, edges)

        assert network.n_nodes == 4  # Check if nodes are correctly set

        # Check if edges are correctly set
        for key, value in network.edges.items():
            assert value == edges_expected.get(key, []), f"key {key}"

        assert np.array_equal(
            network.matrix,
            matrix_expected
        )

    @ pytest.mark.parametrize("n_stations", [.1, True, ''])
    def test_init_n_stations_type_error(self, n_stations):
        """ Test init throws error when n_stations is not of type int """
        with pytest.raises(TypeError) as e_info:
            Network(n_stations, [])
        assert str(e_info.value) == "Parameter n_stations must be of type int"

    @ pytest.mark.parametrize(
        "edges",
        [
            [[.1, 1, 1, 1]],
            [[1, 1, True, 1]],
            [[1, "", 1, 1]],
            [[1, 1,], [1, 1, 1, .1]]
        ]
    )
    def test_init_edges_non_int_type_error(self, edges):
        """ Test init throws error when any edge parameter is not an int """
        with pytest.raises(TypeError) as e_info:
            Network(2, edges)
        assert str(e_info.value) == "Edge parameters must be of type int"

    @ pytest.mark.parametrize(
        "edges",
        [
            [[1, 1]],
            [[1, 1, 1, 1, 1]],
            [[1, 1,], [1, 1, 1, 1]]
        ]
    )
    def test_init_edges_wrong_len_type_error(self, edges):
        """ Test init throws error when any edge does not have 4 parameters """
        with pytest.raises(TypeError) as e_info:
            Network(2, edges)
        assert str(e_info.value) == "Edges must have 4 parameters"

    @ pytest.mark.parametrize(
        "edges",
        [
            [[1, 1, -1, 1]],
            [[1, 1, 0, 1], [1, 1, -1, 1]]
        ]
    )
    def test_init_edges_neg_weight_value_error(self, edges):
        """ Test init throws ValueError when any edge has a negative weight """
        with pytest.raises(ValueError) as e_info:
            Network(2, edges)
        assert str(e_info.value) == "Edges must have non-negative weights"

    @ pytest.mark.parametrize(
        "edges",
        [
            [[-1, 1, 1, 1]],
            [[1, 1, 1, 1], [1, -1, 1, 1]],
            [[1, 1, 1, 1], [2, 1, 1, 1]],
            [[1, 2, 1, 1]]
        ]
    )
    def test_init_edges_station_value_error(self, edges):
        """ Test init throws ValueError when any station < 0 or >= n_stations """
        with pytest.raises(ValueError) as e_info:
            Network(2, edges)
        assert str(e_info.value) == "Edge stations must satisfy 0 <= station < n_stations"

    @ pytest.mark.parametrize(
        "edges_all, matrix_expected, edges_expected",
        [
            # All added
            (
                [
                    [(1, 0, 10, 0), (1, 2, 20, 0)],
                    [(0, 2, 40, 1), (1, 2, 50, 2)],
                    [(1, 3, 30, 2)]
                ],
                None,
                None
            ),
            # All same line, 1 replaced, 1 not
            (
                [
                    [(1, 0, 10, 0), (1, 2, 50, 0)],
                    [(1, 0, 20, 0), (1, 2, 20, 0)],
                ],
                np.array([
                    [0, 10, 0],
                    [10, 0, 20],
                    [0, 20, 0],
                ]),
                {
                    (0, 1): [(10, 0)],
                    (1, 2): [(20, 0)]
                }
            ),
            # Different lines, all added but matrix unchanged
            (
                [
                    [(1, 0, 10, 0), (1, 2, 50, 0)],
                    [(1, 0, 20, 1), (1, 2, 20, 1)],
                ],
                np.array([
                    [0, 10, 0],
                    [10, 0, 20],
                    [0, 20, 0],
                ]),
                {
                    (0, 1): [(10, 0), (20, 1)],
                    (1, 2): [(20, 1), (50, 0)]
                }
            ),
            # 1 is closed in the original and replaced, another is closed in the new and not replaced
            (
                [
                    [(1, 0, 0, 0), (1, 2, 20, 0)],
                    [(1, 0, 10, 0), (1, 2, 0, 0)],
                ],
                np.array([
                    [0, 10, 0],
                    [10, 0, 20],
                    [0, 20, 0],
                ]),
                {
                    (0, 1): [(10, 0)],
                    (1, 2): [(20, 0)]
                }
            ),
        ]
    )
    def test_add_positive_case(
        self, sample_edges_expected, sample_matrix_expected, matrix_expected, edges_all, edges_expected
    ):
        """ Test __add__ function positive case """
        edges_expected = edges_expected or sample_edges_expected
        matrix_expected = sample_matrix_expected if matrix_expected is None else matrix_expected

        n_stations = max(edge[1] for edges in edges_all for edge in edges) + 1
        network = sum([Network(n_stations, edges) for edges in edges_all], Network(n_stations, []))

        for key, value in network.edges.items():
            assert value == edges_expected.get(key, []), f"key {key}"

        assert np.array_equal(network.matrix, matrix_expected)
        assert network.n_nodes == n_stations

    def test_add_different_sizes_error(self):
        """ Test __add__ throws error when the two networks have a different number of stations """
        with pytest.raises(ValueError) as e_info:
            _ = Network(1, []) + Network(2, [])
        assert str(e_info.value) == "Networks cannot be combined with n_nodes 1 and 2"


class TestDisruptions:
    """ Tests for disruption functions """
    @ pytest.mark.parametrize(
        "disruptions_info, matrix_expected, edges_expected",
        [
            (
                # Line 0 at station 1 by 2 -> both edges increased
                (2, 1, None, 0),
                np.array(
                    [
                        [0, 20, 40, 0],
                        [20, 0, 40, 30],
                        [40, 40, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(20, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(40, 0), (50, 2)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # Line 0 at station 2 by 3 -> line 2 is now quicker
                (3, 2, None, 0),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 50, 30],
                        [40, 50, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(50, 2), (60, 0)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # Line 0 at station 1 by 1 -> nothing happens
                (1, 1, None, 0),
                None,
                None
            ),
            (
                # Line 2 at station 0 -> nothing happens
                (3, 0, None, 2),
                None,
                None
            ),
        ],
    )
    def delay_to_specific_line_one_station(
        self, sample_network, sample_edges_expected, sample_matrix_expected,
        disruptions_info, matrix_expected, edges_expected
    ):
        """ Test specific line to one station """
        edges_expected = edges_expected or sample_edges_expected
        matrix_expected = sample_matrix_expected if matrix_expected is None else matrix_expected

        sample_network.apply_delay(*disruptions_info)

        assert np.array_equal(sample_network.matrix, matrix_expected)
        for key, value in sample_network.edges.items():
            assert value == edges_expected.get(key, []), f"key {key}"

    @ pytest.mark.parametrize(
        "disruptions_info, matrix_expected, edges_expected",
        [
            (
                # Line 2 between stations 1&3, delay 2 -> time increased
                (2, 1, 3, 2),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 60],
                        [40, 20, 0, 0],
                        [0, 60, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(20, 0), (50, 2)],
                    (1, 3): [(60, 2)]
                }
            ),
            (
                # Line 0 between stations 1&2, delay 3 -> other line now faster
                (3, 2, 1, 0),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 50, 30],
                        [40, 50, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(50, 2), (60, 0)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # Line 1 between stations 1&2 by 1 -> nothing happens
                (1, 2, 1, 1),
                None,
                None
            ),
            (
                # Line 1 between stations 0&3 by 3 -> nothing happens
                (3, 0, 3, 1),
                None,
                None
            ),
        ],
    )
    def test_delay_to_specific_line_between_stations(
        self, sample_network, sample_edges_expected, sample_matrix_expected,
        disruptions_info, matrix_expected, edges_expected
    ):
        """ Test delay to specific line and stations """
        edges_expected = edges_expected or sample_edges_expected
        matrix_expected = sample_matrix_expected if matrix_expected is None else matrix_expected

        sample_network.apply_delay(*disruptions_info)

        assert np.array_equal(sample_network.matrix, matrix_expected)
        for key, value in sample_network.edges.items():
            assert value == edges_expected.get(key, []), f"key {key}"

    @ pytest.mark.parametrize(
        "disruptions_info, matrix_expected, edges_expected",
        [
            (
                # Delay to station 3 by 2
                (2, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 60],
                        [40, 20, 0, 0],
                        [0, 60, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(20, 0), (50, 2)],
                    (1, 3): [(60, 2)]
                }
            ),

            (
                # Delay to station 2 by 3
                (3, 2),
                np.array(
                    [
                        [0, 10, 120, 0],
                        [10, 0, 60, 30],
                        [120, 60, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(120, 1)],
                    (1, 2): [(60, 0), (150, 2)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # Delay to station 1 by 3
                (3, 1),
                np.array(
                    [
                        [0, 30, 40, 0],
                        [30, 0, 60, 90],
                        [40, 60, 0, 0],
                        [0, 90, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(30, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(60, 0), (150, 2)],
                    (1, 3): [(90, 2)]
                }
            ),
        ],
    )
    def test_delay_to_entire_one_station(
        self, sample_network, disruptions_info, matrix_expected, edges_expected
    ):
        """ Test delay to entire one station """
        edges_expected = edges_expected or sample_edges_expected

        sample_network.apply_delay(*disruptions_info)

        assert np.array_equal(sample_network.matrix, matrix_expected)
        for key, value in sample_network.edges.items():
            assert value == edges_expected.get(key, []), f"key {key}"

    @ pytest.mark.parametrize(
        "disruptions_info, matrix_expected, edges_expected",
        [
            (
                # Delay between 1&3 by 2
                (2, 1, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 60],
                        [40, 20, 0, 0],
                        [0, 60, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(20, 0), (50, 2)],
                    (1, 3): [(60, 2)]
                }
            ),
            (
                # Delay between 2&1 by 3
                (3, 2, 1),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 60, 30],
                        [40, 60, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(60, 0), (150, 2)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # Delay between 2&3 by 3 -> nothing happens
                (3, 2, 3),
                None,
                None
            ),
        ],
    )
    def test_delay_to_entire_between_stations(
        self, sample_network, sample_edges_expected, sample_matrix_expected,
        disruptions_info, matrix_expected, edges_expected
    ):
        """ Test delay to entire between stations """
        edges_expected = edges_expected or sample_edges_expected
        matrix_expected = sample_matrix_expected if matrix_expected is None else matrix_expected

        sample_network.apply_delay(*disruptions_info)

        assert np.array_equal(sample_network.matrix, matrix_expected)
        for key, value in sample_network.edges.items():
            assert value == edges_expected.get(key, []), f"key {key}"

    @ pytest.mark.parametrize(
        "disruptions_info, matrix_expected, edges_expected",
        [
            (
                # Close station 1
                (0, 1, None, None),
                np.array(
                    [
                        [0, 0, 40, 0],
                        [0, 0, 0, 0],
                        [40, 0, 0, 0],
                        [0, 0, 0, 0],
                    ]
                ),
                {
                    (0, 2): [(40, 1)],
                }
            ),
            (
                # Close between stations 1&2
                (0, 1, 2, None),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 0, 30],
                        [40, 0, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # Close between stations 0&2
                (0, 0, 2, None),
                np.array(
                    [
                        [0, 10, 0, 0],
                        [10, 0, 20, 30],
                        [0, 20, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (1, 2): [(20, 0), (50, 2)],
                    (1, 3): [(30, 2)]
                }
            ),
            (
                # Close line 0 between stations 1&2 -> line closed, other line now faster
                (0, 2, 1, 0),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 50, 30],
                        [40, 50, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(40, 1)],
                    (1, 2): [(50, 2)],
                    (1, 3): [(30, 2)]
                }
            ),
        ],
    )
    def test_delay_to_closure(self, sample_network, disruptions_info, matrix_expected, edges_expected):
        """ Test functionality of delay_to_closure """
        sample_network.apply_delay(*disruptions_info)

        assert np.array_equal(sample_network.matrix, matrix_expected)
        for key, value in sample_network.edges.items():
            assert value == edges_expected.get(key, []), f"key {key}"


class TestGraph:
    """ Test the functionality of the graph related methods """

    @pytest.fixture()
    def graph_network(self):
        """ Setup network for graph tests """
        matrix = np.array(
            [
                # Main network nodes 0-4
                [0, 1, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 2, 0, 4, 0, 0, 0, 0],
                [0, 2, 0, 8, 0, 0, 0, 0, 0],
                [0, 0, 8, 0, 1, 0, 0, 0, 0],
                [0, 4, 0, 1, 0, 0, 0, 0, 0],
                # Isolated sub-network with nodes 5-7
                [0, 0, 0, 0, 0, 0, 5, 9, 0],
                [0, 0, 0, 0, 0, 5, 0, 2, 0],
                [0, 0, 0, 0, 0, 9, 2, 0, 0],
                # Isolated node 8
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ]
        )
        network = Network(9, [])
        network.matrix = matrix

        yield network

    @pytest.mark.parametrize(
        "n, v, result_expected",
        [
            (1, 0, [1]),
            (1, 1, [0, 2, 4]),
            (2, 0, [1, 2, 4]),
            (3, 0, [1, 2, 3, 4]),
            (4, 0, [1, 2, 3, 4]),
            (1, 5, [6, 7]),
            (2, 5, [6, 7]),
            (3, 8, []),
        ]
    )
    def test_distant_neighbours_positive(self, graph_network, n, v, result_expected):
        """ Test positive cases for distant neighbours """
        results = Network.distant_neighbours(graph_network,n, v)
        assert set(results) == set(result_expected)
        assert len(results) == len(result_expected)

    def test_distant_neighbours_errors(self, graph_network):
        """ Check that distant neighbours raises the appropriate errors """
        with pytest.raises(ValueError) as e_info:
            Network.distant_neighbours(graph_network,-1, 0)
        assert str(e_info.value) == "n must be > 0"

        with pytest.raises(IndexError) as e_info:
            Network.distant_neighbours(graph_network,1, 10)
        assert str(e_info.value) == "v must satisfy 0 <= v < n_nodes (9)"

        with pytest.raises(IndexError) as e_info:
            Network.distant_neighbours(graph_network,1, -1)
        assert str(e_info.value) == "v must satisfy 0 <= v < n_nodes (9)"

    @pytest.mark.parametrize(
        "parameters, path_expected",
        [
            # Simple path of one node
            (([None, 0], 0, 1), [0, 1]),
            # Two node path
            (([None, 2, 0], 0, 1), [0, 2, 1]),
            # Three node path
            (([None, 2, 3, 0], 0, 1), [0, 3, 2, 1]),
            # Path with unrelated node
            (([None, 2, 0, 3, 2], 0, 1), [0, 2, 1]),
        ]
    )
    def test_construct_path_positive(self, graph_network, parameters, path_expected):
        """ Test positivee cases for construct_path """
        path = Network.construct_path(graph_network,*parameters)
        assert path == path_expected

    @pytest.mark.parametrize(
        "parameters, cost_expected, predecessor_expected",
        [
            ((0, 1), 1, [None, 0, None, None, None, None, None, None, None]),
            ((0, 3), 6, [None, 0, 1, 4, 1, None, None, None, None]),
            ((2, 3), 7, [1, 2, None, 4, 1, None, None, None, None]),
            ((5, 7), 7, [None, None, None, None, None, None, 5, 6, None]),
            ((7, 5), 7, [None, None, None, None, None, 6, 7, None, None]),
        ]
    )
    def test_dijkstra_positive(self, graph_network, parameters, cost_expected, predecessor_expected):
        """ Test dijkstra correctly returns cost and assembles predecessor array """
        Network.construct_path = MagicMock()
        _, cost = Network.dijkstra(graph_network,*parameters)

        assert cost == cost_expected
        Network.construct_path.assert_called_once_with(graph_network,predecessor_expected, *parameters)

    @pytest.mark.parametrize(
        "parameters",
        [
            ((0, 5)),
            ((5, 0)),
            ((1, 8)),
            ((8, 7)),
            ((7, 2)),
        ]
    )
    def test_dijkstra_no_path(self, graph_network, parameters):
        """ Test dijkstra returns none, none when no path """
        Network.construct_path = MagicMock()
        path, cost = Network.dijkstra(graph_network,*parameters)

        assert path is None
        assert cost is None

    @pytest.mark.parametrize(
        "parameters",
        [
            ((0, 9)),
            ((9, 0)),
            ((-1, 0)),
            ((0, -1)),
        ]
    )
    def test_dijkstra_index_error(self, graph_network, parameters):
        """ Assert correct cases for distant neighbours """
        with pytest.raises(IndexError) as e_info:
            Network.dijkstra(graph_network,*parameters)
        assert str(e_info.value) == "start_node and end_node must satisfy 0 <= v < n_nodes (9)"
