# Gemini Canvas Prompt - HW3 Cosmos Text-to-Image App

This document details the instruction and prompt used to configure, develop, and refine the Cosmos3-Super-Text2Image Streamlit application.

## Development Prompt

Below is the structured prompt provided to Gemini to generate the initial prototype:

```markdown
Role: Expert AI App Developer
Goal: Build a Streamlit application that provides a beautiful, user-friendly interface for generating images using various AI models, with a primary focus on integrating Hugging Face's "nvidia/Cosmos3-Super-Text2Image" model.

Key Requirements:
1. Framework: Python and Streamlit.
2. Styling: Modern styling with curated color themes, typography, and clear grid layout.
3. Inputs:
   - Prompt text area.
   - Optional parameters: aspect ratio, image style presets, negative prompt, seed (with manual/random options), and number of images.
4. Security: 
   - No hardcoded API keys.
   - Detect tokens from streamlit secrets (`st.secrets`) and environment variables (`.env`).
   - If not found, display a text field "Enter your Hugging Face API Token" and/or "Enter your Gemini API Key".
5. Robust Fallbacks:
   - Since "nvidia/Cosmos3-Super-Text2Image" is a 64B parameter model requiring specialized serving, the serverless endpoint might return 503 (model loading) or 403 (unsupported/subscription required) on standard Hugging Face serverless accounts.
   - Include backup engines (Google Gemini 2.5 Flash and Pollinations AI Flux) to ensure the user can always generate images successfully during grading.
6. Error Handling:
   - Clear UI warnings when tokens are missing.
   - Graceful try-except handling for HTTP status codes.
   - Informative logs and alerts displaying API responses.
```

## Canvas Iterations & Implementation Notes

- **Streamlit Secrets Setup**: In local development, Streamlit reads secrets from `.streamlit/secrets.toml`. To configure this:
  ```toml
  HF_TOKEN = "your_hugging_face_token_here"
  GEMINI_API_KEY = "your_google_gemini_api_key_here"
  ```
- **Aesthetic Additions**: Streamlit custom markdown is used to insert custom CSS (such as modern fonts like Inter, custom buttons, custom hover states, and smooth shadows) to give the application a premium UI feel inspired by the original `index.html`.
