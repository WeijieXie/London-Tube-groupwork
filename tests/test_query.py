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

# Test the connectivity_of_line function with a known line index.
@pytest.mark.parametrize("line_index", [0, 5, 11])
def test_connectivity_of_line(line_index):
    network = connectivity_of_line(line_index)
    assert isinstance(network, Network), "The returned object should be an instance of Network."
    assert network.n_nodes > 0, "The network should have more than 0 nodes."
