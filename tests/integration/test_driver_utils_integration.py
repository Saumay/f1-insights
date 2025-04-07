"""Integration tests for driver utilities."""

import pytest
import fastf1
import os
from f1_insights.utils.driver_utils import get_driver_info

@pytest.fixture(scope="module")
def real_session():
    """Create a real FastF1 session for testing."""
    # Get absolute path to cache directory
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache'))
    print(f"\nCache directory path: {cache_dir}")
    print(f"Cache directory exists: {os.path.exists(cache_dir)}")
    os.makedirs(cache_dir, exist_ok=True)
    print(f"Cache directory exists after makedirs: {os.path.exists(cache_dir)}")
    fastf1.Cache.enable_cache(cache_dir)
    session = fastf1.get_session(2024, 'Chinese GP', 'SQ')
    session.load()
    return session

@pytest.mark.integration
def test_get_driver_info_ferrari(real_session):
    """Test getting information for Ferrari drivers."""
    info = get_driver_info(real_session, 'LEC')
    assert info['name'] == 'Charles Leclerc'
    assert info['number'] == '16'
    assert info['team'] == 'Ferrari'

@pytest.mark.integration
def test_get_driver_info_redbull(real_session):
    """Test getting information for Red Bull drivers."""
    info = get_driver_info(real_session, 'VER')
    assert info['name'] == 'Max Verstappen'
    assert info['number'] == '1'
    assert info['team'] == 'Red Bull Racing'

@pytest.mark.integration
def test_get_driver_info_mclaren(real_session):
    """Test getting information for McLaren drivers."""
    info = get_driver_info(real_session, 'NOR')
    assert info['name'] == 'Lando Norris'
    assert info['number'] == '4'
    assert info['team'] == 'McLaren'

@pytest.mark.integration
def test_get_driver_info_nonexistent(real_session):
    """Test getting information for a non-existent driver."""
    info = get_driver_info(real_session, 'XXX')
    assert info['name'] == 'XXX'
    assert info['number'] == 'N/A'
    assert info['team'] == 'Unknown' 