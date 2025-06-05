# Sequential Analysis Workflow Manager
import logging
from typing import Dict, Any, List, Optional
import time
import sys
import traceback
sys.path.append('..')
from models.chat_models import ChatRequest, ChatResponse
from services.gemini_service import GeminiService
from services.response_service import ResponseService
from services.plot_context_service import PlotContextService
from utils.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

class SequentialWorkflowManager:
    """Manages the sequential analysis workflow with plot feedback"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.response_service = ResponseService()
        self.plot_context_service = PlotContextService()
        
    def execute_sequential_analysis(self, 
                                   request: ChatRequest, 
                                   uploaded_file_path: Optional[str] = None,
                                   session_id: str = "default",
                                   max_iterations: int = 5) -> ChatResponse:
        """
        Execute sequential analysis workflow:
        1. Initial dataset analysis
        2. Generate first visualization  
        3. Feed plot back to Gemini
        4. Generate next visualization with context
        5. Repeat until complete analysis
        """
        try:
            logger.info(f"Starting sequential analysis workflow for session {session_id}")
            
            # Step 1: Initial Analysis Request
            logger.info("Step 1: Generating initial analysis")
            initial_response = self._generate_initial_analysis(request, uploaded_file_path, session_id)
            logger.info("Initial analysis generated successfully")
            
            # Step 2: Process initial response and extract plots
            logger.info("Step 2: Processing response and extracting plots")
            processed_response = self._process_response_and_extract_plots(
                initial_response, uploaded_file_path, session_id
            )
            logger.info("Response processed successfully")
              # Step 3: Sequential plot generation with feedback
            if self._should_continue_sequential_generation(processed_response):
                logger.info("Step 3: Continuing sequential generation")
                enhanced_response = self._continue_sequential_generation(
                    request, uploaded_file_path, session_id, max_iterations
                )
                return enhanced_response
            
            return processed_response
            
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error in sequential analysis workflow: {e}")
            logger.error(f"Full traceback: {error_details}")
            return ChatResponse(
                message=f"I encountered an error during the sequential analysis. Error: {str(e)}. Please check the logs for more details.",
                metadata={'error': str(e), 'traceback': error_details, 'session_id': session_id}
            )
    
    def _generate_initial_analysis(self, 
                                 request: ChatRequest, 
                                 uploaded_file_path: Optional[str],
                                 session_id: str) -> str:
        """Generate initial dataset analysis"""
        logger.info("Generating initial dataset analysis")
        
        # Add context about sequential workflow
        enhanced_message = f"""
        {request.message}
        
        ANALYSIS WORKFLOW:
        Please provide a comprehensive dataset analysis following this structure:
        1. Dataset Overview & Quality Assessment
        2. Key Insights (5-7 specific findings)
        3. First Visualization (most important pattern)
        
        After each visualization, I will feed the generated plot back to you for context-aware next steps.
        Start with the most fundamental visualization that reveals the dataset's core patterns.
        """
        
        enhanced_request = ChatRequest(
            message=enhanced_message,
            history=request.history,
            file_path=request.file_path
        )
        
        return self.gemini_service.generate_response(
            enhanced_request, 
            uploaded_file_path
        )
    
    def _process_response_and_extract_plots(self, 
                                          response_text: str, 
                                          uploaded_file_path: Optional[str],
                                          session_id: str) -> ChatResponse:
        """Process response and extract generated plots"""
        logger.info("Processing response and extracting plots")
        
        try:
            # Process with step-by-step execution
            processed_response = self.response_service.process_gemini_response_with_step_by_step_plots(
                response_text, uploaded_file_path
            )
            
            logger.info(f"Processed response type: {type(processed_response)}")
            
            # Add generated plots to context
            if hasattr(processed_response, 'message') and isinstance(processed_response.message, dict):
                if 'content' in processed_response.message:
                    logger.info(f"Found {len(processed_response.message['content'])} content sections")
                    
                    for section_idx, section in enumerate(processed_response.message['content']):
                        logger.info(f"Section {section_idx}: type={section.get('type')}")
                        
                        if section.get('type') == 'code' and section.get('data', {}).get('figures'):
                            figures = section['data']['figures']
                            logger.info(f"Processing {len(figures)} figures from code section {section_idx}")
                            
                            for idx, figure in enumerate(figures):
                                logger.info(f"Figure {idx+1}: type={type(figure).__name__}")
                                
                                # Additional debugging - check if it's a PIL Image
                                if hasattr(figure, '_getexif') or str(type(figure)).find('PIL') != -1 or str(type(figure)).find('Image') != -1:
                                    logger.error(f"Found PIL Image in figures list! Type: {type(figure).__name__}")
                                    logger.error("This should not happen - PIL Images should not be in the figures list")
                                    continue
                                
                                # Check if figure is a dictionary (expected format)
                                if isinstance(figure, dict) and 'type' in figure and 'data' in figure:
                                    self.plot_context_service.add_plot_to_context(
                                        {
                                            'type': figure['type'],
                                            'data': figure['data'],
                                            'description': section.get('title', 'Generated visualization'),
                                            'timestamp': time.time()
                                        },
                                        session_id
                                    )
                                    logger.info(f"Successfully added figure {idx+1} to plot context")
                                else:
                                    # Handle PIL Image objects or other formats
                                    logger.warning(f"Unexpected figure format: {type(figure).__name__}. Expected dict with 'type' and 'data' keys. Skipping figure.")
                                    continue
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Error in _process_response_and_extract_plots: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Re-raise the exception so the calling method can handle it
            raise
    
    def _should_continue_sequential_generation(self, response: ChatResponse) -> bool:
        """Determine if sequential generation should continue"""
        # Check if there are plots generated and analysis is comprehensive
        if hasattr(response, 'message') and isinstance(response.message, dict):
            if 'content' in response.message:
                has_plots = any(
                    section.get('type') == 'code' and section.get('data', {}).get('figures')
                    for section in response.message['content']
                )
                return has_plots
        return False
    
    def _continue_sequential_generation(self, 
                                      original_request: ChatRequest,
                                      uploaded_file_path: Optional[str],
                                      session_id: str,
                                      max_iterations: int) -> ChatResponse:
        """Continue generating visualizations with plot context"""
        logger.info(f"Continuing sequential generation for session {session_id}")
        
        current_plots = self.plot_context_service.get_session_plots(session_id)
        iterations = 0
        
        # Continue generating until we have comprehensive analysis
        while iterations < max_iterations and len(current_plots) < 4:
            iterations += 1
            logger.info(f"Sequential iteration {iterations}")
            
            # Prepare plot context for Gemini
            plot_context = self.plot_context_service.get_context_prompt(session_id)
            gemini_plot_images = self.plot_context_service.prepare_plots_for_gemini(session_id)
            
            # Generate next analysis step with plot context
            next_request_message = f"""
            Continue the dataset analysis with the next most important visualization.
            
            {plot_context}
            
            Generate ONE new visualization that:
            1. Builds upon the previous analysis
            2. Reveals different patterns or relationships
            3. Provides additional insights
            
            Focus on: correlation analysis, distribution patterns, categorical relationships, or trend analysis.
            Provide the code for exactly ONE new plot.
            """
            
            next_request = ChatRequest(
                message=next_request_message,
                history=[],
                file_path=original_request.file_path
            )
            
            # Generate response with plot context
            next_response = self.gemini_service.generate_response(
                next_request,
                uploaded_file_path,
                plot_images=gemini_plot_images
            )
            
            # Process and add new plots to context
            self._process_response_and_extract_plots(
                next_response, uploaded_file_path, session_id
            )
            
            current_plots = self.plot_context_service.get_session_plots(session_id)
        
        # Return comprehensive response
        return self._compile_final_response(session_id, uploaded_file_path)
    
    def _compile_final_response(self, session_id: str, uploaded_file_path: Optional[str]) -> ChatResponse:
        """Compile final comprehensive response with all generated plots"""
        plots = self.plot_context_service.get_session_plots(session_id)
        
        final_message = {
            'type': 'rich_response',
            'content': [
                {
                    'type': 'text',
                    'data': f"## 📊 Complete Dataset Analysis\n\nGenerated {len(plots)} comprehensive visualizations revealing key patterns and insights."
                }
            ]
        }
        
        # Add each plot as a separate section
        for plot in plots:
            final_message['content'].append({
                'type': 'code',
                'title': f"Visualization {plot['order']}: {plot.get('description', 'Analysis')}",
                'data': {
                    'code': f"# Visualization {plot['order']}",
                    'output': '',
                    'figures': [plot]
                }
            })
        
        return ChatResponse(
            message=final_message,
            metadata={
                'session_id': session_id,
                'total_plots': len(plots),
                'workflow_type': 'sequential_analysis'
            }
        )
