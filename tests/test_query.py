# tests/test_query.py
from unittest import mock
import pytest

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
    query_station_all_info,
    convert_indices_to_names,
    convert_names_to_indices,
)


# Test the check_http_connection function.
def test_check_http_connection():
    mock_responses = [
        mock.Mock(status_code=200),
        mock.Mock(status_code=404),
        mock.Mock(status_code=500),
    ]
    with mock.patch("requests.get", side_effect=mock_responses) as mock_get:
        assert check_http_connection() is True
        assert check_http_connection() is False
        assert check_http_connection() is False
        mock_get.assert_called()

    with mock.patch("requests.get", side_effect=requests.RequestException()) as mock_get:
        assert check_http_connection() is False
        mock_get.assert_called()


# Test the connectivity_of_line function.
def read_csv_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


network_A = Network(5, [[0, 1, 10, 0], [1, 2, 20, 0]])
network_B = Network(5, [[3, 1, 30, 1], [1, 4, 40, 1]])
network_C = Network(5, [[2, 1, 20, 2]])


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
            assert np.array_equal(network.matrix, network_expected.matrix)
            assert network.n_nodes == 5, "The network should have more than 0 nodes."


def test_connectivity_of_line_raises_exception():
    with mock.patch("londontube.query.query.check_http_connection", return_value=False):
        with pytest.raises(requests.RequestException) as e_info:
            connectivity_of_line(0)
        assert str(e_info.value) == "poor connection, please check the network"


# Test the disruption_info function in poor network.
def test_disruption_info_poor_network():
    with mock.patch("londontube.query.query.check_http_connection", return_value=False):
        with pytest.raises(requests.RequestException):
            disruption_info()


@pytest.fixture()
def simple_disruption():
    yield ([
        {
            "delay": "1",
            "line": "1",
            "stations": ["1", "2"]
        }]
    )


# Test the disruption_info function for today's disruptions.
def test_disruption_info_none(simple_disruption):
    with mock.patch("londontube.query.query.check_http_connection", return_value=True):
        with mock.patch(
            "requests.get",
            side_effect=[
                mock.Mock(
                    json=mock.Mock(
                        return_value=simple_disruption
                    )
                ),
            ],
        ) as mk:
            print(mk.call_count)
            disruptions = disruption_info()
            assert isinstance(disruptions, list), "Disruption info should be a list."
            assert disruptions == simple_disruption


def test_disruption_info_with_date(simple_disruption):
    with mock.patch("londontube.query.query.check_http_connection", return_value=True):
        with mock.patch(
            "requests.get",
            side_effect=[
                mock.Mock(
                    json=mock.Mock(
                        return_value=simple_disruption
                    )
                ),
            ],
        ):
            disruptions = disruption_info("2023-01-01")
            assert isinstance(disruptions, list), "Disruption info should be a list."
            assert disruptions == simple_disruption


# Test the apply_disruptions function.
entire_network_without_disruption = (
    Network(5, [(0, 1, 10, 0), (1, 2, 20, 0)])
    + Network(5, [(3, 1, 30, 1), (1, 4, 40, 1)])
    + Network(5, [(2, 1, 50, 2)])
)


@pytest.mark.parametrize(
    "disruptions_info,network_expected",
    [
        (
            [
                {"delay": 0, "line": 0, "stations": [0, 1]},
                {"delay": 10, "line": 0, "stations": [1, 2]},
            ],
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
            [{"delay": 0, "line": 0, "stations": [1]}, {"delay": 2, "stations": [2]}],
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 100, 30, 40],
                    [0, 100, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
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
    assert np.array_equal(network.matrix, network_expected)
    assert network.n_nodes == 5, "The network should have more than 0 nodes."


# test get the entire network function
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
    with mock.patch("londontube.query.query.check_http_connection", return_value=True):
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
                assert np.array_equal(network.matrix, entire_network)
                assert (
                    network.n_nodes == 5
                ), "The network should have more than 0 nodes."


def test_get_entire_network_raises_exception():
    with mock.patch("londontube.query.query.check_http_connection", return_value=False):
        with pytest.raises(requests.RequestException) as e_info:
            get_entire_network()
        assert str(e_info.value) == "poor connection, please check the network"


# test get the network of given day function
@pytest.mark.parametrize(
    "network_original,disruptions_info,network_expected",
    [
        (
            (
                Network(5, [(0, 1, 10, 0), (1, 2, 20, 0)])
                + Network(5, [(3, 1, 30, 1), (1, 4, 40, 1)])
                + Network(5, [(2, 1, 50, 2)])
            ),
            [
                {"delay": 0, "line": 0, "stations": [0, 1]},
                {"delay": 10, "line": 0, "stations": [1, 2]},
            ],
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
            Network(5, [(0, 1, 10, 0), (1, 2, 20, 0)])
            + Network(5, [(3, 1, 30, 1), (1, 4, 40, 1)]),
            [
                {"delay": 0, "line": 0, "stations": [0, 1]},
                {"delay": 10, "line": 0, "stations": [1, 2]},
            ],
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 200, 30, 40],
                    [0, 200, 0, 0, 0],
                    [0, 30, 0, 0, 0],
                    [0, 40, 0, 0, 0],
                ]
            ),
        ),
        (
            Network(3, [(0, 1, 10, 0), (1, 2, 20, 0)]) + Network(3, [(2, 1, 50, 1)]),
            [
                {"delay": 3, "line": 0, "stations": [0, 1]},
                {"delay": 2, "line": 0, "stations": [1, 2]},
            ],
            np.array(
                [
                    [0, 30, 0],
                    [30, 0, 40],
                    [0, 40, 0],
                ]
            ),
        ),
    ],
)
def test_network_of_given_day(network_original, disruptions_info, network_expected):
    with mock.patch(
        "londontube.query.query.disruption_info", return_value=disruptions_info
    ):
        with mock.patch(
            "londontube.query.query.get_entire_network", return_value=network_original
        ):
            result = network_of_given_day("2021-12-25")

            assert isinstance(
                result, Network
            ), "The result should be an instance of Network."

            assert np.array_equal(result.matrix, network_expected)


# test query_station_all_info()
dict_indices_names_expect = {
    0: "a",
    1: "b",
    2: "c",
    3: "d",
    4: "e",
}
dict_names_indices_expect = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
}
dict_position_expect = {
    0: {"latitude": -1, "longitude": 0},
    1: {"latitude": 0, "longitude": 0},
    2: {"latitude": 1, "longitude": 0},
    3: {"latitude": 0, "longitude": 1},
    4: {"latitude": 0, "longitude": -1},
}

csv_text = read_csv_content("tests/station_all_info.csv")


def test_query_station_all_info():
    with mock.patch("londontube.query.query.check_http_connection", return_value=True):
        with mock.patch("requests.get", return_value=mock.Mock(text=csv_text)):
            (
                dict_indices_names,
                dict_names_indices,
                dict_position,
            ) = query_station_all_info()
            assert dict_indices_names == dict_indices_names_expect
            assert dict_names_indices == dict_names_indices_expect
            assert dict_position == dict_position_expect


# test convert_indices_to_names() func
@pytest.mark.parametrize(
    "station_indices,names_expected",
    [([0], ["a"]), ([0, 1, 2], ["a", "b", "c"]), ([1, 4], ["b", "e"])],
)
def test_convert_indices_to_names(station_indices, names_expected):
    with mock.patch(
        "londontube.query.query.query_station_all_info",
        return_value=(
            dict_indices_names_expect,
            dict_names_indices_expect,
            dict_position_expect,
        ),
    ):
        result = convert_indices_to_names(station_indices)
        assert result == names_expected


# test convert_names_to_indices() func
@pytest.mark.parametrize(
    "station_names,indices_expected",
    [(["a"], [0]), (["a", "b", "c"], [0, 1, 2]), (["b", "e"], [1, 4])],
)
def test_convert_names_to_indices(station_names, indices_expected):
    with mock.patch(
        "londontube.query.query.query_station_all_info",
        return_value=(
            dict_indices_names_expect,
            dict_names_indices_expect,
            dict_position_expect,
        ),
    ):
        result = convert_names_to_indices(station_names)
        assert result == indices_expected
