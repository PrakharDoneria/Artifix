import threading
import time
import math
try:
    import numpy as np
except ImportError:
    # Fallback for when numpy is not available
    class MockNumpy:
        @staticmethod
        def random(*args, **kwargs):
            import random
            return [random.random() for _ in range(args[0] if args else 10)]
        @staticmethod
        def sin(x):
            return math.sin(x)
        @staticmethod
        def linspace(start, stop, num):
            step = (stop - start) / (num - 1)
            return [start + i * step for i in range(num)]
        @staticmethod
        def array(data):
            return data
    np = MockNumpy()

try:
    import flet as ft
except ImportError:
    # Import mock flet
    from core.mock_deps import ft

class AudioVisualizer:
    """Apple Siri-like audio visualization component"""
    
    def __init__(self, width=300, height=100):
        self.width = width
        self.height = height
        self.is_active = False
        self.animation_thread = None
        self.bars = []
        self.time_offset = 0
        
        # Create visualization container
        self.canvas = ft.Canvas(
            width=self.width,
            height=self.height
        )
        
        self.container = ft.Container(
            content=self.canvas,
            width=self.width,
            height=self.height,
            bgcolor=ft.colors.TRANSPARENT,
            border_radius=ft.border_radius.all(10),
            visible=False
        )
        
        # Initialize bars
        self.num_bars = 20
        self.bar_width = self.width / self.num_bars * 0.6
        self.bar_spacing = self.width / self.num_bars
        
    def start_visualization(self):
        """Start the audio visualization animation"""
        if self.is_active:
            return
            
        self.is_active = True
        self.container.visible = True
        
        if hasattr(self.container, 'update'):
            self.container.update()
        
        # Start animation thread
        self.animation_thread = threading.Thread(target=self._animate, daemon=True)
        self.animation_thread.start()
        
    def stop_visualization(self):
        """Stop the audio visualization animation"""
        self.is_active = False
        self.container.visible = False
        
        if hasattr(self.container, 'update'):
            self.container.update()
            
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=1.0)
    
    def _animate(self):
        """Animation loop for the visualization"""
        while self.is_active:
            try:
                self._update_bars()
                if hasattr(self.canvas, 'update'):
                    self.canvas.update()
                time.sleep(0.05)  # ~20 FPS
                self.time_offset += 0.2
            except Exception as e:
                print(f"Visualization animation error: {e}")
                break
    
    def _update_bars(self):
        """Update the visualization bars with Siri-like animation"""
        if not hasattr(self.canvas, 'shapes'):
            return
            
        # Clear previous shapes
        self.canvas.shapes.clear()
        
        # Generate new bar heights with smooth wave-like motion
        for i in range(self.num_bars):
            # Create wave pattern with some randomness
            base_height = 0.3 + 0.4 * math.sin(self.time_offset + i * 0.5)
            noise = 0.2 * math.sin(self.time_offset * 3 + i * 1.2)
            bar_height = max(0.1, base_height + noise)
            
            # Scale to canvas height
            actual_height = bar_height * self.height * 0.8
            
            # Calculate bar position
            x = i * self.bar_spacing + (self.bar_spacing - self.bar_width) / 2
            y = (self.height - actual_height) / 2
            
            # Create bar shape (simplified for mock)
            bar_shape = {
                'type': 'rectangle',
                'x': x,
                'y': y,
                'width': self.bar_width,
                'height': actual_height,
                'color': self._get_bar_color(bar_height)
            }
            
            if hasattr(self.canvas, 'shapes'):
                self.canvas.shapes.append(bar_shape)
    
    def _get_bar_color(self, intensity):
        """Get bar color based on intensity (Siri-like gradient)"""
        # Simple color mapping from blue to white based on intensity
        if intensity > 0.7:
            return '#FFFFFF'  # White for high intensity
        elif intensity > 0.4:
            return '#66B3FF'  # Light blue for medium intensity
        else:
            return '#007AFF'  # Standard blue for low intensity
    
    def pulse(self):
        """Create a brief pulse animation (for responses)"""
        if not self.is_active:
            self.start_visualization()
            # Auto-stop after pulse
            threading.Timer(2.0, self.stop_visualization).start()
    
    def set_listening_mode(self, is_listening):
        """Set visualization mode based on listening state"""
        if is_listening:
            self.start_visualization()
        else:
            self.stop_visualization()

class AudioVisualizationManager:
    """Manager for audio visualization effects"""
    
    def __init__(self):
        self.visualizer = AudioVisualizer()
        self.is_listening = False
        
    def get_visualization_widget(self):
        """Get the visualization widget for UI integration"""
        return self.visualizer.container
    
    def start_listening_visualization(self):
        """Start visualization for listening mode"""
        self.is_listening = True
        self.visualizer.start_visualization()
    
    def stop_listening_visualization(self):
        """Stop visualization for listening mode"""
        self.is_listening = False
        self.visualizer.stop_visualization()
    
    def show_response_pulse(self):
        """Show a brief pulse for AI responses"""
        if not self.is_listening:
            self.visualizer.pulse()
    
    def is_active(self):
        """Check if visualization is currently active"""
        return self.visualizer.is_active