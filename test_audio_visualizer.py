#!/usr/bin/env python3
"""
Comprehensive test cases for AudioVisualizer and AudioVisualizationManager
"""

import sys
import time
import threading
import unittest
from unittest.mock import patch, MagicMock

# Import the modules to test
try:
    from core.audio_visualizer import AudioVisualizer, AudioVisualizationManager
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestAudioVisualizer(unittest.TestCase):
    """Test cases for AudioVisualizer class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.visualizer = AudioVisualizer(width=200, height=80)
    
    def tearDown(self):
        """Clean up after each test method."""
        if self.visualizer.is_active:
            self.visualizer.stop_visualization()
        # Give time for threads to stop
        time.sleep(0.1)
    
    def test_init_default_parameters(self):
        """Test AudioVisualizer initialization with default parameters"""
        viz = AudioVisualizer()
        self.assertEqual(viz.width, 300)
        self.assertEqual(viz.height, 100)
        self.assertEqual(viz.num_bars, 20)
        self.assertFalse(viz.is_active)
        self.assertEqual(viz.time_offset, 0)
        self.assertIsNotNone(viz.container)
        self.assertIsNotNone(viz.bar_containers)
        self.assertEqual(len(viz.bar_containers), 20)
    
    def test_init_custom_parameters(self):
        """Test AudioVisualizer initialization with custom parameters"""
        viz = AudioVisualizer(width=400, height=120)
        self.assertEqual(viz.width, 400)
        self.assertEqual(viz.height, 120)
        self.assertEqual(viz.num_bars, 20)
        self.assertFalse(viz.is_active)
        self.assertEqual(viz.time_offset, 0)
    
    def test_start_visualization(self):
        """Test starting visualization"""
        self.assertFalse(self.visualizer.is_active)
        self.assertFalse(self.visualizer.container.visible)
        
        self.visualizer.start_visualization()
        
        self.assertTrue(self.visualizer.is_active)
        self.assertTrue(self.visualizer.container.visible)
        self.assertIsNotNone(self.visualizer.animation_thread)
        self.assertTrue(self.visualizer.animation_thread.is_alive())
    
    def test_start_visualization_already_active(self):
        """Test starting visualization when already active"""
        self.visualizer.start_visualization()
        first_thread = self.visualizer.animation_thread
        
        # Start again - should not create new thread
        self.visualizer.start_visualization()
        
        self.assertEqual(first_thread, self.visualizer.animation_thread)
    
    def test_stop_visualization(self):
        """Test stopping visualization"""
        self.visualizer.start_visualization()
        self.assertTrue(self.visualizer.is_active)
        
        self.visualizer.stop_visualization()
        
        self.assertFalse(self.visualizer.is_active)
        self.assertFalse(self.visualizer.container.visible)
        
        # Give time for thread to stop
        time.sleep(0.1)
        if self.visualizer.animation_thread:
            self.assertFalse(self.visualizer.animation_thread.is_alive())
    
    def test_stop_visualization_not_active(self):
        """Test stopping visualization when not active"""
        self.assertFalse(self.visualizer.is_active)
        
        # Should not raise any errors
        self.visualizer.stop_visualization()
        
        self.assertFalse(self.visualizer.is_active)
    
    def test_update_bars(self):
        """Test updating bars animation"""
        initial_heights = [bar.height for bar in self.visualizer.bar_containers]
        
        self.visualizer._update_bars()
        
        # Heights should be different after update
        new_heights = [bar.height for bar in self.visualizer.bar_containers]
        # At least some bars should have different heights
        self.assertNotEqual(initial_heights, new_heights)
        
        # All heights should be at least 5 (minimum height)
        for height in new_heights:
            self.assertGreaterEqual(height, 5)
            self.assertLessEqual(height, self.visualizer.height * 0.8)
    
    def test_get_bar_color_high_intensity(self):
        """Test bar color for high intensity"""
        color = self.visualizer._get_bar_color(0.8)
        self.assertEqual(color, '#FFFFFF')
    
    def test_get_bar_color_medium_intensity(self):
        """Test bar color for medium intensity"""
        color = self.visualizer._get_bar_color(0.5)
        self.assertEqual(color, '#66B3FF')
    
    def test_get_bar_color_low_intensity(self):
        """Test bar color for low intensity"""
        color = self.visualizer._get_bar_color(0.2)
        self.assertEqual(color, '#007AFF')
    
    def test_pulse(self):
        """Test pulse animation"""
        self.assertFalse(self.visualizer.is_active)
        
        self.visualizer.pulse()
        
        self.assertTrue(self.visualizer.is_active)
        self.assertTrue(self.visualizer.container.visible)
        
        # Should auto-stop after 2 seconds (test with shorter wait)
        time.sleep(0.1)  # Just verify it started
    
    def test_set_listening_mode_true(self):
        """Test setting listening mode to true"""
        self.assertFalse(self.visualizer.is_active)
        
        self.visualizer.set_listening_mode(True)
        
        self.assertTrue(self.visualizer.is_active)
        self.assertTrue(self.visualizer.container.visible)
    
    def test_set_listening_mode_false(self):
        """Test setting listening mode to false"""
        self.visualizer.start_visualization()
        self.assertTrue(self.visualizer.is_active)
        
        self.visualizer.set_listening_mode(False)
        
        self.assertFalse(self.visualizer.is_active)
        self.assertFalse(self.visualizer.container.visible)
    
    def test_animate_loop(self):
        """Test animation loop functionality"""
        self.visualizer.start_visualization()
        initial_offset = self.visualizer.time_offset
        
        # Let animation run for a short time
        time.sleep(0.2)
        
        # Time offset should have increased
        self.assertGreater(self.visualizer.time_offset, initial_offset)


class TestAudioVisualizationManager(unittest.TestCase):
    """Test cases for AudioVisualizationManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = AudioVisualizationManager()
    
    def tearDown(self):
        """Clean up after each test method."""
        if self.manager.is_listening:
            self.manager.stop_listening_visualization()
        # Give time for threads to stop
        time.sleep(0.1)
    
    def test_init(self):
        """Test AudioVisualizationManager initialization"""
        self.assertIsNotNone(self.manager.visualizer)
        self.assertFalse(self.manager.is_listening)
        self.assertIsInstance(self.manager.visualizer, AudioVisualizer)
    
    def test_get_visualization_widget(self):
        """Test getting visualization widget"""
        widget = self.manager.get_visualization_widget()
        self.assertIsNotNone(widget)
        self.assertEqual(widget, self.manager.visualizer.container)
    
    def test_start_listening_visualization(self):
        """Test starting listening visualization"""
        self.assertFalse(self.manager.is_listening)
        self.assertFalse(self.manager.visualizer.is_active)
        
        self.manager.start_listening_visualization()
        
        self.assertTrue(self.manager.is_listening)
        self.assertTrue(self.manager.visualizer.is_active)
    
    def test_stop_listening_visualization(self):
        """Test stopping listening visualization"""
        self.manager.start_listening_visualization()
        self.assertTrue(self.manager.is_listening)
        
        self.manager.stop_listening_visualization()
        
        self.assertFalse(self.manager.is_listening)
        self.assertFalse(self.manager.visualizer.is_active)
    
    def test_show_response_pulse_when_not_listening(self):
        """Test showing response pulse when not listening"""
        self.assertFalse(self.manager.is_listening)
        self.assertFalse(self.manager.visualizer.is_active)
        
        self.manager.show_response_pulse()
        
        # Should start visualization temporarily
        self.assertTrue(self.manager.visualizer.is_active)
    
    def test_show_response_pulse_when_listening(self):
        """Test showing response pulse when already listening"""
        self.manager.start_listening_visualization()
        self.assertTrue(self.manager.is_listening)
        
        # Should not change listening state
        self.manager.show_response_pulse()
        
        self.assertTrue(self.manager.is_listening)
        self.assertTrue(self.manager.visualizer.is_active)
    
    def test_is_active(self):
        """Test checking if visualization is active"""
        self.assertFalse(self.manager.is_active())
        
        self.manager.start_listening_visualization()
        self.assertTrue(self.manager.is_active())
        
        self.manager.stop_listening_visualization()
        self.assertFalse(self.manager.is_active())


class TestIntegration(unittest.TestCase):
    """Integration tests for AudioVisualizer components"""
    
    def test_visualizer_with_manager(self):
        """Test visualizer working with manager"""
        manager = AudioVisualizationManager()
        
        # Test complete flow
        widget = manager.get_visualization_widget()
        self.assertIsNotNone(widget)
        
        manager.start_listening_visualization()
        self.assertTrue(manager.is_active())
        
        # Let it run briefly
        time.sleep(0.1)
        
        manager.stop_listening_visualization()
        self.assertFalse(manager.is_active())
    
    def test_multiple_managers(self):
        """Test multiple managers can work independently"""
        manager1 = AudioVisualizationManager()
        manager2 = AudioVisualizationManager()
        
        manager1.start_listening_visualization()
        self.assertTrue(manager1.is_active())
        self.assertFalse(manager2.is_active())
        
        manager2.start_listening_visualization()
        self.assertTrue(manager1.is_active())
        self.assertTrue(manager2.is_active())
        
        manager1.stop_listening_visualization()
        self.assertFalse(manager1.is_active())
        self.assertTrue(manager2.is_active())
        
        manager2.stop_listening_visualization()
        self.assertFalse(manager1.is_active())
        self.assertFalse(manager2.is_active())


def run_tests():
    """Run all tests and return success status"""
    print("🧪 Running comprehensive AudioVisualizer tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [TestAudioVisualizer, TestAudioVisualizationManager, TestIntegration]
    
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