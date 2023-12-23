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
