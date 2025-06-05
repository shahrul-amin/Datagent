import google.generativeai as genai
import os

class GeminiModelFactory:
    @staticmethod
    def create_model(model_name: str = 'gemini-2.0-flash'):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        return genai.GenerativeModel(model_name)

    @staticmethod
    def generate_content_with_retry(model, content, generation_config, max_retries: int = 3):
        for attempt in range(max_retries + 1):
            try:
                return model.generate_content(content, generation_config=generation_config)
            except AttributeError as e:
                if 'DESCRIPTOR' in str(e) and attempt < max_retries:
                    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                    model = GeminiModelFactory.create_model()
                    continue
                else:
                    raise
            except Exception as e:
                raise
        raise RuntimeError("Failed to generate content after all retries")

    @staticmethod
    def generate_content_stream_with_retry(model, content, generation_config, max_retries: int = 3):
        for attempt in range(max_retries + 1):
            try:
                return model.generate_content(content, generation_config=generation_config, stream=True)
            except AttributeError as e:
                if 'DESCRIPTOR' in str(e) and attempt < max_retries:
                    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                    model = GeminiModelFactory.create_model()
                    continue
                else:
                    raise
            except Exception as e:
                raise
        raise RuntimeError("Failed to generate streaming content after all retries")
