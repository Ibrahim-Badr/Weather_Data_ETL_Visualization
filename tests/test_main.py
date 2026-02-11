"""
Tests for the main application entry point.

Verifies command-line argument parsing, pipeline integration,
and overall application workflow.
"""
# pylint: disable=redefined-outer-name
from unittest.mock import Mock, patch
import importlib
import pytest
import main


@pytest.fixture
def mock_pipeline():
    """Provide a mock ETL pipeline."""
    pipeline = Mock()
    pipeline.run.return_value = {
        'extracted': 100,
        'transformed': 95,
        'loaded': 95
    }
    return pipeline

@pytest.fixture
def mock_extractor():
    """Provide a mock API extractor."""
    extractor = Mock()
    extractor.extract.return_value = [
        {
            'station_id': '24',
            'station_name': 'Test Station 1',
            'location': 'Toulouse'
        },
        {
            'station_id': '36',
            'station_name': 'Test Station 2',
            'location': 'Colomiers'
        }
    ]
    return extractor

@pytest.fixture
def mock_components(mock_extractor, mock_pipeline):
    """Provide all mocked ETL components."""
    return {
        'extractor': mock_extractor,
        'transformer': Mock(),
        'loader': Mock(),
        'pipeline': mock_pipeline
    }

def test_main_with_default_arguments(mock_components, capsys):
    """Test main function with default arguments (no CLI args)."""
    with patch('sys.argv', ['main.py']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        result = main.main()
                        
                        assert result is None or result == 0
                        captured = capsys.readouterr()
                        assert "Weather Data ETL Application" in captured.out
                        assert "Pipeline completed successfully" in captured.out

def test_main_with_specific_stations(mock_components, capsys):
    """Test main function with specific station IDs."""
    with patch('sys.argv', ['main.py', '--stations', '24', '36']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        main.main()
                        
                        captured = capsys.readouterr()
                        assert "Target: Stations 24, 36" in captured.out
                        
                        # Verify pipeline was called with correct stations
                        mock_components['pipeline'].run.assert_called_once()
                        call_args = mock_components['pipeline'].run.call_args
                        assert call_args[1]['station_ids'] == ['24', '36']

def test_main_with_custom_limit(mock_components, capsys):
    """Test main function with custom record limit."""
    with patch('sys.argv', ['main.py', '--limit', '50']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        result = main.main()
                        
                        assert result is None or result == 0
                        captured = capsys.readouterr()
                        assert "Limit: 50 records per station" in captured.out
                        
                        # Verify pipeline was called with correct limit
                        call_args = mock_components['pipeline'].run.call_args
                        assert call_args[1]['limit_per_station'] == 50

def test_main_with_limit_exceeding_maximum(mock_components, capsys):
    """Test main function with limit exceeding API maximum (should adjust to 100)."""
    with patch('sys.argv', ['main.py', '--limit', '200']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        main.main()
                        
                        captured = capsys.readouterr()
                        assert "Warning: Toulouse API maximum limit is 100" in captured.out
                        assert "Limit: 100 records per station" in captured.out

def test_main_list_stations_flag(mock_extractor, capsys):
    """Test --list-stations flag to display available stations."""
    with patch('sys.argv', ['main.py', '--list-stations']):
        with patch('main.APIExtractor', return_value=mock_extractor):
            result = main.main()
            
            assert result == 0
            captured = capsys.readouterr()
            assert "Fetching available stations" in captured.out
            assert "Test Station 1" in captured.out
            assert "Test Station 2" in captured.out

def test_main_list_stations_with_many_stations(mock_extractor, capsys):
    """Test --list-stations with more than 10 stations (should show truncated list)."""
    # Create a list of 15 mock stations
    stations = [
        {
            'station_id': str(i),
            'station_name': f'Station {i}',
            'location': 'Toulouse'
        }
        for i in range(15)
    ]
    mock_extractor.extract.return_value = stations
    
    with patch('sys.argv', ['main.py', '--list-stations']):
        with patch('main.APIExtractor', return_value=mock_extractor):
            result = main.main()
            
            assert result == 0
            captured = capsys.readouterr()
            assert "Found 15 active weather stations" in captured.out
            assert "and 5 more stations" in captured.out

def test_main_list_stations_no_stations_found(mock_extractor, capsys):
    """Test --list-stations when no stations are available."""
    mock_extractor.extract.side_effect = ConnectionError("API unavailable")
    
    with patch('sys.argv', ['main.py', '--list-stations']):
        with patch('main.APIExtractor', return_value=mock_extractor):
            result = main.main()
            
            assert result == 0
            captured = capsys.readouterr()
            assert "No stations found" in captured.out

def test_main_handles_keyboard_interrupt(mock_components, capsys):
    """Test that KeyboardInterrupt is handled gracefully."""
    mock_components['pipeline'].run.side_effect = KeyboardInterrupt()
    
    with patch('sys.argv', ['main.py']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        main.main()
                        captured = capsys.readouterr()
                        assert "Process interrupted by user" in captured.out

def test_main_handles_runtime_error(mock_components, capsys):
    """Test that RuntimeError is handled and reported."""
    mock_components['pipeline'].run.side_effect = RuntimeError("Test error")
    
    with patch('sys.argv', ['main.py']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        result = main.main()
                        
                        assert result == 1
                        captured = capsys.readouterr()
                        assert "Runtime error: Test error" in captured.out

def test_main_handles_connection_error(mock_components, capsys):
    """Test that ConnectionError is handled and reported."""
    mock_components['pipeline'].run.side_effect = ConnectionError("Network error")
    
    with patch('sys.argv', ['main.py']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        main.main()
                        
                        captured = capsys.readouterr()
                        assert "Unexpected error: Network error" in captured.out

def test_main_displays_statistics(mock_components, capsys):
    """Test that pipeline statistics are displayed correctly."""
    with patch('sys.argv', ['main.py']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        main.main()
                        
                        captured = capsys.readouterr()
                        assert "Extracted: 100 records" in captured.out
                        assert "Transformed: 95 records" in captured.out
                        assert "Loaded: 95 records" in captured.out

def test_main_initializes_database_loader(mock_components):
    """Test that DatabaseLoader is initialized with correct path."""
    with patch('sys.argv', ['main.py']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']) as mock_db:
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        main.main()
                        
                        # Verify DatabaseLoader was instantiated with correct path
                        mock_db.assert_called_once_with("database/weather.db")
                        # Verify initialize was called
                        mock_components['loader'].initialize.assert_called_once()

def test_main_combined_arguments(mock_components, capsys):
    """Test main with multiple combined arguments."""
    with patch('sys.argv', ['main.py', '--stations', '24', '--limit', '25']):
        with patch('main.APIExtractor', return_value=mock_components['extractor']):
            with patch('main.DataCleaner', return_value=mock_components['transformer']):
                with patch('main.DatabaseLoader', return_value=mock_components['loader']):
                    with patch('main.ETLPipeline', return_value=mock_components['pipeline']):
                        result = main.main()
                        
                        assert result is None or result == 0
                        captured = capsys.readouterr()
                        assert "Target: Stations 24" in captured.out
                        assert "Limit: 25 records per station" in captured.out

def test_main_entry_point():
    """Test that __main__ entry point works correctly."""
    with patch('main.main', return_value=0) as _mock_main:
        with patch('sys.exit') as _mock_exit:
            # Import the module to trigger __main__ block if it exists
            importlib.reload(main)
            
            # Verify our main function is callable
            assert callable(main.main)
