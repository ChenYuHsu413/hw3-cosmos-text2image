# HW3 Cosmos3-Super-Text2Image App

## Project Goal

This project uses Streamlit and Hugging Face to build a text-to-image generation app with NVIDIA Cosmos3-Super-Text2Image. It offers a beautiful, modern web-based workspace to let users input custom creative prompts, set aspect ratios, define artistic styles, apply negative prompts, customize seeds, and generate multiple images simultaneously. 

To ensure stability and ease of testing, the application supports four powerful AI backends:
1. **NVIDIA Cosmos3-Super-Text2Image** (via Hugging Face API)
2. **Google Gemini 2.5 Flash Image** (via Google AI Studio)
3. **Puter.js (Stable Diffusion)** (completely free, browser-side rendering, no API key required)
4. **Pollinations AI Flux** (completely free, no API key required fallback)


---

## Model

Model: [nvidia/Cosmos3-Super-Text2Image](https://huggingface.co/nvidia/Cosmos3-Super-Text2Image)

---

## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/ChenYuHsu413/hw3-cosmos-text2image.git
cd hw3-cosmos-text2image
```

### 2. Install dependencies
Ensure you have Python 3.8+ installed. Run:
```bash
pip install -r requirements.txt
```

### 3. Setup API Keys (Optional but Recommended)
You can configure your Hugging Face Access Token and Google Gemini API Key in two ways:

#### Option A: Local `.env` file
Create a file named `.env` in the root of the project:
```env
HF_TOKEN=your_hugging_face_access_token
GEMINI_API_KEY=your_gemini_api_key
```

#### Option B: Streamlit Secrets
Create a file named `.streamlit/secrets.toml`:
```toml
HF_TOKEN = "your_hugging_face_access_token"
GEMINI_API_KEY = "your_gemini_api_key"
```

#### Option C: In-App Input
If no keys are found in `.env` or secrets, the app will automatically display input fields for you to securely paste your tokens.

### 4. Run the application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## How to Deploy to Streamlit.io

Streamlit Community Cloud is the easiest way to deploy and share your app:
1. Push this project to your GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **"New app"** and select your repository, branch (`main`), and main file path (`app.py`).
4. Click **"Advanced settings"** and add your secrets to the Secrets text area:
   ```toml
   HF_TOKEN = "your_hugging_face_access_token"
   GEMINI_API_KEY = "your_gemini_api_key"
   ```
5. Click **"Deploy!"** Your app will be live in a few minutes.

---

## Links

- **GitHub Repository**: [https://github.com/ChenYuHsu413/hw3-cosmos-text2image](https://github.com/ChenYuHsu413/hw3-cosmos-text2image)
- **Live Streamlit Demo**: [https://hw3-cosmos-text2image.streamlit.app](https://hw3-cosmos-text2image.streamlit.app) *(Please update this link after deployment)*

---

## Screenshots

Below is the directory structure for project screenshots.

- **App Home Screen**: `screenshots/app_home.png`
- **Generated Result**: `screenshots/generated_result.png`
