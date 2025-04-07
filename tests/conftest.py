"""Test configuration and shared fixtures."""

import pytest
import pandas as pd

@pytest.fixture
def mock_session():
    """Create a mock FastF1 session with sample driver data."""
    # Create a mock session object
    class MockSession:
        def __init__(self):
            # Create sample results data
            data = {
                'Abbreviation': ['HAM', 'VER', 'NOR'],
                'FirstName': ['Lewis', 'Max', 'Lando'],
                'LastName': ['Hamilton', 'Verstappen', 'Norris'],
                'DriverNumber': ['44', '1', '4'],
                'TeamName': ['Ferrari', 'Red Bull Racing', 'McLaren']
            }
            self.results = pd.DataFrame(data)
    
    return MockSession() 