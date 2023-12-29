import pytest
from unittest import mock

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
