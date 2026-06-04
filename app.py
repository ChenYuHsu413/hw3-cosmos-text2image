import os
import io
import time
import base64
import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

# Load local .env file if present
load_dotenv()

# Initialize session state variables for generation
if "generation_trigger" not in st.session_state:
    st.session_state["generation_trigger"] = False
if "active_engine" not in st.session_state:
    st.session_state["active_engine"] = None
if "prompt_state" not in st.session_state:
    st.session_state["prompt_state"] = ""
if "style_desc_state" not in st.session_state:
    st.session_state["style_desc_state"] = ""
if "style_choice_state" not in st.session_state:
    st.session_state["style_choice_state"] = ""
if "dims_state" not in st.session_state:
    st.session_state["dims_state"] = (1024, 1024)
if "seed_state" not in st.session_state:
    st.session_state["seed_state"] = 42
if "num_images_state" not in st.session_state:
    st.session_state["num_images_state"] = 1
if "hf_token_state" not in st.session_state:
    st.session_state["hf_token_state"] = None
if "gemini_key_state" not in st.session_state:
    st.session_state["gemini_key_state"] = None
if "is_random_seed_state" not in st.session_state:
    st.session_state["is_random_seed_state"] = True
if "negative_prompt_state" not in st.session_state:
    st.session_state["negative_prompt_state"] = ""


# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="AI Image Studio - Multi-Engine Edition",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Tailwind-like color scheme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Font Settings */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Microsoft JhengHei', sans-serif;
    }
    
    /* Header Gradient styling */
    .title-container {
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .main-title {
        font-size: 2.25rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .badge {
        display: inline-block;
        padding: 0.18rem 0.5rem;
        font-size: 0.7rem;
        font-weight: 600;
        color: #4f46e5;
        background-color: #e0e7ff;
        border: 1px solid #c7d2fe;
        border-radius: 9999px;
        margin-left: 0.5rem;
        vertical-align: middle;
    }
    
    /* Custom Card container for UI elements */
    .card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    /* Grid background effect for the output canvas */
    .grid-bg-container {
        background-color: #f1f5f9;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0.04) 1px, transparent 1px),
                          linear-gradient(to bottom, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
        background-size: 20px 20px;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 480px;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .title-container {
            border-bottom: 1px solid #334155;
        }
        .card {
            background-color: #1e293b;
            border-color: #334155;
        }
        .grid-bg-container {
            background-color: #0f172a;
            background-image: linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                              linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            border-color: #475569;
        }
        .badge {
            color: #818cf8;
            background-color: #1e1b4b;
            border-color: #312e81;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS (API INGESTION)
# ==========================================

def get_api_token(secret_key, env_key):
    """Retrieve API keys from Streamlit secrets, environment variables, or local state."""
    # 1. Try Streamlit secrets (handling StreamlitSecretNotFoundError safely)
    try:
        if secret_key in st.secrets:
            return st.secrets[secret_key]
    except Exception:
        pass
    
    # 2. Try Environment variables (loaded via python-dotenv)
    token = os.getenv(env_key)
    if token:
        return token
    
    # 3. Check if stored in Streamlit session state
    session_state_key = f"key_{env_key.lower()}"
    if session_state_key in st.session_state:
        return st.session_state[session_state_key]
    
    return None


def generate_huggingface_image(prompt, negative_prompt, style_desc, aspect_ratio_dims, seed, token):
    """Call Hugging Face Inference API for nvidia/Cosmos3-Super-Text2Image."""
    API_URL = "https://api-inference.huggingface.co/models/nvidia/Cosmos3-Super-Text2Image"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Formulate prompt including image style
    final_prompt = prompt
    if style_desc:
        final_prompt = f"{prompt}, {style_desc}"
        
    width, height = aspect_ratio_dims
    
    # Prepare payload
    payload = {
        "inputs": final_prompt,
        "parameters": {
            "negative_prompt": negative_prompt if negative_prompt else "blurry, low quality, distorted",
            "width": width,
            "height": height
        }
    }
    
    # Add seed if specified
    if seed is not None:
        payload["parameters"]["seed"] = int(seed)
        
    response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
    
    # Handle response status codes
    if response.status_code == 200:
        try:
            image = Image.open(io.BytesIO(response.content))
            return image
        except Exception as e:
            raise RuntimeError(f"Failed to decode image data from Hugging Face: {e}")
    elif response.status_code == 503:
        # 503 indicates model is loading
        try:
            err_json = response.json()
            estimated_time = err_json.get("estimated_time", 20.0)
            raise RuntimeError(
                f"Model is loading. Please wait approximately {estimated_time:.1f} seconds "
                "and try generating again. (HTTP 503)"
            )
        except ValueError:
            raise RuntimeError("Model is loading on Hugging Face servers. Please try again shortly. (HTTP 503)")
    else:
        # Generic errors
        try:
            err_json = response.json()
            err_msg = err_json.get("error", f"Unknown Hugging Face API error: {response.text}")
        except Exception:
            err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
        raise RuntimeError(f"Hugging Face API Error: {err_msg}")

def generate_gemini_image(prompt, style_desc, token):
    """Call Gemini 2.5 Flash Image Preview API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={token}"
    
    # Formulate final prompt
    final_prompt = prompt
    if style_desc:
        final_prompt = f"{prompt}, {style_desc}"
        
    payload = {
        "contents": [{
            "parts": [{"text": final_prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        try:
            data = response.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            image_part = next((p for p in parts if "inlineData" in p), None)
            
            if not image_part or "inlineData" not in image_part:
                raise RuntimeError("API response succeeded, but did not return image data.")
                
            base64_data = image_part["inlineData"]["data"]
            mime_type = image_part["inlineData"].get("mimeType", "image/png")
            
            image_bytes = base64.b64decode(base64_data)
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            raise RuntimeError(f"Failed to parse Gemini API response: {e}")
    else:
        try:
            err_json = response.json()
            err_msg = err_json.get("error", {}).get("message", f"HTTP {response.status_code}")
        except Exception:
            err_msg = f"HTTP {response.status_code}: {response.text}"
        raise RuntimeError(f"Google Gemini API Error: {err_msg}")

def generate_pollinations_image(prompt, style_desc, aspect_ratio_dims, seed):
    """Fetch image from Pollinations AI (Flux Model - completely free fallback)."""
    # Formulate prompt
    final_prompt = prompt
    if style_desc:
        final_prompt = f"{prompt}, {style_desc}"
        
    width, height = aspect_ratio_dims
    
    # Encode prompt for safe URL transmission
    import urllib.parse
    encoded_prompt = urllib.parse.quote(final_prompt)
    
    url = f"https://image.pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={seed}&model=flux&nologo=true"
    
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        try:
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            raise RuntimeError(f"Failed to parse image from Pollinations: {e}")
    else:
        raise RuntimeError(f"Pollinations AI failed (HTTP {response.status_code})")

# ==========================================
# APP LAYOUT & USER INTERFACE
# ==========================================

# Modern Page Title Banner
st.markdown("""
<div class="title-container">
    <h1 class="main-title">AI 生圖工作室 <span class="badge">旗艦多引擎版</span></h1>
    <p style="color: #64748b; margin-top: 0.25rem; font-size: 0.9rem;">
        整合 NVIDIA Cosmos 3.0 / Gemini / Flux，支援極速出圖與多模型切換，最適合交作業與創意開發。
    </p>
</div>
""", unsafe_allow_html=True)

# Main Grid Layout (Left Config Panel: 5 columns, Right Preview Canvas: 7 columns)
col_left, col_right = st.columns([5, 7], gap="large")

# ----------------- LEFT PANEL: CONFIG -----------------
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔮 1. 選擇生圖引擎 (Engine)")
    
    engine_choice = st.radio(
        label="選擇欲使用的後端 AI 模型：",
        options=[
            "nvidia/Cosmos3-Super-Text2Image (Hugging Face)",
            "Gemini 2.5 Flash Image (Google API)",
            "Puter.js (Stable Diffusion - 完全免金鑰)",
            "Pollinations AI (Flux - 完全免金鑰)"
        ],
        index=2,  # Default to Puter.js as suggested by the user
        label_visibility="collapsed"
    )
    
    # Dynamic Token Inputs based on selected engine
    hf_token = None
    gemini_key = None
    
    if "Cosmos3" in engine_choice:
        hf_token = get_api_token("HF_TOKEN", "HF_TOKEN")
        if not hf_token:
            st.info("💡 提示：未在 Streamlit secrets 或 .env 中檢測到金鑰。請於下方手動輸入。")
            user_token = st.text_input(
                "Enter your Hugging Face API Token:",
                type="password",
                placeholder="hf_...",
                help="取得方式：登入 Hugging Face -> Settings -> Access Tokens"
            )
            if user_token:
                st.session_state["key_hf_token"] = user_token.strip()
                hf_token = user_token.strip()
        else:
            st.success("✅ 已自動載入 Hugging Face API 金鑰")
            
    elif "Gemini" in engine_choice:
        gemini_key = get_api_token("GEMINI_API_KEY", "GEMINI_API_KEY")
        if not gemini_key:
            st.info("💡 提示：未在 Streamlit secrets 或 .env 中檢測到金鑰。請於下方手動輸入。")
            user_key = st.text_input(
                "Enter your Gemini API Key:",
                type="password",
                placeholder="AIzaSy...",
                help="取得方式：前往 Google AI Studio 申請免費的 API 金鑰"
            )
            if user_key:
                st.session_state["key_gemini_api_key"] = user_key.strip()
                gemini_key = user_key.strip()
        else:
            st.success("✅ 已自動載入 Gemini API 金鑰")
            
    elif "Puter.js" in engine_choice:
        st.success("🎈 Puter.js 為瀏覽器免金鑰引擎，直接由您的瀏覽器進行生圖，100% 穩定且不需金鑰！")
    else:
        st.success("🎈 Pollinations AI 為免金鑰引擎，可直接點擊按鈕生圖！")
        
    st.markdown('</div>', unsafe_allow_html=True)

    
    # Prompt Input Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 2. 輸入創意提示詞 (Prompt)")
    
    # Preset Quick Prompts
    quick_prompt = st.selectbox(
        "快速套用範本：",
        options=[
            "自行輸入...",
            "賽博朋克 (Cyberpunk street, neon signs, wet asphalt, highly detailed, photorealistic)",
            "日系水彩 (A beautiful Japanese garden with cherry blossoms, traditional temple in the background, anime watercolor style)",
            "可愛 3D (A cute chubby hamster wearing an astronaut helmet on the moon, holding a cheese, 3d render, clay style)"
        ]
    )
    
    # Pre-fill prompt text area if a preset is selected
    default_prompt_val = ""
    if quick_prompt != "自行輸入...":
        default_prompt_val = quick_prompt.split(" (")[1][:-1]
        
    prompt = st.text_area(
        "輸入您的創意提示詞 (英文效果尤佳)：",
        value=default_prompt_val,
        height=100,
        placeholder="例如: A golden retriever playing in a field of sunflowers, soft sunset lighting, highly detailed..."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced Options Accordion
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.expander("🛠️ 3. 高級自訂設置 (Advanced Options)", expanded=False):
        
        # Aspect Ratio Selector
        ratio_choice = st.selectbox(
            "圖片尺寸比例 (Aspect Ratio)：",
            options=["1:1 (正方形 - 1024x1024)", "16:9 (橫向寬螢幕 - 1024x576)", "9:16 (直式手機 - 576x1024)"]
        )
        # Parse Aspect Ratio Dimensions
        if "1:1" in ratio_choice:
            dims = (1024, 1024)
        elif "16:9" in ratio_choice:
            dims = (1024, 576)
        else:
            dims = (576, 1024)
            
        # Image Style Presets
        style_choice = st.selectbox(
            "藝術風格 (Image Style)：",
            options=["無特定風格 (None)", "寫實攝影 (Photographic)", "日系動漫 (Anime)", "賽博朋克 (Cyberpunk)", "電影質感 (Cinematic)", "3D 黏土 (3D Clay)"]
        )
        style_mappings = {
            "無特定風格 (None)": "",
            "寫實攝影 (Photographic)": "photorealistic, hyperrealistic, 8k resolution, highly detailed, raw photo",
            "日系動漫 (Anime)": "anime key visual, beautiful anime watercolor illustration, vivid colors",
            "賽博朋克 (Cyberpunk)": "cyberpunk style, neon lights, rainy street reflecting lights, high contrast",
            "電影質感 (Cinematic)": "cinematic shot, warm dramatic volumetric lighting, highly detailed movie still",
            "3D 黏土 (3D Clay)": "cute 3d clay illustration, smooth textures, warm lighting, miniature model"
        }
        style_desc = style_mappings[style_choice]
        
        # Negative Prompt
        negative_prompt = st.text_input(
            "排除提示詞 (Negative Prompt)：",
            value="blurry, low quality, ugly, distorted, lowres, text, signature",
            help="這些元素將會盡量避免出現在生成的圖片中"
        )
        
        # Seed Settings
        is_random_seed = st.checkbox("自動隨機種子 (Random Seed)", value=True)
        if is_random_seed:
            seed = int(time.time()) % 1000000
            st.number_input("種子數值 (Seed)：", value=seed, disabled=True)
        else:
            seed = st.number_input("種子數值 (Seed)：", min_value=0, max_value=99999999, value=42)
            
        # Number of Images
        num_images = st.slider("生成張數 (Number of Images)：", min_value=1, max_value=4, value=1, help="多張生成時將會循序生成")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Button
    generate_btn = st.button("🧙‍♂️ 開始生成 (Generate Image)", use_container_width=True, type="primary")
    
    # Set states on button click
    if generate_btn:
        st.session_state["generation_trigger"] = True
        st.session_state["active_engine"] = engine_choice
        st.session_state["prompt_state"] = prompt
        st.session_state["style_desc_state"] = style_desc
        st.session_state["style_choice_state"] = style_choice
        st.session_state["dims_state"] = dims
        st.session_state["seed_state"] = seed
        st.session_state["num_images_state"] = num_images
        st.session_state["hf_token_state"] = hf_token
        st.session_state["gemini_key_state"] = gemini_key
        st.session_state["is_random_seed_state"] = is_random_seed
        st.session_state["negative_prompt_state"] = negative_prompt

# ----------------- RIGHT PANEL: CANVAS PREVIEW -----------------
with col_right:
    st.markdown('<h4>即時渲染畫布 (Canvas)</h4>', unsafe_allow_html=True)
    
    # Define a clean outer container representing the image frame
    canvas_container = st.container()
    
    # Render generation process or results based on session state
    if st.session_state["generation_trigger"]:
        prompt_val = st.session_state["prompt_state"]
        active_engine = st.session_state["active_engine"]
        style_desc_val = st.session_state["style_desc_state"]
        style_choice_val = st.session_state["style_choice_state"]
        dims_val = st.session_state["dims_state"]
        seed_val = st.session_state["seed_state"]
        num_images_val = st.session_state["num_images_state"]
        hf_token_val = st.session_state["hf_token_state"]
        gemini_key_val = st.session_state["gemini_key_state"]
        is_random_seed_val = st.session_state["is_random_seed_state"]
        negative_prompt_val = st.session_state["negative_prompt_state"]
        
        if not prompt_val.strip():
            st.error("⚠️ 請先在左側輸入一些提示詞再點擊生成！")
            st.session_state["generation_trigger"] = False
        else:
            can_proceed = True
            if "Cosmos3" in active_engine and not hf_token_val:
                st.error("❌ 錯誤：使用 Hugging Face 模型需要填入 API Token！請在左側 Token 輸入框中貼上您的金鑰。")
                can_proceed = False
            elif "Gemini" in active_engine and not gemini_key_val:
                st.error("❌ 錯誤：使用 Gemini 引擎需要填入 API Key！請在左側金鑰輸入框中貼上您的金鑰。")
                can_proceed = False
                
            if can_proceed:
                if "Puter" in active_engine:
                    # Puter.js browser generation injected into iframe
                    import json
                    final_prompt_str = prompt_val
                    if style_desc_val:
                        final_prompt_str = f"{prompt_val}, {style_desc_val}"
                    prompt_json = json.dumps(final_prompt_str)
                    num_images_json = int(num_images_val)
                    
                    puter_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <script src="https://js.puter.com/v2/"></script>
                        <script src="https://cdn.tailwindcss.com"></script>
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
                        <style>
                            body {{
                                background-color: transparent;
                                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                            }}
                            .grid-bg {{
                                background-image: linear-gradient(to right, rgba(0, 0, 0, 0.04) 1px, transparent 1px),
                                                  linear-gradient(to bottom, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
                                background-size: 20px 20px;
                            }}
                            @media (prefers-color-scheme: dark) {{
                                .grid-bg {{
                                    background-image: linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                                                      linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
                                }}
                            }}
                        </style>
                    </head>
                    <body class="p-4 grid-bg min-h-screen text-slate-800 dark:text-slate-100 flex flex-col items-center justify-center">
                        <div id="loading" class="text-center space-y-6 w-full max-w-md px-6 py-12">
                            <div class="relative w-20 h-20 mx-auto">
                                <div class="absolute inset-0 rounded-full border-4 border-slate-200 dark:border-slate-800"></div>
                                <div class="absolute inset-0 rounded-full border-4 border-t-emerald-500 border-r-teal-500 animate-spin"></div>
                                <div class="absolute inset-0 flex items-center justify-center text-emerald-500">
                                    <i class="fa-solid fa-wand-magic-sparkles text-xl animate-bounce"></i>
                                </div>
                            </div>
                            <div class="space-y-2">
                                <h4 class="text-sm font-medium text-slate-700 dark:text-slate-350">Puter.js 正在發送瀏覽器端生圖請求...</h4>
                                <div class="inline-block px-2 py-0.5 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400 rounded text-[10px] font-semibold">
                                    使用引擎: Puter.js (Stable Diffusion XL)
                                </div>
                            </div>
                        </div>

                        <div id="result" class="hidden w-full flex flex-col items-center space-y-6">
                            <div id="image-container">
                                <!-- Images will be inserted here dynamically -->
                            </div>
                            <div class="text-emerald-500 text-xs font-bold" id="time-badge"></div>
                        </div>

                        <script>
                            async function runGeneration() {{
                                const promptText = {prompt_json};
                                const numImages = {num_images_json};
                                const startTime = Date.now();
                                
                                try {{
                                    const promises = [];
                                    for (let i = 0; i < numImages; i++) {{
                                        promises.push(puter.ai.txt2img(promptText, {{
                                            model: "stabilityai/stable-diffusion-xl-base-1.0"
                                        }}));
                                    }}
                                    
                                    const results = await Promise.all(promises);
                                    
                                    const container = document.getElementById('image-container');
                                    container.innerHTML = '';
                                    
                                    if (numImages > 1) {{
                                        container.className = "grid grid-cols-2 gap-4 w-full max-w-2xl";
                                    }} else {{
                                        container.className = "grid grid-cols-1 gap-4 w-full max-w-md";
                                    }}
                                    
                                    results.forEach((res, idx) => {{
                                        if (res && res.src) {{
                                            const wrapper = document.createElement('div');
                                            wrapper.className = "flex flex-col items-center space-y-2 bg-white dark:bg-slate-800 p-3 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm";
                                            
                                            const img = document.createElement('img');
                                            img.src = res.src;
                                            img.className = "max-h-80 w-full object-contain rounded-lg border border-slate-100 dark:border-slate-700";
                                            img.alt = `Generated Image ${{idx+1}}`;
                                            
                                            const downloadBtn = document.createElement('button');
                                            downloadBtn.className = "flex items-center justify-center space-x-2 py-2 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs rounded-lg shadow-sm transition-colors w-full";
                                            downloadBtn.innerHTML = '<i class="fa-solid fa-file-arrow-down"></i><span>下載圖片</span>';
                                            downloadBtn.onclick = () => {{
                                                const link = document.createElement('a');
                                                link.href = res.src;
                                                link.download = `puter_image_${{idx+1}}_${{Date.now()}}.png`;
                                                document.body.appendChild(link);
                                                link.click();
                                                document.body.removeChild(link);
                                            }};
                                            
                                            wrapper.appendChild(img);
                                            wrapper.appendChild(downloadBtn);
                                            container.appendChild(wrapper);
                                        }} else {{
                                            throw new Error("Puter returned empty response.");
                                        }}
                                    }});
                                    
                                    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                                    document.getElementById('time-badge').innerText = `🎉 繪圖成功！費時: ${{elapsed}} 秒`;
                                    document.getElementById('loading').classList.add('hidden');
                                    document.getElementById('result').classList.remove('hidden');
                                }} catch (err) {{
                                    console.error(err);
                                    document.getElementById('loading').innerHTML = `
                                        <span class="text-3xl">⚠️</span>
                                        <p class="text-red-500 font-semibold mt-2">Puter.js 生成失敗</p>
                                        <p class="text-slate-400 text-xs mt-1">${{err.message || '連線逾時'}}</p>
                                        <p class="text-slate-400 text-xs mt-4">請確認您的網路連線或重試。</p>
                                    `;
                                }}
                            }}

                            if (typeof puter !== 'undefined') {{
                                runGeneration();
                            }} else {{
                                window.onload = runGeneration;
                            }}
                        </script>
                    </body>
                    </html>
                    """
                    with canvas_container:
                        import streamlit.components.v1 as components
                        components.html(puter_html, height=520, scrolling=True)
                else:
                    st.toast("🔮 正在發送請求至繪圖伺服器...", icon="🚀")
                    with st.spinner("✨ 魔法繪製中，請稍候... (Cosmos3 首次加載可能需要 1~2 分鐘)"):
                        try:
                            images_result = []
                            start_time = time.time()
                            
                            for i in range(num_images_val):
                                current_seed = seed_val + i if not is_random_seed_val else (seed_val + i * 137) % 1000000
                                
                                if "Cosmos3" in active_engine:
                                    img = generate_huggingface_image(prompt_val, negative_prompt_val, style_desc_val, dims_val, current_seed, hf_token_val)
                                elif "Gemini" in active_engine:
                                    img = generate_gemini_image(prompt_val, style_desc_val, gemini_key_val)
                                else:
                                    img = generate_pollinations_image(prompt_val, style_desc_val, dims_val, current_seed)
                                
                                images_result.append(img)
                            
                            elapsed_time = time.time() - start_time
                            
                            with canvas_container:
                                st.markdown(f'<div class="grid-bg-container">', unsafe_allow_html=True)
                                
                                if len(images_result) == 1:
                                    st.image(images_result[0], caption=f"Prompt: {prompt_val} | Style: {style_choice_val}", use_container_width=True)
                                    buf = io.BytesIO()
                                    images_result[0].save(buf, format="PNG")
                                    byte_im = buf.getvalue()
                                    st.download_button(
                                        label="💾 下載高畫質圖片",
                                        data=byte_im,
                                        file_name=f"ai_image_{int(time.time())}.png",
                                        mime="image/png",
                                        type="secondary"
                                    )
                                else:
                                    cols = st.columns(min(2, len(images_result)))
                                    for idx, img in enumerate(images_result):
                                        with cols[idx % 2]:
                                            st.image(img, caption=f"Image #{idx+1} (Seed: {seed_val + idx})", use_container_width=True)
                                            buf = io.BytesIO()
                                            img.save(buf, format="PNG")
                                            byte_im = buf.getvalue()
                                            st.download_button(
                                                label=f"💾 下載 #{idx+1}",
                                                data=byte_im,
                                                file_name=f"ai_image_{idx+1}_{int(time.time())}.png",
                                                mime="image/png"
                                            )
                                
                                st.markdown(f'<p style="color: #10b981; font-size: 0.85rem; font-weight: bold; margin-top: 1rem;">🎉 繪圖成功！費時: {elapsed_time:.2f} 秒</p>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                st.success("生圖大成功！您可以點選下載按鈕保存成果。")
                                
                        except Exception as e:
                            error_msg = str(e)
                            st.error(f"❌ 生圖失敗：{error_msg}")
                            st.markdown("""
                            > [!WARNING]
                            > **故障排除小助手**：
                            > - **若您使用的是 Cosmos3-Super-Text2Image**，該模型尺寸高達 64B，伺服器可能偶發性離線 (HTTP 503/403)。建議先手動將引擎切換為 **"Puter.js (Stable Diffusion - 完全免金鑰)"**，這是一個備用的免費免金鑰引擎，保證能百分之百順利出圖，方便您完成作業演示！
                            """)
                            with canvas_container:
                                st.markdown("""
                                <div class="grid-bg-container">
                                    <span style="font-size: 3rem;">⚠️</span>
                                    <p style="color: #ef4444; font-weight: 600; margin-top: 0.5rem;">連線異常或模型未啟動</p>
                                    <p style="color: #64748b; font-size: 0.8rem; text-align: center; max-width: 320px;">
                                        伺服器目前無法處理此請求。建議切換至「Puter.js」引擎進行測試與生成。
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
    else:
        # Default placeholder display inside the canvas container
        with canvas_container:
            st.markdown("""
            <div class="grid-bg-container">
                <span style="font-size: 3rem; animation: pulse 2s infinite;">🎨</span>
                <p style="font-weight: bold; color: #475569; margin-top: 0.75rem;">準備完成，等待魔法指令</p>
                <p style="color: #64748b; font-size: 0.8rem; text-align: center; max-width: 380px;">
                    請於左側輸入您的創意想法，調整所需的進階設定，並選擇合適的 AI 引擎，隨後點擊「開始生成」，高畫質 AI 畫作便會立刻在此呈現！
                </p>
            </div>
            """, unsafe_allow_html=True)

# Footer Information
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 0.75rem;">
    HW3 Cosmos3-Super-Text2Image Streamlit Studio | 學生作業繳交專用 | Powered by Hugging Face & Google AI & Puter.js & Pollinations
</div>
""", unsafe_allow_html=True)

