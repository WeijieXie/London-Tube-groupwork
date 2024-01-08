import pytest
from unittest.mock import MagicMock
import numpy as np
from londontube.network import Network


@pytest.fixture
def sample_network():
    # Setting up a small network to use in the tests
    n_stations = 5
    list_of_edges_1 = [
        (1, 0, 10, 0),
        (1, 2, 20, 0),
    ]
    list_of_edges_2 = [
        (1, 3, 30, 1),
        (1, 4, 40, 1),
    ]
    list_of_edges_3 = [
        (1, 2, 50, 2),  # Different line
    ]
    return (
        Network(n_stations, list_of_edges_1)
        + Network(n_stations, list_of_edges_2)
        + Network(n_stations, list_of_edges_3)
    )


# Test Initialization
def test_initialization(sample_network):
    assert sample_network.n_nodes == 5  # Check if nodes are correctly set
    # assert len(sample_network.edges) == 5  # Check if edges are correctly set
    assert np.array_equal(
        sample_network.matrix,
        np.array(
            [
                [0, 10, 0, 0, 0],
                [10, 0, 20, 30, 40],
                [0, 20, 0, 0, 0],
                [0, 30, 0, 0, 0],
                [0, 40, 0, 0, 0],
            ]
        ),
    )


# Test Properties
def test_properties(sample_network):
    assert np.array_equal(
        sample_network.adjacency_matrix,
        np.array(
            [
                [0, 10, 0, 0, 0],
                [10, 0, 20, 30, 40],
                [0, 20, 0, 0, 0],
                [0, 30, 0, 0, 0],
                [0, 40, 0, 0, 0],
            ]
        ),
    )
    assert sample_network.n_nodes == 5


@pytest.mark.parametrize(
    "disruptions_info,network_expected",
    [
        (
            (0, 1, 2),
            np.array(
                [
                    [0, 20, 0, 0, 0],
                    [20, 0, 40, 30, 40],
                    [0, 40, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            (0, 2, 3),
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 50, 30, 40],
                    [0, 50, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
    ],
)
def delay_to_specific_line_one_station(
    sample_network, disruptions_info, network_expected
):
    sample_network.delay_to_specific_line_one_station(*disruptions_info)
    assert isinstance(
        sample_network, Network
    ), "The returned object should be an instance of Network."
    assert np.array_equal(sample_network.matrix, network_expected)
    assert sample_network.n_nodes == 5, "The network should have more than 0 nodes."


@pytest.mark.parametrize(
    "disruptions_info,network_expected",
    [
        (
            (1, 1, 3, 2),
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 20, 60, 40],
                    [0, 20, 0, 0, 0],
                    [0, 60, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            (0, 2, 1, 3),
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 50, 30, 40],
                    [0, 50, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
    ],
)
def test_delay_to_specific_line_between_stations(
    sample_network, disruptions_info, network_expected
):
    sample_network.delay_to_specific_line_between_stations(*disruptions_info)
    assert isinstance(
        sample_network, Network
    ), "The returned object should be an instance of Network."
    assert np.array_equal(sample_network.matrix, network_expected)
    assert sample_network.n_nodes == 5, "The network should have more than 0 nodes."


@pytest.mark.parametrize(
    "disruptions_info,network_expected",
    [
        (
            (3, 2),
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 20, 60, 40],
                    [0, 20, 0, 0, 0],
                    [0, 60, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            (2, 3),
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 60, 30, 40],
                    [0, 60, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            (1, 3),
            np.array(
                [
                    [0, 30, 0, 0, 0],
                    [30, 0, 60, 90, 120],
                    [0, 60, 0, 0, 0],
                    [0, 90, 0, 0, 0],
                    [0, 120, 0, 0, 0],
                ]
            ),
        ),
    ],
)
def test_delay_to_entire_one_station(
    sample_network, disruptions_info, network_expected
):
    sample_network.delay_to_entire_one_station(*disruptions_info)
    assert isinstance(
        sample_network, Network
    ), "The returned object should be an instance of Network."
    assert np.array_equal(sample_network.matrix, network_expected)
    assert sample_network.n_nodes == 5, "The network should have more than 0 nodes."


@pytest.mark.parametrize(
    "disruptions_info,network_expected",
    [
        (
            (1, 3, 2),
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 20, 60, 40],
                    [0, 20, 0, 0, 0],
                    [0, 60, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            (2, 1, 3),
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 60, 30, 40],
                    [0, 60, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
    ],
)
def test_delay_to_entire_between_stations(
    sample_network, disruptions_info, network_expected
):
    sample_network.delay_to_entire_between_stations(*disruptions_info)
    assert isinstance(
        sample_network, Network
    ), "The returned object should be an instance of Network."
    assert np.array_equal(sample_network.matrix, network_expected)
    assert sample_network.n_nodes == 5, "The network should have more than 0 nodes."


@pytest.mark.parametrize(
    "disruptions_info,network_expected",
    [
        (
            [1],
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
        ),
        (
            [2],
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 0, 30, 40],
                    [0, 0, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            [0, 3, 4],
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 20, 0, 0],
                    [0, 20, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
        ),
    ],
)
def test_delay_to_closure(sample_network, disruptions_info, network_expected):
    sample_network.delay_to_closure(disruptions_info)
    assert isinstance(
        sample_network, Network
    ), "The returned object should be an instance of Network."
    assert np.array_equal(sample_network.matrix, network_expected)
    assert sample_network.n_nodes == 5, "The network should have more than 0 nodes."


class TestGraph:
    """ Test the functionality of the graph related methods """

    @pytest.fixture()
    def graph_network(self):
        matrix = np.array(
            [
                # Main network nodes 0-4
                [0, 1, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 2, 0, 4, 0, 0, 0, 0],
                [0, 2, 0, 8, 0, 0, 0, 0, 0],
                [0, 3, 8, 0, 1, 0, 0, 0, 0],
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
        results = graph_network.distant_neighbours(n, v)
        assert set(results) == set(result_expected)
        assert len(results) == len(result_expected)

    def test_distant_neighbours_errors(self, graph_network):
        """ Check that distant neighbours raises the appropriate errors """
        with pytest.raises(ValueError) as e_info:
            graph_network.distant_neighbours(-1, 0)
        assert str(e_info.value) == "n must be > 0"

        with pytest.raises(IndexError) as e_info:
            graph_network.distant_neighbours(1, 10)
        assert str(e_info.value) == "v must satisfy 0 <= v < n_nodes (9)"

        with pytest.raises(IndexError) as e_info:
            graph_network.distant_neighbours(1, -1)
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
        path = graph_network.construct_path(*parameters)
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
        graph_network.construct_path = MagicMock()
        _, cost = graph_network.dijkstra(*parameters)

        assert cost == cost_expected
        graph_network.construct_path.assert_called_once_with(predecessor_expected, *parameters)

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
        graph_network.construct_path = MagicMock()
        path, cost = graph_network.dijkstra(*parameters)

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
            graph_network.dijkstra(*parameters)
        assert str(e_info.value) == "start_node and end_node must satisfy 0 <= v < n_nodes (9)"
