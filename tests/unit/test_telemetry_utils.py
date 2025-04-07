"""Unit tests for telemetry utilities."""

import pytest
import pandas as pd
import numpy as np
from f1_insights.utils.telemetry_utils import (
    get_straight_section_telemetry,
    analyze_slipstream,
    get_driver_lap_telemetry
)

@pytest.fixture
def mock_telemetry():
    """Create mock telemetry data."""
    # Use fixed seed for reproducibility
    np.random.seed(42)
    return pd.DataFrame({
        'Distance': np.linspace(0, 1000, 100),
        'Speed': np.random.uniform(200, 350, 100),
        'DistanceToCarAhead': np.random.uniform(30, 100, 100)
    })

@pytest.fixture
def mock_circuit():
    """Create mock circuit data."""
    return pd.DataFrame({
        'Corner': ['Turn 13', 'Turn 14'],
        'Distance': [500, 700]
    })

@pytest.fixture
def mock_session():
    """Create a mock FastF1 session."""
    class MockLap:
        def __init__(self, driver):
            self.driver = driver
        
        def get_telemetry(self):
            return pd.DataFrame({
                'Distance': np.linspace(0, 1000, 100),
                'Speed': np.random.uniform(200, 350, 100),
                'DistanceToCarAhead': np.random.uniform(30, 100, 100)
            })
    
    class MockLaps:
        def __init__(self):
            self.laps = pd.DataFrame({
                'LapNumber': [1, 2],
                'LapTime': [80.0, 79.5]
            })
        
        def pick_driver(self, driver):
            return self
        
        def pick_fastest(self):
            return MockLap('VER')
        
        def pick_lap(self, lap_number):
            return MockLap('HAM')
    
    class MockCircuitInfo:
        def __init__(self):
            self.corners = pd.DataFrame({
                'Number': ['Turn 13', 'Turn 14'],
                'Distance': [500, 700]
            })
    
    class MockSession:
        def __init__(self):
            self.laps = MockLaps()
        
        def get_circuit_info(self):
            return MockCircuitInfo()
    
    return MockSession()

@pytest.mark.unit
def test_get_straight_section_telemetry(mock_session):
    """Test extracting telemetry for a specific section."""
    telemetry = pd.DataFrame({
        'Distance': np.linspace(0, 1000, 100),
        'Speed': np.random.uniform(200, 350, 100),
        'DistanceToCarAhead': np.random.uniform(30, 100, 100)
    })
    
    section = get_straight_section_telemetry(
        telemetry,
        'Turn 13',
        'Turn 14',
        mock_session.get_circuit_info()
    )
    
    assert len(section) > 0
    assert section['Distance'].min() >= 500
    assert section['Distance'].max() <= 700

@pytest.mark.unit
def test_analyze_slipstream_with_slipstream(mock_telemetry):
    """Test slipstream detection when conditions are met."""
    # Create a new DataFrame with controlled values
    test_telemetry = pd.DataFrame({
        'Distance': np.linspace(0, 1000, 100),
        'Speed': np.full(100, 320.0),  # Fixed speed
        'DistanceToCarAhead': np.full(100, 30.0)  # Fixed distance
    })
    
    has_slipstream, min_dist, max_speed = analyze_slipstream(test_telemetry)
    
    assert has_slipstream
    assert min_dist == 30.0
    assert max_speed == 320.0

@pytest.mark.unit
def test_analyze_slipstream_without_slipstream(mock_telemetry):
    """Test slipstream detection when conditions are not met."""
    # Create a new DataFrame with controlled values
    test_telemetry = pd.DataFrame({
        'Distance': np.linspace(0, 1000, 100),
        'Speed': np.full(100, 290.0),  # Fixed speed below threshold
        'DistanceToCarAhead': np.full(100, 60.0)  # Fixed distance above threshold
    })
    
    has_slipstream, min_dist, max_speed = analyze_slipstream(test_telemetry)
    
    assert not has_slipstream
    assert min_dist == 60.0
    assert max_speed == 290.0

@pytest.mark.unit
def test_get_driver_lap_telemetry(mock_session):
    """Test getting telemetry data for a driver's lap."""
    # Test getting fastest lap
    telemetry = get_driver_lap_telemetry(mock_session, 'VER')
    assert isinstance(telemetry, pd.DataFrame)
    assert 'Distance' in telemetry.columns
    assert 'Speed' in telemetry.columns
    
    # Test getting specific lap
    telemetry = get_driver_lap_telemetry(mock_session, 'HAM', lap_number=1)
    assert isinstance(telemetry, pd.DataFrame)
    assert len(telemetry) > 0

@pytest.mark.unit
def test_circuit_info_structure(mock_session):
    """Test to understand CircuitInfo structure."""
    circuit = mock_session.get_circuit_info()
    assert hasattr(circuit, 'corners')
    assert isinstance(circuit.corners, pd.DataFrame)
    assert 'Number' in circuit.corners.columns
    assert 'Distance' in circuit.corners.columns 