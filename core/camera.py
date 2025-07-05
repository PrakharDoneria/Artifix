import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable, Dict, Any
import base64
import io
from PIL import Image
import json

class CameraManager:
    """Manages camera input for multimodal AI interaction"""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.is_capturing = False
        self.current_frame = None
        self.capture_thread = None
        self.frame_callbacks = []
        
    def start_camera(self) -> str:
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                return "Failed to open camera"
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_capturing = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            return "Camera started successfully"
        
        except Exception as e:
            return f"Failed to start camera: {str(e)}"
    
    def stop_camera(self) -> str:
        """Stop camera capture"""
        try:
            self.is_capturing = False
            
            if self.capture_thread:
                self.capture_thread.join(timeout=2.0)
            
            if self.cap:
                self.cap.release()
                self.cap = None
            
            return "Camera stopped"
        
        except Exception as e:
            return f"Failed to stop camera: {str(e)}"
    
    def _capture_loop(self):
        """Main camera capture loop"""
        while self.is_capturing and self.cap:
            try:
                ret, frame = self.cap.read()
                
                if ret:
                    self.current_frame = frame
                    
                    # Notify callbacks
                    for callback in self.frame_callbacks:
                        try:
                            callback(frame)
                        except Exception as e:
                            print(f"Frame callback error: {e}")
                
                time.sleep(1/30)  # 30 FPS
                
            except Exception as e:
                print(f"Camera capture error: {e}")
                break
    
    def capture_image(self, filename: str = None) -> str:
        """Capture a single image"""
        try:
            if not self.is_capturing or self.current_frame is None:
                return "Camera not active"
            
            if filename is None:
                filename = f"capture_{int(time.time())}.jpg"
            
            cv2.imwrite(filename, self.current_frame)
            return f"Image saved as {filename}"
        
        except Exception as e:
            return f"Failed to capture image: {str(e)}"
    
    def get_current_frame_base64(self) -> Optional[str]:
        """Get current frame as base64 encoded string"""
        try:
            if self.current_frame is None:
                return None
            
            # Convert to PIL Image
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Convert to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
        
        except Exception as e:
            print(f"Failed to encode frame: {e}")
            return None
    
    def add_frame_callback(self, callback: Callable):
        """Add callback function for frame processing"""
        self.frame_callbacks.append(callback)
    
    def remove_frame_callback(self, callback: Callable):
        """Remove frame callback"""
        if callback in self.frame_callbacks:
            self.frame_callbacks.remove(callback)
    
    def detect_motion(self, threshold: float = 0.1) -> bool:
        """Simple motion detection"""
        # This is a placeholder for motion detection
        # In a real implementation, you would compare frames
        return False
    
    def detect_faces(self) -> list:
        """Detect faces in current frame"""
        try:
            if self.current_frame is None:
                return []
            
            # Load face cascade (you might need to adjust the path)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale
            gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            face_data = []
            for (x, y, w, h) in faces:
                face_data.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                })
            
            return face_data
        
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get camera information"""
        if not self.cap:
            return {"error": "Camera not initialized"}
        
        try:
            return {
                "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
                "brightness": self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                "contrast": self.cap.get(cv2.CAP_PROP_CONTRAST),
                "is_capturing": self.is_capturing
            }
        except Exception as e:
            return {"error": f"Failed to get camera info: {str(e)}"}

class GestureDetector:
    """Basic gesture detection using camera input"""
    
    def __init__(self, camera_manager: CameraManager):
        self.camera_manager = camera_manager
        self.gesture_callbacks = {}
        self.is_detecting = False
        
        # Add frame callback for gesture detection
        self.camera_manager.add_frame_callback(self._process_frame)
    
    def start_detection(self):
        """Start gesture detection"""
        self.is_detecting = True
    
    def stop_detection(self):
        """Stop gesture detection"""
        self.is_detecting = False
    
    def add_gesture_callback(self, gesture_name: str, callback: Callable):
        """Add callback for specific gesture"""
        self.gesture_callbacks[gesture_name] = callback
    
    def _process_frame(self, frame):
        """Process frame for gesture detection"""
        if not self.is_detecting:
            return
        
        try:
            # Basic gesture detection (placeholder)
            # In a real implementation, you would use more sophisticated methods
            
            # Detect hand gestures, head movements, etc.
            # For now, just detect if someone is waving (mock implementation)
            
            faces = self.camera_manager.detect_faces()
            if len(faces) > 0:
                # Someone is visible, could trigger "presence" gesture
                if "presence_detected" in self.gesture_callbacks:
                    self.gesture_callbacks["presence_detected"]()
        
        except Exception as e:
            print(f"Gesture detection error: {e}")

class VisualAssistant:
    """Visual analysis assistant using camera input"""
    
    def __init__(self, camera_manager: CameraManager):
        self.camera_manager = camera_manager
    
    def describe_scene(self) -> str:
        """Describe what's currently visible in the camera"""
        try:
            if not self.camera_manager.is_capturing:
                return "Camera is not active"
            
            # Get current frame info
            faces = self.camera_manager.detect_faces()
            
            description_parts = []
            
            if len(faces) > 0:
                if len(faces) == 1:
                    description_parts.append("I can see one person in view")
                else:
                    description_parts.append(f"I can see {len(faces)} people in view")
            else:
                description_parts.append("I don't see any people in the current view")
            
            # Additional analysis could be added here
            # - Object detection
            # - Scene classification
            # - Text recognition (OCR)
            
            if not description_parts:
                return "I can see the camera feed but cannot determine specific details"
            
            return ". ".join(description_parts) + "."
        
        except Exception as e:
            return f"Failed to analyze scene: {str(e)}"
    
    def read_text_from_camera(self) -> str:
        """Read text visible in the camera (OCR)"""
        try:
            if not self.camera_manager.is_capturing:
                return "Camera is not active"
            
            # This would require OCR library like pytesseract
            # For now, return a placeholder
            return "Text recognition from camera not yet implemented"
        
        except Exception as e:
            return f"Failed to read text: {str(e)}"
    
    def identify_objects(self) -> list:
        """Identify objects in the current camera view"""
        try:
            if not self.camera_manager.is_capturing:
                return [{"error": "Camera is not active"}]
            
            # This would require object detection models
            # For now, return basic information
            objects = []
            
            faces = self.camera_manager.detect_faces()
            for i, face in enumerate(faces):
                objects.append({
                    "type": "person",
                    "confidence": 0.8,
                    "location": f"position {i+1}",
                    "bounds": face
                })
            
            return objects
        
        except Exception as e:
            return [{"error": f"Failed to identify objects: {str(e)}"}]

class MultimodalProcessor:
    """Processes multimodal input (voice + visual) for enhanced AI interaction"""
    
    def __init__(self, camera_manager: CameraManager):
        self.camera_manager = camera_manager
        self.visual_assistant = VisualAssistant(camera_manager)
        self.gesture_detector = GestureDetector(camera_manager)
    
    def process_multimodal_query(self, voice_query: str, include_visual: bool = True) -> str:
        """Process query that might reference visual context"""
        try:
            visual_context = ""
            
            if include_visual and self.camera_manager.is_capturing:
                # Check if query references visual elements
                visual_keywords = ["see", "look", "show", "what's", "camera", "picture", "image"]
                
                if any(keyword in voice_query.lower() for keyword in visual_keywords):
                    scene_description = self.visual_assistant.describe_scene()
                    visual_context = f"\nVisual context: {scene_description}"
            
            # Combine voice query with visual context
            enhanced_query = voice_query + visual_context
            
            return enhanced_query
        
        except Exception as e:
            return voice_query  # Return original query if enhancement fails
    
    def handle_visual_commands(self, command: str) -> str:
        """Handle commands that specifically require visual processing"""
        command_lower = command.lower()
        
        try:
            if "take picture" in command_lower or "capture image" in command_lower:
                return self.camera_manager.capture_image()
            
            elif "describe" in command_lower and ("scene" in command_lower or "what" in command_lower):
                return self.visual_assistant.describe_scene()
            
            elif "read text" in command_lower or "ocr" in command_lower:
                return self.visual_assistant.read_text_from_camera()
            
            elif "identify objects" in command_lower or "what objects" in command_lower:
                objects = self.visual_assistant.identify_objects()
                if objects and not objects[0].get('error'):
                    object_list = [f"- {obj['type']} (confidence: {obj['confidence']:.1f})" for obj in objects]
                    return f"I can see:\n" + "\n".join(object_list)
                return "No objects detected"
            
            elif "start camera" in command_lower:
                return self.camera_manager.start_camera()
            
            elif "stop camera" in command_lower:
                return self.camera_manager.stop_camera()
            
            else:
                return None  # Command not handled
        
        except Exception as e:
            return f"Failed to process visual command: {str(e)}"