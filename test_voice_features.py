#!/usr/bin/env python3
"""
Test script to demonstrate the new Artifix voice-only features
"""

import sys
import time
import threading

# Test the core new functionality
def test_audio_visualization():
    """Test the audio visualization component"""
    print("🎵 Testing Audio Visualization...")
    try:
        from core.audio_visualizer import AudioVisualizationManager
        
        viz_manager = AudioVisualizationManager()
        
        # Test listening visualization
        print("  - Starting listening visualization...")
        viz_manager.start_listening_visualization()
        time.sleep(2)
        
        print("  - Stopping listening visualization...")
        viz_manager.stop_listening_visualization()
        
        # Test response pulse
        print("  - Testing response pulse...")
        viz_manager.show_response_pulse()
        time.sleep(1)
        
        print("  ✓ Audio visualization test completed")
        return True
        
    except Exception as e:
        print(f"  ✗ Audio visualization test failed: {e}")
        return False

def test_clap_detection():
    """Test the clap detection component"""
    print("👏 Testing Clap Detection...")
    try:
        from core.clap_detection import ClapDetectionManager
        
        # Create callback function
        def on_double_clap():
            print("  - Double clap detected in callback!")
        
        clap_manager = ClapDetectionManager(on_double_clap)
        
        print("  - Starting clap detection...")
        clap_manager.start_listening()
        
        print("  - Clap detection running for 3 seconds...")
        time.sleep(3)
        
        print("  - Stopping clap detection...")
        clap_manager.stop_listening()
        
        print("  ✓ Clap detection test completed")
        return True
        
    except Exception as e:
        print(f"  ✗ Clap detection test failed: {e}")
        return False

def test_voice_ui():
    """Test the voice-only UI"""
    print("🎤 Testing Voice UI...")
    try:
        from ui.layout import UI
        
        def mock_send(event):
            print("  - Mock send called")
            
        def mock_voice(event):
            print("  - Mock voice called")
        
        ui = UI(mock_send, mock_voice)
        print("  - UI created successfully")
        
        # Test status updates
        ui.update_status("Test status message")
        print("  - Status update test completed")
        
        # Test visualization controls
        ui.start_listening_visualization()
        ui.stop_listening_visualization()
        ui.show_response_pulse()
        print("  - Visualization controls test completed")
        
        print("  ✓ Voice UI test completed")
        return True
        
    except Exception as e:
        print(f"  ✗ Voice UI test failed: {e}")
        return False

def test_documentation():
    """Test that documentation was created"""
    print("📖 Testing Documentation...")
    try:
        import os
        
        doc_file = "VOICE_COMMANDS.md"
        if os.path.exists(doc_file):
            with open(doc_file, 'r') as f:
                content = f.read()
                
            if len(content) > 1000:  # Should be substantial
                print(f"  - Documentation file exists ({len(content)} chars)")
                if "Double Clap Activation" in content:
                    print("  - Contains double clap documentation")
                if "Audio Visualization" in content:
                    print("  - Contains audio visualization documentation")
                if "Voice Commands" in content:
                    print("  - Contains voice commands documentation")
                    
                print("  ✓ Documentation test completed")
                return True
            else:
                print("  ✗ Documentation file too short")
                return False
        else:
            print(f"  ✗ Documentation file {doc_file} not found")
            return False
            
    except Exception as e:
        print(f"  ✗ Documentation test failed: {e}")
        return False

def demonstrate_features():
    """Demonstrate the new features"""
    print("\n🚀 Artifix Voice-Only Assistant Feature Demo")
    print("=" * 50)
    
    results = []
    
    # Test each component
    results.append(test_audio_visualization())
    results.append(test_clap_detection())
    results.append(test_voice_ui())
    results.append(test_documentation())
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("-" * 30)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Features are ready.")
        print("\n✨ New Features Added:")
        print("  • Apple Siri-like audio visualization")
        print("  • Double clap detection for hands-free activation")
        print("  • Voice-only interface (chat box removed)")
        print("  • Comprehensive voice commands documentation")
        
        print("\n🎯 How to use:")
        print("  1. Say 'Hey Artifix' or double clap to activate")
        print("  2. Speak your command when visualization appears")
        print("  3. Get audio response with visual feedback")
        print("  4. See VOICE_COMMANDS.md for all available commands")
    else:
        print(f"⚠️ {total - passed} tests failed. Check error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = demonstrate_features()
    sys.exit(0 if success else 1)