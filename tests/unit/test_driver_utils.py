"""Unit tests for driver utilities."""

import pytest
from f1_insights.utils.driver_utils import get_driver_info

@pytest.mark.unit
def test_get_driver_info_existing_driver(mock_session):
    """Test getting information for an existing driver."""
    info = get_driver_info(mock_session, 'HAM')
    assert info['name'] == 'Lewis Hamilton'
    assert info['number'] == '44'
    assert info['team'] == 'Ferrari'

@pytest.mark.unit
def test_get_driver_info_nonexistent_driver(mock_session):
    """Test getting information for a non-existent driver."""
    info = get_driver_info(mock_session, 'XXX')
    assert info['name'] == 'XXX'
    assert info['number'] == 'N/A'
    assert info['team'] == 'Unknown'

@pytest.mark.unit
def test_get_driver_info_all_fields_present(mock_session):
    """Test that all expected fields are present in the returned information."""
    info = get_driver_info(mock_session, 'VER')
    expected_fields = {'name', 'number', 'team'}
    assert set(info.keys()) == expected_fields
    assert all(isinstance(value, str) for value in info.values()) 