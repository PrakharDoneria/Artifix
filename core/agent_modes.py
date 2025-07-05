import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

@dataclass
class AgentPersonality:
    """Defines an agent personality/mode"""
    name: str
    description: str
    personality_traits: List[str]
    response_style: str
    expertise_areas: List[str]
    default_actions: List[str]
    system_prompt: str
    voice_settings: Dict[str, Any]
    ui_theme: Dict[str, str]
    active: bool = False

class AgentModes:
    """Manages different agent personalities and modes"""
    
    def __init__(self, config_path: str = "config/agent_modes.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.modes: Dict[str, AgentPersonality] = {}
        self.current_mode = None
        self.load_modes()
        self.init_default_modes()
    
    def init_default_modes(self):
        """Initialize default agent modes"""
        default_modes = [
            AgentPersonality(
                name="Professional",
                description="Formal, business-oriented assistant focused on productivity",
                personality_traits=["formal", "efficient", "detail-oriented", "professional"],
                response_style="concise and formal",
                expertise_areas=["business", "productivity", "scheduling", "communication"],
                default_actions=["check_calendar", "manage_tasks", "send_emails"],
                system_prompt="You are a professional AI assistant. Respond formally and focus on productivity and efficiency. Keep responses concise and business-appropriate.",
                voice_settings={"rate": 175, "volume": 0.8, "voice": "professional"},
                ui_theme={"primary": "#1f2937", "secondary": "#374151", "accent": "#3b82f6"}
            ),
            AgentPersonality(
                name="Casual",
                description="Friendly, conversational assistant for daily interactions",
                personality_traits=["friendly", "casual", "helpful", "conversational"],
                response_style="warm and conversational",
                expertise_areas=["general_knowledge", "entertainment", "casual_chat"],
                default_actions=["chat", "provide_information", "suggest_activities"],
                system_prompt="You are a friendly and casual AI assistant. Be warm, conversational, and helpful. Use a relaxed tone and feel free to be personable in your responses.",
                voice_settings={"rate": 160, "volume": 0.9, "voice": "friendly"},
                ui_theme={"primary": "#10b981", "secondary": "#059669", "accent": "#34d399"}
            ),
            AgentPersonality(
                name="Technical",
                description="Developer-focused assistant with deep technical knowledge",
                personality_traits=["analytical", "precise", "knowledgeable", "problem-solving"],
                response_style="technical and detailed",
                expertise_areas=["programming", "debugging", "system_administration", "development_tools"],
                default_actions=["code_analysis", "debug_assistance", "git_operations", "run_tests"],
                system_prompt="You are a technical AI assistant specialized in software development. Provide detailed, accurate technical information. Focus on code quality, best practices, and problem-solving.",
                voice_settings={"rate": 170, "volume": 0.7, "voice": "neutral"},
                ui_theme={"primary": "#1e293b", "secondary": "#334155", "accent": "#0ea5e9"}
            ),
            AgentPersonality(
                name="Creative",
                description="Imaginative assistant for creative projects and brainstorming",
                personality_traits=["creative", "imaginative", "inspiring", "artistic"],
                response_style="inspiring and creative",
                expertise_areas=["writing", "design", "brainstorming", "creative_projects"],
                default_actions=["brainstorm_ideas", "creative_writing", "design_suggestions"],
                system_prompt="You are a creative AI assistant. Be imaginative, inspiring, and help users explore creative possibilities. Encourage innovation and artistic expression.",
                voice_settings={"rate": 155, "volume": 0.85, "voice": "expressive"},
                ui_theme={"primary": "#7c3aed", "secondary": "#8b5cf6", "accent": "#a78bfa"}
            ),
            AgentPersonality(
                name="Research",
                description="Academic and research-focused assistant for deep analysis",
                personality_traits=["analytical", "thorough", "scholarly", "methodical"],
                response_style="detailed and academic",
                expertise_areas=["research", "analysis", "fact_checking", "academic_writing"],
                default_actions=["research_topics", "fact_verification", "data_analysis"],
                system_prompt="You are a research-focused AI assistant. Provide thorough, well-researched responses with citations when possible. Be methodical and analytical in your approach.",
                voice_settings={"rate": 165, "volume": 0.8, "voice": "scholarly"},
                ui_theme={"primary": "#dc2626", "secondary": "#ef4444", "accent": "#f87171"}
            ),
            AgentPersonality(
                name="Personal",
                description="Intimate, personalized assistant that learns your preferences",
                personality_traits=["empathetic", "personal", "adaptive", "caring"],
                response_style="personal and empathetic",
                expertise_areas=["personal_assistance", "wellness", "lifestyle", "relationships"],
                default_actions=["personal_reminders", "mood_tracking", "lifestyle_suggestions"],
                system_prompt="You are a personal AI assistant who knows the user well. Be empathetic, personal, and adaptive to their needs. Remember their preferences and provide caring, personalized assistance.",
                voice_settings={"rate": 150, "volume": 0.9, "voice": "warm"},
                ui_theme={"primary": "#f59e0b", "secondary": "#f97316", "accent": "#fb923c"}
            ),
            AgentPersonality(
                name="Gaming",
                description="Gaming-focused assistant for gamers and game development",
                personality_traits=["enthusiastic", "competitive", "knowledgeable", "fun"],
                response_style="enthusiastic and gaming-oriented",
                expertise_areas=["gaming", "game_development", "esports", "streaming"],
                default_actions=["game_recommendations", "gaming_stats", "streaming_assistance"],
                system_prompt="You are a gaming-focused AI assistant. Be enthusiastic about games, knowledgeable about gaming culture, and help with gaming-related tasks. Use gaming terminology appropriately.",
                voice_settings={"rate": 180, "volume": 0.9, "voice": "energetic"},
                ui_theme={"primary": "#8b5cf6", "secondary": "#a78bfa", "accent": "#c4b5fd"}
            )
        ]
        
        # Add default modes if they don't exist
        for mode in default_modes:
            if mode.name not in self.modes:
                self.modes[mode.name] = mode
        
        # Set Professional as default if no mode is active
        if not self.current_mode and "Professional" in self.modes:
            self.set_active_mode("Professional")
        
        self.save_modes()
    
    def load_modes(self):
        """Load agent modes from configuration file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.modes = {}
                    for mode_data in data.get('modes', []):
                        personality = AgentPersonality(**mode_data)
                        self.modes[personality.name] = personality
                    
                    self.current_mode = data.get('current_mode')
        except Exception as e:
            print(f"Failed to load agent modes: {e}")
            self.modes = {}
    
    def save_modes(self):
        """Save agent modes to configuration file"""
        try:
            data = {
                'modes': [asdict(mode) for mode in self.modes.values()],
                'current_mode': self.current_mode,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save agent modes: {e}")
    
    def add_mode(self, personality: AgentPersonality) -> str:
        """Add a new agent mode"""
        try:
            self.modes[personality.name] = personality
            self.save_modes()
            return f"Added agent mode: {personality.name}"
        except Exception as e:
            return f"Failed to add mode: {str(e)}"
    
    def remove_mode(self, mode_name: str) -> str:
        """Remove an agent mode"""
        try:
            if mode_name not in self.modes:
                return f"Mode '{mode_name}' not found"
            
            if self.current_mode == mode_name:
                # Switch to Professional mode if removing current mode
                self.set_active_mode("Professional")
            
            del self.modes[mode_name]
            self.save_modes()
            return f"Removed agent mode: {mode_name}"
        except Exception as e:
            return f"Failed to remove mode: {str(e)}"
    
    def get_modes(self) -> List[Dict[str, Any]]:
        """Get list of all available modes"""
        return [
            {
                "name": mode.name,
                "description": mode.description,
                "active": mode.name == self.current_mode,
                "personality_traits": mode.personality_traits,
                "expertise_areas": mode.expertise_areas
            }
            for mode in self.modes.values()
        ]
    
    def get_current_mode(self) -> Optional[AgentPersonality]:
        """Get the currently active mode"""
        if self.current_mode and self.current_mode in self.modes:
            return self.modes[self.current_mode]
        return None
    
    def set_active_mode(self, mode_name: str) -> str:
        """Set the active agent mode"""
        try:
            if mode_name not in self.modes:
                return f"Mode '{mode_name}' not found"
            
            # Deactivate previous mode
            if self.current_mode and self.current_mode in self.modes:
                self.modes[self.current_mode].active = False
            
            # Activate new mode
            self.current_mode = mode_name
            self.modes[mode_name].active = True
            self.save_modes()
            
            return f"Switched to {mode_name} mode"
        except Exception as e:
            return f"Failed to switch mode: {str(e)}"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for current mode"""
        current = self.get_current_mode()
        return current.system_prompt if current else "You are a helpful AI assistant."
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice settings for current mode"""
        current = self.get_current_mode()
        return current.voice_settings if current else {"rate": 160, "volume": 0.8}
    
    def get_ui_theme(self) -> Dict[str, str]:
        """Get UI theme for current mode"""
        current = self.get_current_mode()
        return current.ui_theme if current else {"primary": "#1f2937", "secondary": "#374151", "accent": "#3b82f6"}
    
    def get_default_actions(self) -> List[str]:
        """Get default actions for current mode"""
        current = self.get_current_mode()
        return current.default_actions if current else ["chat", "provide_information"]
    
    def update_mode(self, mode_name: str, **updates) -> str:
        """Update an existing mode"""
        try:
            if mode_name not in self.modes:
                return f"Mode '{mode_name}' not found"
            
            mode = self.modes[mode_name]
            
            # Update allowed fields
            for field, value in updates.items():
                if hasattr(mode, field):
                    setattr(mode, field, value)
            
            self.save_modes()
            return f"Updated mode: {mode_name}"
        except Exception as e:
            return f"Failed to update mode: {str(e)}"
    
    def create_custom_mode(self, name: str, description: str, base_mode: str = "Professional") -> str:
        """Create a custom mode based on an existing mode"""
        try:
            if base_mode not in self.modes:
                return f"Base mode '{base_mode}' not found"
            
            if name in self.modes:
                return f"Mode '{name}' already exists"
            
            # Copy base mode
            base = self.modes[base_mode]
            custom_mode = AgentPersonality(
                name=name,
                description=description,
                personality_traits=base.personality_traits.copy(),
                response_style=base.response_style,
                expertise_areas=base.expertise_areas.copy(),
                default_actions=base.default_actions.copy(),
                system_prompt=base.system_prompt,
                voice_settings=base.voice_settings.copy(),
                ui_theme=base.ui_theme.copy(),
                active=False
            )
            
            self.modes[name] = custom_mode
            self.save_modes()
            
            return f"Created custom mode '{name}' based on '{base_mode}'"
        except Exception as e:
            return f"Failed to create custom mode: {str(e)}"
    
    def get_mode_suggestions(self, context: str) -> List[str]:
        """Suggest appropriate modes based on context"""
        context_lower = context.lower()
        suggestions = []
        
        # Keyword-based suggestions
        mode_keywords = {
            "Professional": ["work", "business", "meeting", "email", "formal", "office"],
            "Technical": ["code", "programming", "debug", "error", "development", "git"],
            "Creative": ["design", "art", "creative", "brainstorm", "write", "idea"],
            "Research": ["research", "analyze", "study", "academic", "paper", "data"],
            "Gaming": ["game", "gaming", "play", "stream", "esports", "gaming"],
            "Personal": ["personal", "mood", "feeling", "wellness", "life", "relationship"]
        }
        
        for mode_name, keywords in mode_keywords.items():
            if mode_name in self.modes:
                for keyword in keywords:
                    if keyword in context_lower:
                        if mode_name not in suggestions:
                            suggestions.append(mode_name)
                        break
        
        # If no specific suggestions, recommend current mode
        if not suggestions and self.current_mode:
            suggestions.append(self.current_mode)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_mode_analytics(self) -> Dict[str, Any]:
        """Get analytics about mode usage (placeholder for future implementation)"""
        return {
            "total_modes": len(self.modes),
            "current_mode": self.current_mode,
            "available_modes": list(self.modes.keys()),
            "last_updated": datetime.now().isoformat()
        }

class ModeBasedResponseGenerator:
    """Generates responses based on current agent mode"""
    
    def __init__(self, agent_modes: AgentModes):
        self.agent_modes = agent_modes
    
    def generate_response(self, user_input: str, base_response: str) -> str:
        """Modify response based on current mode"""
        current_mode = self.agent_modes.get_current_mode()
        if not current_mode:
            return base_response
        
        # Apply personality traits to response
        if "formal" in current_mode.personality_traits:
            return self._formalize_response(base_response)
        elif "casual" in current_mode.personality_traits:
            return self._casualize_response(base_response)
        elif "technical" in current_mode.personality_traits:
            return self._technicalize_response(base_response)
        elif "creative" in current_mode.personality_traits:
            return self._creativize_response(base_response)
        
        return base_response
    
    def _formalize_response(self, response: str) -> str:
        """Make response more formal"""
        # Simple formalization logic
        formal_phrases = {
            "yeah": "yes",
            "ok": "very well",
            "sure": "certainly",
            "nope": "no",
            "gonna": "going to",
            "wanna": "want to"
        }
        
        for informal, formal in formal_phrases.items():
            response = response.replace(informal, formal)
        
        return response
    
    def _casualize_response(self, response: str) -> str:
        """Make response more casual"""
        # Add casual elements
        if not response.endswith(('!', '?', '.')):
            response += "!"
        
        return response
    
    def _technicalize_response(self, response: str) -> str:
        """Make response more technical"""
        # Add technical precision
        return response
    
    def _creativize_response(self, response: str) -> str:
        """Make response more creative"""
        # Add creative flair
        return response