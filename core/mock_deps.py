# Mock implementations for development when dependencies are not available

class MockFlet:
    """Mock Flet implementation for development"""
    
    class Container:
        def __init__(self, **kwargs):
            self.visible = kwargs.get('visible', True)
            self.content = kwargs.get('content')
            self.bgcolor = kwargs.get('bgcolor')
            self.width = kwargs.get('width')
            self.height = kwargs.get('height')
            self.border_radius = kwargs.get('border_radius')
            self.padding = kwargs.get('padding')
            self.margin = kwargs.get('margin')
            self.expand = kwargs.get('expand', False)
            
        def update(self):
            pass
    
    class Row:
        def __init__(self, controls=None, **kwargs):
            self.controls = controls or []
            self.alignment = kwargs.get('alignment')
            self.spacing = kwargs.get('spacing', 0)
            
        def update(self):
            pass
    
    class Column:
        def __init__(self, controls=None, **kwargs):
            self.controls = controls or []
            self.spacing = kwargs.get('spacing', 0)
            self.horizontal_alignment = kwargs.get('horizontal_alignment')
            
        def update(self):
            pass
    
    class Text:
        def __init__(self, value="", **kwargs):
            self.value = value
            self.size = kwargs.get('size', 16)
            self.color = kwargs.get('color', '#000000')
            self.weight = kwargs.get('weight')
            self.text_align = kwargs.get('text_align')
            self.selectable = kwargs.get('selectable', False)
            
        def update(self):
            pass
    
    class TextField:
        def __init__(self, **kwargs):
            self.value = ""
            self.hint_text = kwargs.get('hint_text', '')
            self.read_only = kwargs.get('read_only', False)
            self.expand = kwargs.get('expand', False)
            
        def update(self):
            pass
    
    class IconButton:
        def __init__(self, **kwargs):
            self.icon = kwargs.get('icon')
            self.icon_color = kwargs.get('icon_color')
            self.tooltip = kwargs.get('tooltip')
            self.on_click = kwargs.get('on_click')
            self.icon_size = kwargs.get('icon_size', 24)
            
        def update(self):
            pass
    
    class ListView:
        def __init__(self, **kwargs):
            self.controls = []
            self.expand = kwargs.get('expand', False)
            self.spacing = kwargs.get('spacing', 0)
            self.padding = kwargs.get('padding', 0)
            self.auto_scroll = kwargs.get('auto_scroll', False)
            
        def update(self):
            pass
    
    class CircleAvatar:
        def __init__(self, **kwargs):
            self.content = kwargs.get('content')
            self.color = kwargs.get('color')
            self.bgcolor = kwargs.get('bgcolor')
            self.radius = kwargs.get('radius', 20)
            
        def update(self):
            pass
    
    class Canvas:
        def __init__(self, **kwargs):
            self.shapes = []
            self.width = kwargs.get('width', 300)
            self.height = kwargs.get('height', 100)
            
        def update(self):
            pass
    
    # Constants and enums
    class Icons:
        MIC = "mic"
        SEND_ROUNDED = "send"
    
    class FontWeight:
        BOLD = "bold"
    
    class ThemeMode:
        LIGHT = "light"
        DARK = "dark"
    
    class MainAxisAlignment:
        START = "start"
        END = "end"
        CENTER = "center"
        SPACE_BETWEEN = "space_between"
    
    class CrossAxisAlignment:
        START = "start"
        END = "end"
        CENTER = "center"
    
    class TextAlign:
        LEFT = "left"
        RIGHT = "right"
        CENTER = "center"
    
    class colors:
        WHITE = "#FFFFFF"
        BLACK = "#000000"
        BLUE = "#007AFF"
        TRANSPARENT = "transparent"
    
    # Create static instances for border_radius, padding, margin, and alignment
    border_radius = type('BorderRadius', (), {
        'all': lambda self, radius: radius
    })()
    
    padding = type('Padding', (), {
        'only': lambda self, **kwargs: kwargs  
    })()
    
    margin = type('Margin', (), {
        'only': lambda self, **kwargs: kwargs
    })()
    
    alignment = type('Alignment', (), {
        'center': 'center',
        'topLeft': 'topLeft',
        'topCenter': 'topCenter',
        'topRight': 'topRight',
        'centerLeft': 'centerLeft',
        'centerRight': 'centerRight',
        'bottomLeft': 'bottomLeft', 
        'bottomCenter': 'bottomCenter',
        'bottomRight': 'bottomRight'
    })()
    
    class TextStyle:
        def __init__(self, **kwargs):
            self.color = kwargs.get('color')
            self.size = kwargs.get('size')
            self.weight = kwargs.get('weight')
    
    class animation:
        class Animation:
            def __init__(self, duration, curve):
                self.duration = duration
                self.curve = curve

# Try to import real flet, fallback to mock
try:
    import flet as ft
    print("Using real Flet")
except ImportError:
    ft = MockFlet()
    print("Using mock Flet implementation")

# Export the flet module (real or mock)
__all__ = ['ft']