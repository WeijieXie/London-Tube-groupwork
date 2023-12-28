import pytest
from unittest import mock

import numpy as np

from londontube.network import Network


@pytest.fixture
def sample_network():
    # Setting up a small network to use in the tests
    n_stations = 5
    list_of_edges = [
        (1, 0, 10, 0),  # (station1, station2, weight, line_id)
        (1, 2, 20, 0),
        (1, 3, 30, 1),
        (1, 4, 40, 1),
        (1, 2, 50, 2),  # Different line
    ]
    return Network(n_stations, list_of_edges)


# Test Initialization
def test_initialization(sample_network):
    assert sample_network.n_nodes == 5  # Check if nodes are correctly set
    assert len(sample_network.edges) == 5  # Check if edges are correctly set
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
