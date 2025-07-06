#!/usr/bin/env python3
"""
Comprehensive test cases for UI Layout functionality
"""

import sys
import time
import unittest
from unittest.mock import patch, MagicMock, Mock

# Import the modules to test
try:
    from ui.layout import UI
    from core.audio_visualizer import AudioVisualizationManager
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestUI(unittest.TestCase):
    """Test cases for UI class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.on_send_called = False
        self.on_voice_called = False
        
        def mock_on_send(event):
            self.on_send_called = True
        
        def mock_on_voice(event):
            self.on_voice_called = True
        
        self.mock_on_send = mock_on_send
        self.mock_on_voice = mock_on_voice
        self.ui = UI(self.mock_on_send, self.mock_on_voice)
    
    def test_init(self):
        """Test UI initialization"""
        self.assertEqual(self.ui.on_send, self.mock_on_send)
        self.assertEqual(self.ui.on_voice, self.mock_on_voice)
        self.assertIsNone(self.ui.page)
        self.assertIsNone(self.ui.chat)
        self.assertIsNone(self.ui.input)
        self.assertIsNone(self.ui.typing)
        self.assertIsInstance(self.ui.audio_viz_manager, AudioVisualizationManager)
        self.assertIsNone(self.ui.status_text)
    
    def test_build_page_setup(self):
        """Test build method sets up page correctly"""
        mock_page = Mock()
        mock_page.add = Mock()
        
        self.ui.build(mock_page)
        
        # Check page setup
        self.assertEqual(self.ui.page, mock_page)
        self.assertEqual(mock_page.title, "Artifix")
        self.assertEqual(mock_page.bgcolor, "#1a1a1a")
        self.assertEqual(mock_page.padding, 0)
        self.assertEqual(mock_page.spacing, 0)
        
        # Check components were created
        self.assertIsNotNone(self.ui.chat)
        self.assertIsNotNone(self.ui.typing)
        self.assertIsNotNone(self.ui.status_text)
        
        # Check page.add was called
        mock_page.add.assert_called_once()
    
    def test_add_message_user(self):
        """Test adding user message"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        mock_page.width = 800  # Add numeric width
        self.ui.build(mock_page)
        
        test_message = "Hello, this is a user message"
        self.ui.add_message(test_message, True)
        
        # Should add message to chat
        self.assertGreater(len(self.ui.chat.controls), 0)
    
    def test_add_message_bot(self):
        """Test adding bot message"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        mock_page.width = 800  # Add numeric width
        self.ui.build(mock_page)
        
        test_message = "Hello, this is a bot response"
        self.ui.add_message(test_message, False)
        
        # Should add message to chat
        self.assertGreater(len(self.ui.chat.controls), 0)
    
    def test_show_typing(self):
        """Test showing typing indicator"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        self.ui.show_typing(True)
        
        # Typing indicator should be visible
        self.assertTrue(self.ui.typing.controls[0].visible)
    
    def test_hide_typing(self):
        """Test hiding typing indicator"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        # First show, then hide
        self.ui.show_typing(True)
        self.ui.show_typing(False)
        
        # Typing indicator should be hidden
        self.assertFalse(self.ui.typing.controls[0].visible)
    
    def test_update_status(self):
        """Test updating status"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        new_status = "Listening..."
        self.ui.update_status(new_status)
        
        self.assertEqual(self.ui.status_text.value, new_status)
    
    def test_get_input(self):
        """Test getting input value"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        # Should return empty string for voice-only mode
        input_value = self.ui.get_input()
        self.assertEqual(input_value, "")
    
    def test_clear_input(self):
        """Test clearing input (compatibility method)"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        # Should not raise any errors (compatibility method)
        self.ui.clear_input()
    
    def test_show_response_pulse(self):
        """Test showing response pulse"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        # Should not raise any errors
        self.ui.show_response_pulse()
    
    def test_start_listening_visualization(self):
        """Test starting listening visualization"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        self.ui.start_listening_visualization()
        
        # Should start the audio visualization
        self.assertTrue(self.ui.audio_viz_manager.is_active())
    
    def test_stop_listening_visualization(self):
        """Test stopping listening visualization"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        # Start then stop
        self.ui.start_listening_visualization()
        self.ui.stop_listening_visualization()
        
        # Should stop the audio visualization
        self.assertFalse(self.ui.audio_viz_manager.is_active())
    
    def test_set_voice_mode_status(self):
        """Test setting voice mode status messages"""
        # Setup mock page first
        mock_page = Mock()
        mock_page.add = Mock()
        self.ui.build(mock_page)
        
        # Test listening status
        self.ui.start_listening_visualization()
        self.assertEqual(self.ui.status_text.value, "Listening... Speak now")
        
        # Test ready status
        self.ui.stop_listening_visualization()
        self.assertEqual(self.ui.status_text.value, "Ready - Say 'Hey Artifix' or double clap to start")


class TestUIIntegration(unittest.TestCase):
    """Integration tests for UI components"""
    
    def test_ui_with_audio_visualization(self):
        """Test UI integration with audio visualization"""
        def dummy_callback(event):
            pass
        
        ui = UI(dummy_callback, dummy_callback)
        
        # Setup mock page
        mock_page = Mock()
        mock_page.add = Mock()
        ui.build(mock_page)
        
        # Test visualization flow
        ui.start_listening_visualization()
        self.assertTrue(ui.audio_viz_manager.is_active())
        
        ui.stop_listening_visualization()
        self.assertFalse(ui.audio_viz_manager.is_active())
    
    def test_message_flow(self):
        """Test complete message flow"""
        def dummy_callback(event):
            pass
        
        ui = UI(dummy_callback, dummy_callback)
        
        # Setup mock page
        mock_page = Mock()
        mock_page.add = Mock()
        mock_page.width = 800  # Add numeric width
        ui.build(mock_page)
        
        # Test message flow
        ui.add_message("User message", True)
        ui.show_typing(True)
        
        # Wait briefly to simulate processing
        time.sleep(0.1)
        
        ui.show_typing(False)
        ui.add_message("Bot response", False)
        
        # Should have 2 messages in chat
        self.assertGreaterEqual(len(ui.chat.controls), 2)
    
    def test_status_updates(self):
        """Test status update flow"""
        def dummy_callback(event):
            pass
        
        ui = UI(dummy_callback, dummy_callback)
        
        # Setup mock page
        mock_page = Mock()
        mock_page.add = Mock()
        ui.build(mock_page)
        
        # Test status flow
        statuses = [
            "Ready",
            "Listening...", 
            "Processing...",
            "Speaking...",
            "Ready"
        ]
        
        for status in statuses:
            ui.update_status(status)
            self.assertEqual(ui.status_text.value, status)
    
    def test_visualization_flow(self):
        """Test visualization state changes"""
        def dummy_callback(event):
            pass
        
        ui = UI(dummy_callback, dummy_callback)
        
        # Setup mock page
        mock_page = Mock()
        mock_page.add = Mock()
        ui.build(mock_page)
        
        # Test visualization changes
        ui.start_listening_visualization()
        self.assertTrue(ui.audio_viz_manager.is_active())
        self.assertEqual(ui.status_text.value, "Listening... Speak now")
        
        ui.stop_listening_visualization()
        self.assertFalse(ui.audio_viz_manager.is_active())
        self.assertEqual(ui.status_text.value, "Ready - Say 'Hey Artifix' or double clap to start")
        
        ui.show_response_pulse()  # Should not change active state but create pulse


def run_tests():
    """Run all tests and return success status"""
    print("🧪 Running comprehensive UI Layout tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [TestUI, TestUIIntegration]
    
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