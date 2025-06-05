import re
from typing import Dict, List, Optional
import markdown

class ResponseFormatter:
    @staticmethod
    def extract_code_blocks(text: str) -> tuple[str, List[str]]:
        """Extract Python code blocks from markdown text."""
        # Pattern for Python code blocks
        pattern = r"```python\n(.*?)```"
        code_blocks = re.findall(pattern, text, re.DOTALL)
        
        # Remove code blocks from text and replace with placeholders
        cleaned_text = re.sub(pattern, "{{code_output}}", text, flags=re.DOTALL)
        
        return cleaned_text, code_blocks
    
    @staticmethod
    def format_response(
        text: str,
        code_outputs: Optional[List[Dict]] = None
    ) -> Dict:
        """Format the response with markdown and code outputs."""
        # Extract code blocks
        cleaned_text, code_blocks = ResponseFormatter.extract_code_blocks(text)
        
        # Initialize response
        response = {
            'type': 'rich_response',
            'content': [],
        }
        
        # Split text by code output placeholders
        text_parts = cleaned_text.split("{{code_output}}")
        
        # Build response sections
        for i, text_part in enumerate(text_parts):
            if text_part.strip():
                # Add text section with raw markdown
                response['content'].append({
                    'type': 'text',
                    'data': text_part.strip()
                })
            
            # Add code section if available
            if i < len(code_blocks):
                code_section = {
                    'type': 'code',
                    'data': {
                        'code': code_blocks[i],
                    }
                }
                
                # Add code output if available
                if code_outputs and i < len(code_outputs):
                    output = code_outputs[i]
                    if output.get('error'):
                        code_section['data']['error'] = output['error']
                    if output.get('output'):
                        code_section['data']['output'] = output['output']
                    if output.get('figures'):
                        code_section['data']['figures'] = output['figures']
                
                response['content'].append(code_section)
        
        return response 