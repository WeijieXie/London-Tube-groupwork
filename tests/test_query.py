# tests/test_query.py
import pytest
from unittest import mock

import csv
import requests
import numpy as np

from londontube.network import Network
from londontube.query.query import (
    check_http_connection,
    connectivity_of_line,
    disruption_info,
    apply_disruptions,
    get_entire_network,
    network_of_given_day,
)


# Test the check_http_connection function.
def test_check_http_connection():
    mock_responses = [
        mock.Mock(status_code=200),
        mock.Mock(status_code=404),
        mock.Mock(status_code=500),
    ]
    with mock.patch("requests.get", side_effect=mock_responses) as mock_get:
        assert check_http_connection() == True
        assert check_http_connection() == False
        assert check_http_connection() == False
        mock_get.assert_called()


# Test the connectivity_of_line function.
def read_csv_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


network_A = Network(5, [[0, 1, 10, 0], [1, 2, 20, 0]])
network_B = Network(5, [[3, 1, 30, 1], [1, 4, 40, 1]])
network_C = Network(5, [[2, 1, 10, 2]])


@pytest.mark.parametrize(
    "csv_content,network_expected",
    [
        (read_csv_content("tests/line_A.csv"), network_A),
        (read_csv_content("tests/line_B.csv"), network_B),
        (read_csv_content("tests/line_C.csv"), network_C),
    ],
)
def test_connectivity_of_line(csv_content, network_expected):
    with mock.patch("londontube.query.query.check_http_connection", return_value=True):
        with mock.patch(
            "requests.get",
            side_effect=[
                mock.Mock(
                    json=mock.Mock(
                        return_value={
                            "lines": {
                                "0": "A",
                                "1": "B",
                                "2": "C",
                            },
                            "n_lines": 3,
                            "n_stations": 5,
                        }
                    )
                ),
                mock.Mock(content=csv_content.encode("utf-8")),
            ],
        ):
            network = connectivity_of_line(0)
            assert isinstance(
                network, Network
            ), "The returned object should be an instance of Network."
            assert network.matrix.shape == (5, 5)
            assert network.matrix.all() == network_expected.matrix.all()
            assert network.n_nodes == 5, "The network should have more than 0 nodes."


# Test the disruption_info function in poor network.
def test_disruption_info_poor_network():
    with mock.patch(
        "londontube.query.query.check_http_connection", return_value=False
    ) as mock_get:
        with pytest.raises(requests.RequestException):
            disruption_info()


# Test the disruption_info function for today's disruptions.
def test_disruption_info_none():
    disruptions = disruption_info()
    assert isinstance(disruptions, list), "Disruption info should be a list."
    if disruptions:  # If there are disruptions today
        assert all(
            "line" in d or "stations" in d for d in disruptions
        ), "Each disruption should have 'line' or 'stations' key."


@pytest.mark.parametrize(
    ("date", "info_list"),
    [
        (
            "2023-01-01",
            [
                {"delay": 6, "stations": [242, 266]},
                {"delay": 3, "line": 1, "stations": [152, 153]},
                {"delay": 0, "line": 1, "stations": [67, 249]},
                {"delay": 0, "stations": [133]},
                {"delay": 0, "stations": [271]},
                {"delay": 6, "stations": [47, 244]},
                {"delay": 4, "line": 10, "stations": [271]},
                {"delay": 0, "line": 10, "stations": [12, 271]},
                {"delay": 2, "stations": [83, 147]},
                {"delay": 2, "line": 6, "stations": [215, 217]},
                {"delay": 4, "line": 10, "stations": [12, 271]},
                {"delay": 7, "stations": [182, 273]},
                {"delay": 5, "stations": [12, 271]},
                {"delay": 7, "stations": [2, 256]},
                {"delay": 7, "line": 4, "stations": [2, 155]},
                {"delay": 0, "stations": [248]},
                {"delay": 9, "line": 7, "stations": [254, 294]},
                {"delay": 2, "line": 10, "stations": [12, 271]},
                {"delay": 6, "line": 5, "stations": [141]},
                {"delay": 1, "line": 7, "stations": [54, 239]},
                {"delay": 0, "line": 5, "stations": [227, 271]},
                {"delay": 1, "line": 9, "stations": [144]},
                {"delay": 0, "line": 2, "stations": [230]},
                {"delay": 4, "line": 3, "stations": [242, 277]},
                {"delay": 0, "line": 11, "stations": [41]},
                {"delay": 8, "stations": [149, 222]},
                {"delay": 1, "line": 8, "stations": [229, 245]},
                {"delay": 5, "line": 6, "stations": [167, 210]},
                {"delay": 6, "line": 1, "stations": [286]},
                {"delay": 2, "stations": [12]},
                {"delay": 7, "line": 5, "stations": [42, 281]},
                {"delay": 0, "line": 2, "stations": [43, 160]},
                {"delay": 2, "line": 6, "stations": [89, 103]},
            ],
        ),
        (
            "2023-08-23",
            [
                {"delay": 9, "line": 6, "stations": [10, 93]},
                {"delay": 6, "stations": [10, 27]},
                {"delay": 2, "line": 8, "stations": [133]},
                {"delay": 3, "line": 7, "stations": [37, 80]},
                {"delay": 5, "line": 10, "stations": [12, 271]},
                {"delay": 7, "line": 10, "stations": [12, 271]},
                {"delay": 1, "line": 9, "stations": [194, 266]},
                {"delay": 3, "line": 3, "stations": [225, 292]},
                {"delay": 8, "line": 9, "stations": [94, 219]},
                {"delay": 7, "stations": [188]},
                {"delay": 4, "stations": [208]},
                {"delay": 4, "line": 8, "stations": [124, 133]},
                {"delay": 8, "line": 4, "stations": [100, 109]},
                {"delay": 2, "line": 1, "stations": [75, 178]},
                {"delay": 1, "line": 10, "stations": [12, 271]},
                {"delay": 8, "line": 8, "stations": [125, 218]},
                {"delay": 6, "line": 8, "stations": [0]},
                {"delay": 7, "line": 8, "stations": [59]},
                {"delay": 5, "line": 4, "stations": [35, 281]},
                {"delay": 5, "line": 8, "stations": [74]},
                {"delay": 0, "line": 3, "stations": [84, 128]},
                {"delay": 2, "line": 5, "stations": [22, 156]},
                {"delay": 2, "stations": [142]},
                {"delay": 6, "stations": [142, 202]},
                {"delay": 3, "stations": [196, 281]},
                {"delay": 0, "line": 3, "stations": [121, 183]},
                {"delay": 4, "line": 11, "stations": [31]},
                {"delay": 9, "line": 5, "stations": [143, 203]},
                {"delay": 4, "line": 10, "stations": [12, 271]},
                {"delay": 4, "line": 9, "stations": [88, 269]},
                {"delay": 0, "stations": [17, 183]},
                {"delay": 2, "line": 3, "stations": [43, 160]},
                {"delay": 3, "line": 2, "stations": [98, 230]},
                {"delay": 5, "line": 11, "stations": [41]},
                {"delay": 5, "line": 1, "stations": [23, 155]},
                {"delay": 8, "line": 8, "stations": [30, 295]},
                {"delay": 3, "line": 7, "stations": [28, 83]},
                {"delay": 9, "line": 3, "stations": [163]},
                {"delay": 8, "line": 9, "stations": [219, 253]},
                {"delay": 2, "stations": [264]},
                {"delay": 3, "stations": [158]},
                {"delay": 3, "stations": [56, 184]},
                {"delay": 0, "stations": [243, 247]},
                {"delay": 0, "line": 2, "stations": [165]},
                {"delay": 9, "line": 10, "stations": [12, 271]},
                {"delay": 8, "line": 10, "stations": [12, 271]},
                {"delay": 5, "line": 2, "stations": [89, 144]},
            ],
        ),
        (
            "2024-12-31",
            [
                {"delay": 9, "line": 5, "stations": [141, 289]},
                {"delay": 7, "line": 1, "stations": [286]},
                {"delay": 7, "line": 2, "stations": [43, 160]},
                {"delay": 5, "line": 3, "stations": [236]},
                {"delay": 3, "line": 8, "stations": [116]},
                {"delay": 2, "line": 7, "stations": [166]},
                {"delay": 0, "line": 9, "stations": [94, 219]},
                {"delay": 0, "line": 3, "stations": [2, 287]},
                {"delay": 2, "line": 9, "stations": [219, 253]},
                {"delay": 6, "line": 1, "stations": [204]},
                {"delay": 2, "line": 8, "stations": [129, 130]},
                {"delay": 5, "line": 8, "stations": [130, 186]},
                {"delay": 1, "line": 8, "stations": [73, 98]},
                {"delay": 5, "line": 11, "stations": [62, 214]},
                {"delay": 4, "stations": [81, 189]},
                {"delay": 0, "stations": [43, 165]},
                {"delay": 5, "line": 9, "stations": [122, 144]},
                {"delay": 0, "line": 3, "stations": [16, 285]},
                {"delay": 1, "line": 7, "stations": [101, 269]},
                {"delay": 9, "line": 4, "stations": [82, 189]},
                {"delay": 4, "line": 6, "stations": [74, 206]},
                {"delay": 7, "line": 2, "stations": [103]},
                {"delay": 5, "line": 8, "stations": [217]},
                {"delay": 0, "line": 8, "stations": [38, 144]},
                {"delay": 4, "stations": [142, 158]},
                {"delay": 0, "line": 7, "stations": [55]},
            ],
        ),
    ],
)
def test_disruption_info_with_date(date, info_list):
    disruptions = disruption_info(date)
    assert isinstance(disruptions, list), "Disruption info should be a list."
    assert disruptions == info_list


# Test the apply_disruptions function.
entire_network_without_disruption = Network(
    5, [(0, 1, 10, 0), (1, 2, 20, 0), (3, 1, 30, 1), (1, 4, 40, 1), (2, 1, 50, 2)]
)


@pytest.mark.parametrize(
    "disruptions_info,network_expected",
    [
        (
            [{"delay": 0, "line": 0, "stations": [0,1]},{"delay": 10, "line": 0, "stations": [1,2]}],
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 50, 30, 40],
                    [0, 50, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            [{"delay": 0, "line": 0, "stations": [1]},{"delay": 2, "stations": [2]}],
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 60, 80],
                    [0, 0, 0, 0, 0],
                    [0, 60, 0, 0, 0],
                    [0, 80, 0, 0, 0],
                ]
            ),
        ),
        (
            [{"delay": 0, "stations": [1]}],
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
    ],
)
def test_apply_disruptions(disruptions_info, network_expected):
    network = apply_disruptions(entire_network_without_disruption, disruptions_info)
    assert isinstance(
        network, Network
    ), "The returned object should be an instance of Network."
    assert network.matrix.all() == network_expected.all()
    assert network.n_nodes == 5, "The network should have more than 0 nodes."


#
network_A = Network(5, [[0, 1, 10, 0], [1, 2, 20, 0]])
network_B = Network(5, [[3, 1, 30, 1], [1, 4, 40, 1]])
network_C = Network(5, [[2, 1, 10, 2]])


@pytest.mark.parametrize(
    "line_info, line_net_list, entire_network",
    [
        (
            {
                "lines": {
                    "0": "A",
                    "1": "B",
                },
                "n_lines": 2,
                "n_stations": 5,
            },
            [network_A, network_B],
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 20, 30, 40],
                    [0, 20, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            {
                "lines": {
                    "0": "A",
                    "1": "B",
                    "2": "C",
                },
                "n_lines": 3,
                "n_stations": 5,
            },
            [network_A, network_B, network_C],
            np.array(
                [
                    [0, 10, 0, 0, 0],
                    [10, 0, 10, 30, 40],
                    [0, 10, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
    ],
)
def test_get_entire_network(line_info, line_net_list, entire_network):
    with mock.patch(
        "londontube.query.query.check_http_connection", return_value=True
    ) as mock_connection:
        with mock.patch(
            "requests.get",
            side_effect=[
                mock.Mock(json=mock.Mock(return_value=line_info)),
            ],
        ):
            with mock.patch(
                "londontube.query.query.connectivity_of_line",
                side_effect=line_net_list,
            ):
                network = get_entire_network()
                assert isinstance(
                    network, Network
                ), "The returned object should be an instance of Network."
                assert network.matrix.all() == entire_network.all()
                assert (
                    network.n_nodes == 5
                ), "The network should have more than 0 nodes."


# @pytest.mark.parametrize(
#     "name, region, CRS, lat, lon, hub",
#     [
#         ("Edinburgh Park", "Scotland", "abc", 55.927615, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "aBc", 55.927615, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "ABCD", 55.927615, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "EDP", 91, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "EDP", 55.927615, -180.43, False),
#     ],
# )
# def test_convert_indices_to_names():
#     pass

# @pytest.mark.parametrize(
#     "name, region, CRS, lat, lon, hub",
#     [
#         ("Edinburgh Park", "Scotland", "abc", 55.927615, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "aBc", 55.927615, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "ABCD", 55.927615, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "EDP", 91, -3.307829, False),
#         ("Edinburgh Park", "Scotland", "EDP", 55.927615, -180.43, False),
#     ],
# )
# def test_convert_names_to_indices():
#     pass


# # Test the apply_disruptions function by applying a known disruption to the network.
# def test_apply_disruptions():
#     network = Network()
#     network.matrix = [[0,2,3,4]
#                       [2,0,4,8]
#                       [3,4,0,3]
#                       [4,8,3,0]]
#     disruptions = [{"line": 1, "stations": [2, 3], "delay": 2}] # Sample disruption data
#     network_with_disruptions = apply_disruptions(network, disruptions)
#     assert network_with_disruptions == True

# # Test the network_of_given_day function for a specific date.
# @pytest.mark.parametrize("date", ["2023-01-01","2023-08-23","2024-12-31",None])
# def test_network_of_given_day(date):
#     network = network_of_given_day(date)
#     assert isinstance(network, Network), "The returned object should be an instance of Network."
#     assert network.n_nodes > 0, "The network should have more than 0 nodes."
