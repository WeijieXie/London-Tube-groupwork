''' Tests for the network class '''
import pytest
import numpy as np
from londontube.network import Network


@pytest.fixture()
def sample_edges():
    ''' Setup sample edges '''
    yield [
        (1, 0, 10, 0),
        (1, 2, 20, 0),
        (1, 3, 30, 1),
        (0, 2, 40, 1),
        (1, 2, 50, 2),
    ]


@pytest.fixture()
def sample_network(sample_edges):
    ''' Setup sample network '''
    # Setting up a small network to use in the tests
    yield Network(4, sample_edges)


class TestInit:
    """Test basic functionality of the Network class"""

    def test_init_positive(self, sample_edges):
        ''' Test positive init - we don't use the sample_network fixture directly since that depends on __add__'''
        network = Network(4, sample_edges)
        assert network.n_nodes == 4  # Check if nodes are correctly set
        # Check if edges are correctly set
        assert set(network.edges) == set(sample_edges)
        assert len(network.edges) == len(sample_edges)
        assert np.array_equal(
            network.matrix,
            np.array(
                [
                    [0, 10, 40, 0],
                    [10, 0, 20, 30],
                    [40, 20, 0, 0],
                    [0, 30, 0, 0],
                ]
            ),
        )

    @ pytest.mark.parametrize("n_stations", [.1, True, ''])
    def test_init_n_stations_type_error(self, n_stations):
        ''' Test init throws error when n_stations is not of type int '''
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
        ''' Test init throws error when any edge parameter is not an int '''
        with pytest.raises(TypeError) as e_info:
            Network(1, edges)
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
        ''' Test init throws error when any edge does not have 4 parameters '''
        with pytest.raises(TypeError) as e_info:
            Network(1, edges)
        assert str(e_info.value) == "Edges must have 4 parameters"

    @ pytest.mark.parametrize(
        "edges_all, matrix_expected, edges_record_expected",
        [
            # All added
            (
                [
                    [(1, 0, 10, 0), (1, 2, 20, 0)],
                    [(0, 2, 30, 1)],
                    [(2, 3, 50, 2)]
                ],
                np.array([
                    [0, 10, 30, 0],
                    [10, 0, 20, 0],
                    [30, 20, 0, 50],
                    [0, 0, 50, 0]
                ]),
                {
                    (0, 1): [(10, 0)],
                    (0, 2): [(30, 1)],
                    (1, 2): [(20, 0)],
                    (2, 3): [(50, 2)],
                }
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
                    (0, 1): [(10, 0), (20, 0)],
                    (1, 2): [(20, 0), (50, 0)],
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
                    (1, 2): [(20, 1), (50, 0)],
                }
            ),
        ]
    )
    def test_add_positive_case(self, edges_all, matrix_expected, edges_record_expected):
        ''' Test __add__ function positive case '''
        edges = [edge for edges in edges_all for edge in edges]
        n_stations = max(edge[1] for edge in edges) + 1
        network = sum([Network(n_stations, edges) for edges in edges_all], Network(n_stations, []))

        for key, value in network.edges_record.items():
            assert value == edges_record_expected.get(tuple(set(key)), []), f"key {key}"
        assert np.array_equal(network.matrix, matrix_expected)

    def test_add_different_sizes_error(self):
        ''' Test __add__ throws error when the two networks have a different number of stations '''
        with pytest.raises(ValueError) as e_info:
            _ = Network(1, []) + Network(2, [])
        assert str(e_info.value) == "Networks cannot be combined with n_stations 1 and 2"


class TestDisruptions:
    ''' Tests for disruption functions '''
    @ pytest.mark.parametrize(
        "disruptions_info, network_expected, edges_expected",
        [
            (
                # Line 0 at station 1 -> both edges increased
                (0, 1, 2),
                np.array(
                    [
                        [0, 20, 40, 0],
                        [20, 0, 40, 30],
                        [40, 40, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 20, 0),
                    (1, 2, 40, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                # Line 0 at station 2 by 3 -> line 2 is now quicker
                (0, 2, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 50, 30],
                        [40, 50, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 60, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                # Line 0 at station 1 by 1 -> nothing happens
                (0, 1, 1),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 30],
                        [40, 20, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 20, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                # Line 2 at station 0 -> nothing happens
                (2, 0, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 30],
                        [40, 20, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 20, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
        ],
    )
    def delay_to_specific_line_one_station(
        self, sample_network, disruptions_info, network_expected, edges_expected
    ):
        ''' Test specific line to one station '''
        sample_network.delay_to_specific_line_one_station(*disruptions_info)
        assert np.array_equal(sample_network.matrix, network_expected)
        assert set(sample_network.edges) == set(edges_expected)
        assert len(sample_network.edges) == len(edges_expected)

    @ pytest.mark.parametrize(
        "disruptions_info, network_expected, edges_expected",
        [
            (
                # Line 1 between stations 1&3 -> time increased
                (1, 1, 3, 2),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 60],
                        [40, 20, 0, 0],
                        [0, 60, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 20, 0),
                    (1, 3, 60, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                # Line 0 between stations 1&2 -> time increased, other line now faster
                (0, 2, 1, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 50, 30],
                        [40, 50, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 60, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                # Line 1 between stations 1&2 -> nothing happens
                (1, 2, 1, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 30],
                        [40, 20, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 20, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                # Line 1 between stations 0&3 -> nothing happens
                (1, 0, 3, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 30],
                        [40, 20, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 20, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
        ],
    )
    def test_delay_to_specific_line_between_stations(
        self, sample_network, disruptions_info, network_expected, edges_expected
    ):
        """ Test delay to specific line and stations """
        sample_network.delay_to_specific_line_between_stations(*disruptions_info)
        assert np.array_equal(sample_network.matrix, network_expected)
        assert set(sample_network.edges) == set(edges_expected)
        assert len(sample_network.edges) == len(edges_expected)

    @ pytest.mark.parametrize(
        "disruptions_info, network_expected, edges_expected",
        [
            (
                (3, 2),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 60],
                        [40, 20, 0, 0],
                        [0, 60, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 20, 0),
                    (1, 3, 60, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                (2, 3),
                np.array(
                    [
                        [0, 10, 80, 0],
                        [10, 0, 60, 30],
                        [80, 60, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 60, 0),
                    (1, 3, 30, 1),
                    (0, 2, 80, 1),
                    (1, 2, 150, 2),
                ]
            ),
            (
                (1, 3),
                np.array(
                    [
                        [0, 30, 40, 0],
                        [30, 0, 60, 90],
                        [40, 60, 0, 0],
                        [0, 90, 0, 0],
                    ]
                ),
                [
                    (1, 0, 30, 0),
                    (1, 2, 60, 0),
                    (1, 3, 90, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
        ],
    )
    def test_delay_to_entire_one_station(
        self, sample_network, disruptions_info, network_expected, edges_expected
    ):
        """ Test delay to entire one station """
        sample_network.delay_to_entire_one_station(*disruptions_info)
        assert np.array_equal(sample_network.matrix, network_expected)
        assert set(sample_network.edges) == set(edges_expected)
        assert len(sample_network.edges) == len(edges_expected)

    @ pytest.mark.parametrize(
        "disruptions_info, network_expected, edges_expected",
        [
            (
                (1, 3, 2),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 20, 60],
                        [40, 20, 0, 0],
                        [0, 60, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 20, 0),
                    (1, 3, 60, 1),
                    (0, 2, 40, 1),
                    (1, 2, 50, 2),
                ]
            ),
            (
                (2, 1, 3),
                np.array(
                    [
                        [0, 10, 40, 0],
                        [10, 0, 60, 30],
                        [40, 60, 0, 0],
                        [0, 30, 0, 0],
                    ]
                ),
                [
                    (1, 0, 10, 0),
                    (1, 2, 60, 0),
                    (1, 3, 30, 1),
                    (0, 2, 40, 1),
                    (1, 2, 150, 2),
                ]
            ),
        ],
    )
    def test_delay_to_entire_between_stations(
        self, sample_network, disruptions_info, network_expected, edges_expected
    ):
        """ Test delay to entire between stations """
        sample_network.delay_to_entire_between_stations(*disruptions_info)
        assert np.array_equal(sample_network.matrix, network_expected)
        assert set(sample_network.edges) == set(edges_expected)
        assert len(sample_network.edges) == len(edges_expected)

    @ pytest.mark.parametrize(
        "disruptions_info, network_expected, edges_expected",
        [
            (
                [1],
                np.array(
                    [
                        [0, 0, 40, 0],
                        [0, 0, 0, 0],
                        [40, 0, 0, 0],
                        [0, 0, 0, 0],
                    ]
                ),
                [
                    (1, 0, 0, 0),
                    (1, 2, 0, 0),
                    (1, 3, 0, 1),
                    (0, 2, 40, 1),
                    (1, 2, 0, 2),
                ]
            ),
            (
                [0, 3, 4],
                np.array(
                    [
                        [0, 0, 0, 0],
                        [0, 0, 20, 0],
                        [0, 20, 0, 0],
                        [0, 0, 0, 0],
                    ]
                ),
                [
                    (1, 0, 0, 0),
                    (1, 2, 20, 0),
                    (1, 3, 0, 1),
                    (0, 2, 0, 1),
                    (1, 2, 0, 2),
                ]
            ),
        ],
    )
    def test_delay_to_closure(self, sample_network, disruptions_info, network_expected, edges_expected):
        """ Test functionality of delay_to_closure """
        sample_network.delay_to_closure(disruptions_info)
        assert np.array_equal(sample_network.matrix, network_expected)
        assert set(sample_network.edges) == set(edges_expected)
        assert len(sample_network.edges) == len(edges_expected)
