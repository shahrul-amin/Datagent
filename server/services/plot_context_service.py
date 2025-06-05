# Plot Context Manager Service
import logging
import base64
import os
import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
import io

logger = logging.getLogger(__name__)

class PlotContextService:
    """Service for managing plot context and feeding images back to Gemini"""
    
    def __init__(self):
        self.plot_history = []
        self.context_images = []
        self.session_plots = {}
    
    def add_plot_to_context(self, plot_data: Dict[str, Any], session_id: str = "default") -> None:
        """Add a generated plot to the context for future requests"""
        try:
            if session_id not in self.session_plots:
                self.session_plots[session_id] = []
            
            # Validate plot_data structure
            if not isinstance(plot_data, dict):
                logger.error(f"plot_data must be a dictionary, got {type(plot_data)}")
                return
                
            # Store plot metadata with safe access
            plot_context = {
                'type': plot_data.get('type', 'unknown'),
                'data': plot_data.get('data', ''),
                'description': plot_data.get('description', ''),
                'timestamp': plot_data.get('timestamp', time.time()),
                'order': len(self.session_plots[session_id]) + 1
            }
            
            self.session_plots[session_id].append(plot_context)
            logger.info(f"Added plot {plot_context['order']} to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error adding plot to context: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    def get_session_plots(self, session_id: str = "default") -> List[Dict[str, Any]]:
        """Get all plots for a session"""
        return self.session_plots.get(session_id, [])
    
    def prepare_plots_for_gemini(self, session_id: str = "default", limit: int = 5) -> List[Any]:
        """Prepare plots as Gemini-compatible image objects"""
        gemini_images = []
        
        try:
            plots = self.get_session_plots(session_id)
            recent_plots = plots[-limit:] if len(plots) > limit else plots
            
            for plot in recent_plots:
                if plot['type'] == 'matplotlib':
                    # Convert base64 to PIL Image for Gemini
                    img_data = base64.b64decode(plot['data'])
                    img = Image.open(io.BytesIO(img_data))
                    gemini_images.append(img)
                    logger.info(f"Prepared matplotlib plot {plot['order']} for Gemini")
                    
        except Exception as e:
            logger.error(f"Error preparing plots for Gemini: {e}")
            
        return gemini_images
    
    def create_plot_summary(self, session_id: str = "default") -> str:
        """Create a text summary of generated plots for context"""
        plots = self.get_session_plots(session_id)
        
        if not plots:
            return "No plots generated yet."
            
        summary = f"Generated Plots Summary ({len(plots)} plots):\n"
        for plot in plots:
            summary += f"- Plot {plot['order']}: {plot.get('description', 'Visualization')}\n"
            
        return summary
    
    def clear_session_context(self, session_id: str = "default") -> None:
        """Clear plot context for a session"""
        if session_id in self.session_plots:
            del self.session_plots[session_id]
            logger.info(f"Cleared plot context for session {session_id}")
    
    def get_context_prompt(self, session_id: str = "default") -> str:
        """Generate context prompt with plot history"""
        plots = self.get_session_plots(session_id)
        
        if not plots:
            return ""
            
        context = "\n\nPREVIOUS PLOTS CONTEXT:\n"
        context += f"You have already generated {len(plots)} visualizations:\n"
        
        for plot in plots:
            context += f"- Plot {plot['order']}: {plot.get('description', 'Visualization')}\n"
            
        context += "\nBuild upon these visualizations for the next analysis step.\n"
        context += "Reference the previous plots when generating new insights.\n"
        
        return context
