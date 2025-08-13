"""
Tests for Task Mapping
Verifies that task types are correctly mapped to automation service functions.
"""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Add project directories to Python path
project_root = Path(__file__).parent.parent
shared_path = project_root / "shared"
worker_path = project_root / "worker_service"
automation_path = project_root / "automation_service"

sys.path.insert(0, str(shared_path))
sys.path.insert(0, str(worker_path))
sys.path.insert(0, str(automation_path))

# Import modules to test
from worker_service.tasks import TASK_MAPPING, get_automation_function, test_automation_task
import batch_approval_service

class TestTaskMapping:
    """Test cases for task mapping functionality."""
    
    def test_task_mapping_exists(self):
        """Test that TASK_MAPPING dictionary exists and has expected tasks."""
        assert isinstance(TASK_MAPPING, dict)
        assert len(TASK_MAPPING) > 0
        
        # Check for expected task types
        expected_tasks = ['approve_batches', 'test_task']
        for task_type in expected_tasks:
            assert task_type in TASK_MAPPING, f"Task type '{task_type}' not found in TASK_MAPPING"
    
    def test_approve_batches_mapping(self):
        """Test that approve_batches maps to the correct function."""
        task_type = 'approve_batches'
        expected_function_path = 'batch_approval_service.approve_batches'
        
        assert task_type in TASK_MAPPING
        assert TASK_MAPPING[task_type] == expected_function_path
    
    def test_test_task_mapping(self):
        """Test that test_task maps to the correct function."""
        task_type = 'test_task'
        expected_function_path = 'test_automation_task'
        
        assert task_type in TASK_MAPPING
        assert TASK_MAPPING[task_type] == expected_function_path
    
    def test_get_automation_function_valid_task(self):
        """Test getting automation function for valid task types."""
        # Test approve_batches
        func = get_automation_function('approve_batches')
        assert func is not None
        assert callable(func)
        assert func == batch_approval_service.approve_batches
        
        # Test test_task
        func = get_automation_function('test_task')
        assert func is not None
        assert callable(func)
        assert func == test_automation_task
    
    def test_get_automation_function_invalid_task(self):
        """Test getting automation function for invalid task type."""
        func = get_automation_function('nonexistent_task')
        assert func is None
    
    def test_get_automation_function_empty_task(self):
        """Test getting automation function for empty task type."""
        func = get_automation_function('')
        assert func is None
    
    def test_test_automation_task_execution(self):
        """Test that test_automation_task executes correctly."""
        params = {
            'duration': 0.1,  # Short duration for testing
            'success_rate': 1.0  # Ensure success
        }
        
        result = test_automation_task(params)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'approved_count' in result
        assert 'details' in result
        assert 'summary' in result
        assert 'execution_time' in result
        
        # Verify result values
        assert result['status'] == 'completed'
        assert isinstance(result['approved_count'], int)
        assert result['approved_count'] > 0
        assert isinstance(result['details'], list)
        assert len(result['details']) > 0
        assert isinstance(result['summary'], str)
        assert isinstance(result['execution_time'], float)
    
    def test_test_automation_task_failure(self):
        """Test that test_automation_task can simulate failures."""
        params = {
            'duration': 0.1,
            'success_rate': 0.0  # Force failure
        }
        
        with pytest.raises(Exception) as exc_info:
            test_automation_task(params)
        
        assert "Test task failed" in str(exc_info.value)
    
    @patch('batch_approval_service.approve_batches')
    def test_batch_approval_function_callable(self, mock_approve_batches):
        """Test that batch approval function can be called."""
        # Setup mock
        mock_approve_batches.return_value = {
            'status': 'completed',
            'approved_count': 3,
            'details': [],
            'summary': 'Mock approval completed'
        }
        
        # Get function
        func = get_automation_function('approve_batches')
        assert func is not None
        
        # Call function
        params = {'batch_ids': ['B001', 'B002', 'B003']}
        result = func(params)
        
        # Verify mock was called
        mock_approve_batches.assert_called_once_with(params)
        
        # Verify result
        assert result['status'] == 'completed'
        assert result['approved_count'] == 3
    
    def test_all_mapped_functions_exist(self):
        """Test that all functions in TASK_MAPPING actually exist."""
        for task_type, function_path in TASK_MAPPING.items():
            func = get_automation_function(task_type)
            assert func is not None, f"Function for task '{task_type}' (path: '{function_path}') does not exist"
            assert callable(func), f"Function for task '{task_type}' is not callable"

class TestTaskMappingIntegration:
    """Integration tests for task mapping with worker service."""
    
    @patch('worker_service.tasks.app')
    def test_task_mapping_integration(self, mock_celery_app):
        """Test integration between task mapping and Celery tasks."""
        # This would test the actual Celery task execution
        # For now, we'll just verify the mapping works
        
        for task_type in TASK_MAPPING.keys():
            func = get_automation_function(task_type)
            assert func is not None, f"Task type '{task_type}' should have a valid function"
    
    def test_task_mapping_consistency(self):
        """Test that task mapping is consistent and complete."""
        # Verify no duplicate mappings
        function_paths = list(TASK_MAPPING.values())
        assert len(function_paths) == len(set(function_paths)), "Duplicate function paths found in TASK_MAPPING"
        
        # Verify all task types are strings
        for task_type in TASK_MAPPING.keys():
            assert isinstance(task_type, str), f"Task type '{task_type}' should be a string"
            assert len(task_type) > 0, f"Task type should not be empty"
        
        # Verify all function paths are strings
        for function_path in TASK_MAPPING.values():
            assert isinstance(function_path, str), f"Function path '{function_path}' should be a string"
            assert len(function_path) > 0, f"Function path should not be empty"

if __name__ == '__main__':
    # Run tests when script is executed directly
    pytest.main([__file__, '-v'])
