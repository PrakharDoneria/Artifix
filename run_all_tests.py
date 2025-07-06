#!/usr/bin/env python3
"""
Comprehensive test suite runner for Artifix
"""

import sys
import time
import subprocess
import os

def run_test_file(test_file, description):
    """Run a single test file and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ Test {test_file} timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running test {test_file}: {e}")
        return False


def main():
    """Run all comprehensive tests"""
    print("🚀 Artifix Comprehensive Test Suite")
    print("=" * 70)
    print("Running all test cases to verify functionality...")
    
    start_time = time.time()
    
    # Define all test files
    test_cases = [
        ("test_voice_features.py", "Voice Features Integration Tests"),
        ("test_audio_visualizer.py", "Audio Visualizer Unit Tests"),
        ("test_clap_detection.py", "Clap Detection Unit Tests"),
        ("test_ui_layout.py", "UI Layout Unit Tests"),
    ]
    
    results = []
    
    # Run each test suite
    for test_file, description in test_cases:
        if os.path.exists(test_file):
            success = run_test_file(test_file, description)
            results.append((test_file, description, success))
        else:
            print(f"⚠️ Test file {test_file} not found, skipping...")
            results.append((test_file, description, False))
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*70}")
    print("📊 TEST SUITE SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    print(f"Total test suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Duration: {duration:.2f} seconds")
    
    print("\nDetailed Results:")
    for test_file, description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {description}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! All {total} test suites completed successfully.")
        print("\n✨ Summary of tested functionality:")
        print("  • AudioVisualizer: Canvas-free Siri-like visualization")
        print("  • ClapDetectionManager: Double clap detection system")
        print("  • UI Layout: Voice-only interface components")
        print("  • Integration: Complete voice features workflow")
        print("\n🔧 Technical fixes implemented:")
        print("  • Fixed AttributeError: module 'flet' has no attribute 'Canvas'")
        print("  • Replaced Canvas with Container-based visualization")
        print("  • Updated mock implementation to match real flet API")
        print("  • Added comprehensive test coverage for all functions")
        
        return True
    else:
        print(f"\n❌ SOME TESTS FAILED! {total - passed} out of {total} test suites failed.")
        print("Please check the error messages above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)