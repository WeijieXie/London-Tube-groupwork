# tests/test_query.py
import pytest
from unittest import mock

import requests
from londontube.network import Network
from londontube.query.query import check_http_connection, connectivity_of_line, disruption_info, apply_disruptions, get_entire_network, network_of_given_day


def test_check_http_connection():
    mock_responses = [mock.Mock(status_code=200),mock.Mock(status_code=404),mock.Mock(status_code=500)]
    with mock.patch('requests.get',side_effect = mock_responses) as mock_get:
        assert check_http_connection() == True
        assert check_http_connection() == False
        assert check_http_connection() == False
        mock_get.assert_called()

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

# # Test the connectivity_of_line function with a known line index.
# @pytest.mark.parametrize("line_index", [0, 1, 2]) # You can add more line indices as needed.
# def test_connectivity_of_line(line_index):
#     network = connectivity_of_line(line_index)
#     assert isinstance(network, Network), "The returned object should be an instance of Network."
#     assert network.n_nodes > 0, "The network should have more than 0 nodes."

# # Test the disruption_info function for today's disruptions.
# def test_disruption_info():
#     disruptions = disruption_info()
#     assert isinstance(disruptions, list), "Disruption info should be a list."
#     if disruptions: # If there are disruptions today
#         assert all("line" in d or "stations" in d for d in disruptions), "Each disruption should have 'line' or 'stations' key."

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