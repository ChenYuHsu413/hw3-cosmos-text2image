# HW3 Cosmos3-Super-Text2Image App

## Project Goal

This project uses Streamlit and Hugging Face to build a text-to-image generation app with NVIDIA Cosmos3-Super-Text2Image. It offers a beautiful, modern web-based workspace to let users input custom creative prompts, set aspect ratios, define artistic styles, apply negative prompts, customize seeds, and generate multiple images simultaneously. 

To ensure stability and ease of testing, the application supports four powerful AI backends:
1. **NVIDIA Cosmos3-Super-Text2Image** (via Hugging Face API)
2. **Google Gemini 2.5 Flash Image** (via Google AI Studio)
3. **Puter.js (Stable Diffusion)** (completely free, browser-side rendering, no API key required)
4. **Pollinations AI Flux** (completely free, no API key required fallback)


---

## Model & Engines

### NVIDIA Cosmos3-Super-Text2Image
Model: [nvidia/Cosmos3-Super-Text2Image](https://huggingface.co/nvidia/Cosmos3-Super-Text2Image)

### Puter.js (推薦展示使用)
由於絕大部分的免費 API (如 Hugging Face Serverless 等) 經常流量過載或無法成功產圖，本專案特別加入了 **Puter.js (Stable Diffusion)** 選項，以方便進行作業功能的完整展示。
* **使用說明**：在瀏覽器中首次使用 Puter.js 進行生圖時，會彈出 Puter 的登入視窗，此時需要按照提示使用 Google 帳號登入 Puter 帳戶，即可取得免費生圖額度並成功產圖。

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
- **Live Streamlit Demo**: [https://chenyu-hw3-cosmos-text2image.streamlit.app/](https://chenyu-hw3-cosmos-text2image.streamlit.app/)

---

## Screenshots

以下為本專案的應用程式畫面截圖：

- **App Home Screen (手機版首頁)**:
  
  ![App Home 1](screenshots/IMG_6598.PNG)
  
  ![App Home 2](screenshots/IMG_6599.PNG)

- **Generated Result (生成結果)**:
  
  ![Generated Result](screenshots/IMG_6597.PNG)

- **Desktop Preview (電腦版預覽)**:
  
  ![Desktop Preview](screenshots/2026-06-04%20201852.png)


