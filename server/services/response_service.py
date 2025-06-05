# Response processing service for handling Gemini responses
import logging
from typing import List, Tuple
import sys
sys.path.append('..')
from models.chat_models import ChatResponse, CodeExecution
from utils.code_executor import CodeExecutor
from utils.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

class ResponseService:
    """Service for processing and formatting responses"""
    
    def __init__(self):
        self.code_executor = CodeExecutor()
        self.response_formatter = ResponseFormatter()

    def process_gemini_response(self, response_text: str, uploaded_filename: str = None) -> ChatResponse:
        """Process Gemini response, execute code blocks, and format the response"""
        try:
            # Extract code blocks and clean text
            cleaned_text, code_blocks = ResponseFormatter.extract_code_blocks(response_text)
            
            # Execute code blocks if any
            code_executions = []
            code_outputs = []
            if code_blocks:
                executions = []
                for code_block in code_blocks:
                    exec_result = self.code_executor.execute(code_block, uploaded_filename)
                    executions.append(exec_result)
                    code_outputs.append({
                        'output': exec_result.get('output', ''),
                        'error': exec_result.get('error', ''),
                        'figures': exec_result.get('figures', [])
                    })
                code_executions = [self._convert_to_code_execution(exec_result) for exec_result in executions]
            
            # Format as rich response
            formatted_response = ResponseFormatter.format_response(response_text, code_outputs)
            
            return ChatResponse(
                message=formatted_response,
                code_executions=code_executions,
                metadata={'original_response_length': len(response_text)}
            )
            
        except Exception as e:
            logger.error(f"Error processing Gemini response: {e}")
            # Return error response
            return ChatResponse(
                message="I apologize, but I encountered an error processing the response. Please try again.",
                metadata={'error': str(e)}
            )
    
    def _convert_to_code_execution(self, exec_result: dict) -> CodeExecution:
        """Convert execution result dict to CodeExecution model"""
        return CodeExecution(
            code=exec_result.get('code', ''),            output=exec_result.get('output'),
            error=exec_result.get('error'),
            execution_time=exec_result.get('execution_time'),
            plots=exec_result.get('plots', [])
        )
    
    def process_gemini_response_with_step_by_step_plots(self, response_text: str, uploaded_filename: str = None) -> ChatResponse:
        """Process Gemini response with step-by-step plot generation and detailed logging"""
        try:
            logger.info("Starting step-by-step plot processing")
            
            # Extract code blocks and clean text
            cleaned_text, code_blocks = ResponseFormatter.extract_code_blocks(response_text)
            logger.info(f"Extracted {len(code_blocks)} code blocks from response")
            
            # Execute code blocks one by one
            code_executions = []
            code_outputs = []
            executions = []
            
            if code_blocks:
                for i, code_block in enumerate(code_blocks):
                    logger.info(f"Processing code block {i+1}/{len(code_blocks)}")
                    logger.info(f"Code preview: {code_block[:100]}...")
                    
                    # Execute the code block
                    exec_result = self.code_executor.execute(code_block, uploaded_filename)
                    
                    # Log execution results
                    if exec_result.get('error'):
                        logger.warning(f"Code block {i+1} had error: {exec_result['error']}")
                    else:
                        logger.info(f"Code block {i+1} executed successfully")
                    
                    if exec_result.get('figures'):
                        logger.info(f"Code block {i+1} generated {len(exec_result['figures'])} figures")
                        for j, figure in enumerate(exec_result['figures']):
                            logger.info(f"  Figure {j+1}: type={figure.get('type')}")
                    
                    # Store results
                    executions.append(exec_result)
                    code_outputs.append({
                        'output': exec_result.get('output', ''),
                        'error': exec_result.get('error', ''),
                        'figures': exec_result.get('figures', [])
                    })
                
                code_executions = [self._convert_to_code_execution(exec_result) for exec_result in executions]
            
            # Format as rich response
            formatted_response = ResponseFormatter.format_response(response_text, code_outputs)
            logger.info("Successfully formatted response with plots")
            
            return ChatResponse(
                message=formatted_response,
                code_executions=code_executions,
                metadata={
                    'original_response_length': len(response_text),
                    'code_blocks_count': len(code_blocks),
                    'total_figures_generated': sum(len(output.get('figures', [])) for output in code_outputs)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in step-by-step plot processing: {e}")
            # Return error response
            return ChatResponse(
                message="I apologize, but I encountered an error processing the plots. Please try again.",
                metadata={'error': str(e)}
            )
