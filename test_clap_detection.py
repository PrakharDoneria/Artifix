#!/usr/bin/env python3
"""
Comprehensive test cases for ClapDetectionManager
"""

import sys
import time
import threading
import unittest
from unittest.mock import patch, MagicMock, Mock

# Import the modules to test
try:
    from core.clap_detection import ClapDetectionManager, MockClapDetector, EnhancedClapDetector
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestClapDetectionManager(unittest.TestCase):
    """Test cases for ClapDetectionManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.callback_called = False
        self.callback_count = 0
        
        def test_callback():
            self.callback_called = True
            self.callback_count += 1
        
        self.test_callback = test_callback
        self.manager = ClapDetectionManager(self.test_callback)
    
    def tearDown(self):
        """Clean up after each test method."""
        if self.manager.is_listening:
            self.manager.stop_listening()
        # Give time for threads to stop
        time.sleep(0.1)
    
    def test_init_with_callback(self):
        """Test ClapDetectionManager initialization with callback"""
        self.assertEqual(self.manager.callback, self.test_callback)
        self.assertFalse(self.manager.is_listening)
        self.assertIsNone(self.manager.listen_thread)
        self.assertIsNotNone(self.manager.clap_detector)
    
    def test_init_without_callback(self):
        """Test ClapDetectionManager initialization without callback"""
        manager = ClapDetectionManager()
        self.assertIsNone(manager.callback)
        self.assertFalse(manager.is_listening)
    
    def test_start_listening(self):
        """Test starting clap detection"""
        self.assertFalse(self.manager.is_listening)
        
        self.manager.start_listening()
        
        self.assertTrue(self.manager.is_listening)
        self.assertIsNotNone(self.manager.listen_thread)
        self.assertTrue(self.manager.listen_thread.is_alive())
    
    def test_start_listening_already_active(self):
        """Test starting clap detection when already active"""
        self.manager.start_listening()
        first_thread = self.manager.listen_thread
        
        # Start again - should not create new thread
        self.manager.start_listening()
        
        self.assertEqual(first_thread, self.manager.listen_thread)
    
    def test_stop_listening(self):
        """Test stopping clap detection"""
        self.manager.start_listening()
        self.assertTrue(self.manager.is_listening)
        
        self.manager.stop_listening()
        
        self.assertFalse(self.manager.is_listening)
        
        # Give time for thread to stop
        time.sleep(0.1)
        if self.manager.listen_thread:
            self.assertFalse(self.manager.listen_thread.is_alive())
    
    def test_stop_listening_not_active(self):
        """Test stopping clap detection when not active"""
        self.assertFalse(self.manager.is_listening)
        
        # Should not raise any errors
        self.manager.stop_listening()
        
        self.assertFalse(self.manager.is_listening)
    
    def test_set_callback(self):
        """Test setting callback function"""
        new_callback_called = False
        
        def new_callback():
            nonlocal new_callback_called
            new_callback_called = True
        
        self.manager.set_callback(new_callback)
        self.assertEqual(self.manager.callback, new_callback)
        
        # Test new callback works
        self.manager._trigger_callback()
        self.assertTrue(new_callback_called)
    
    def test_set_clap_timeout(self):
        """Test setting clap timeout"""
        new_timeout = 3.5
        self.manager.set_clap_timeout(new_timeout)
        self.assertEqual(self.manager.clap_timeout, new_timeout)
    
    def test_trigger_callback_with_callback(self):
        """Test triggering callback when callback exists"""
        self.assertFalse(self.callback_called)
        
        self.manager._trigger_callback()
        
        self.assertTrue(self.callback_called)
        self.assertEqual(self.callback_count, 1)
    
    def test_trigger_callback_without_callback(self):
        """Test triggering callback when no callback set"""
        manager = ClapDetectionManager()
        
        # Should not raise any errors
        manager._trigger_callback()
    
    def test_listen_loop_with_mock_detector(self):
        """Test the listen loop with mock detector"""
        self.manager.start_listening()
        
        # Let it run briefly
        time.sleep(0.1)
        
        # Mock detector should be working
        self.assertTrue(self.manager.is_listening)
        
        self.manager.stop_listening()


class TestMockClapDetector(unittest.TestCase):
    """Test cases for MockClapDetector class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = MockClapDetector()
    
    def test_init(self):
        """Test MockClapDetector initialization"""
        self.assertIsInstance(self.detector, MockClapDetector)
    
    def test_detect_clap(self):
        """Test detect_clap method returns boolean"""
        result = self.detector.detect_clap()
        self.assertIsInstance(result, bool)
    
    def test_detect_clap_multiple_calls(self):
        """Test multiple calls to detect_clap"""
        results = []
        for i in range(3):  # Use fewer calls to avoid timing issues
            result = self.detector.detect_clap()
            results.append(result)
        
        # All should be boolean values
        self.assertEqual(len(results), 3)
        self.assertTrue(all(isinstance(r, bool) for r in results))


class TestEnhancedClapDetector(unittest.TestCase):
    """Test cases for EnhancedClapDetector class"""
    
    def test_init_fallback_to_mock(self):
        """Test EnhancedClapDetector falls back to mock when real detector unavailable"""
        # Since clap-detector package is likely not available in test environment
        detector = EnhancedClapDetector()
        
        # Should fall back to using MockClapDetector
        self.assertIsNotNone(detector)
    
    def test_detect_claps_method_exists(self):
        """Test that detect_clap method exists"""
        detector = EnhancedClapDetector()
        self.assertTrue(hasattr(detector, 'detect_clap'))
        self.assertTrue(callable(getattr(detector, 'detect_clap')))


class TestIntegration(unittest.TestCase):
    """Integration tests for clap detection components"""
    
    def test_full_clap_detection_flow(self):
        """Test complete clap detection flow"""
        callback_called = False
        
        def callback():
            nonlocal callback_called
            callback_called = True
        
        manager = ClapDetectionManager(callback)
        
        # Start listening
        manager.start_listening()
        self.assertTrue(manager.is_listening)
        
        # Test callback directly (since we can't easily simulate real claps)
        manager._trigger_callback()
        self.assertTrue(callback_called)
        
        # Stop listening
        manager.stop_listening()
        self.assertFalse(manager.is_listening)
    
    def test_multiple_callbacks(self):
        """Test multiple callback invocations"""
        callback_count = 0
        
        def callback():
            nonlocal callback_count
            callback_count += 1
        
        manager = ClapDetectionManager(callback)
        
        # Trigger multiple callbacks
        manager._trigger_callback()
        manager._trigger_callback()
        manager._trigger_callback()
        
        self.assertEqual(callback_count, 3)
    
    def test_thread_safety(self):
        """Test thread safety of clap detection"""
        manager = ClapDetectionManager()
        
        # Start and stop multiple times quickly
        for i in range(5):
            manager.start_listening()
            time.sleep(0.01)
            manager.stop_listening()
            time.sleep(0.01)
        
        # Should end in stopped state
        self.assertFalse(manager.is_listening)


def run_tests():
    """Run all tests and return success status"""
    print("🧪 Running comprehensive ClapDetectionManager tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [TestClapDetectionManager, TestMockClapDetector, TestEnhancedClapDetector, TestIntegration]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} tests failed")
    
    return success


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)