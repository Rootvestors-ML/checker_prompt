import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = input('AIzaSyAke6WuR9N-sn9zsCznMVlYw6h-kssjGbI')
genai.configure(api_key=GOOGLE_API_KEY)

print("Available models for your API key:")
for model in genai.list_models():
    print(f"- {model.name} (Supported methods: {model.supported_generation_methods})")
