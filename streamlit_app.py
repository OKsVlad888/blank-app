"""
Streamlit Control Panel - Multi-Provider AI Edition
====================================================
לוח בקרה לעדכון אוטומטי של אפליקציות Streamlit דרך AI + GitHub.

תומך ב-4 ספקי AI (בחר אחד לפי מה שיש לך):
- Anthropic Claude (claude-3-5-sonnet)  - מומלץ! עובד מעולה בעברית
- Google Gemini (gemini-1.5-pro)         - חינמי עם מגבלות
- Azure OpenAI                            - אם יש לך גישה דרך העבודה
- OpenAI (gpt-4o)                         - הוריאציה המקורית

Secrets נדרשים (לפחות אחד מהבאים):
    ANTHROPIC_API_KEY = "sk-ant-..."     ← Anthropic Claude
    GOOGLE_API_KEY    = "..."             ← Google Gemini
    AZURE_OPENAI_ENDPOINT = "https://....openai.azure.com"
    AZURE_OPENAI_KEY = "..."
    AZURE_OPENAI_DEPLOYMENT = "gpt-4o"   ← שם ה-deployment ב-Azure
    OPENAI_API_KEY    = "sk-..."         ← OpenAI הקלאסי
    
ותמיד צריך:
    GH_TOKEN = "ghp_..."                 ← GitHub PAT
"""

import ast
import base64
from datetime import datetime
from urllib.parse import quote

import requests
import streamlit as st


# ============================================================
# הגדרת עמוד
# ============================================================
st.set_page_config(
    layout="wide",
    page_title="Streamlit Control Panel",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS
# ============================================================
st.markdown(
    """
    <style>
        html, body, .stApp {
            overflow: hidden !important;
            height: 100vh !important;
            max-height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        html::-webkit-scrollbar, body::-webkit-scrollbar, .stApp::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
        }
        .stApp { background-color: #0e1117; direction: rtl; }
        .block-container, [data-testid="stMainBlockContainer"] {
            padding: 0.4rem 0.7rem !important;
            max-width: 100% !important;
            height: 100vh !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
        }
        h1, h2, h3, h4, p, label, .stMarkdown {
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
        }
        h1 { font-size: clamp(18px, 1.8vw, 26px) !important; margin: 0 0 6px 0 !important; line-height: 1.2 !important; }
        h2 { font-size: clamp(16px, 1.5vw, 22px) !important; margin: 4px 0 !important; line-height: 1.2 !important; }
        h3 { font-size: clamp(14px, 1.2vw, 18px) !important; margin: 3px 0 !important; }
        div[data-testid="stHorizontalBlock"] { gap: 10px !important; }
        .main-screen div[data-testid="stHorizontalBlock"] { height: calc(100vh - 16px) !important; }
        .main-screen div[data-testid="stColumn"] { height: 100% !important; overflow: hidden !important; }
        .main-screen div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
            border: 1px solid #3a3a3a; border-radius: 10px;
            padding: 12px 16px; background-color: #0e1117;
            height: 100% !important; box-sizing: border-box;
            overflow: hidden !important;
            display: flex !important; flex-direction: column !important;
        }
        div[data-testid="stColumn"] *::-webkit-scrollbar { display: none !important; }
        div[data-testid="stColumn"] * { scrollbar-width: none !important; }
        .stTextArea textarea {
            border: 1.5px solid #8B0000 !important;
            background-color: #1a1a1a !important;
            color: #FAFAFA !important;
            text-align: right; direction: rtl;
            border-radius: 6px; font-size: 14px !important;
        }
        .stTextInput input, .stSelectbox select {
            background-color: #1a1a1a !important;
            color: #FAFAFA !important;
            border: 1px solid #444 !important;
            text-align: right; direction: ltr;
            font-size: 13px !important; padding: 4px 8px !important;
        }
        .stTextArea label, .stTextInput label, .stSelectbox label {
            text-align: right; width: 100%;
            font-size: 12px !important; margin-bottom: 2px !important;
        }
        .stButton button {
            background-color: #1a1a1a; color: #FAFAFA;
            border: 1px solid #444; border-radius: 6px;
            padding: 5px 12px; font-size: 13px; min-height: 32px;
        }
        .stButton button:hover { border-color: #888; background-color: #262730; }
        .stButton button[kind="primary"] { background-color: #8B0000; border-color: #8B0000; }
        .stButton button[kind="primary"]:hover { background-color: #a00000; border-color: #a00000; }
        .icon-btn .stButton button,
        .icon-btn div[data-testid="stPopover"] button {
            min-height: 32px !important; height: 32px !important; width: 36px !important;
            padding: 0 !important; font-size: 15px !important; border-radius: 6px !important;
        }
        div[data-testid="stIFrame"], iframe { flex: 1 !important; min-height: 0 !important; border: none !important; }
        iframe {
            height: 100% !important; min-height: calc(100vh - 100px) !important;
            width: 100% !important; border-radius: 6px !important; background: #0e1117 !important;
        }
        #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {
            visibility: hidden !important; height: 0 !important; display: none !important;
        }
        .stCaption, [data-testid="stCaption"] { font-size: 10px !important; color: #888 !important; margin: 2px 0 !important; }
        .attachment-chip {
            display: inline-block; background: #1a1a1a;
            border: 1px solid #8B0000; border-radius: 12px;
            padding: 2px 10px; margin: 2px; color: #FAFAFA; font-size: 11px;
        }
        div[data-testid="stStatusWidget"] { background-color: #1a1a1a !important; border: 1px solid #3a3a3a !important; font-size: 12px !important; }
        div[data-testid="stAlert"] { padding: 6px 10px !important; font-size: 12px !important; margin: 4px 0 !important; }
        div[data-testid="stAlert"] p { font-size: 12px !important; margin: 0 !important; }
        div[data-testid="stExpander"] { border: 1px solid #3a3a3a; border-radius: 6px; margin: 2px 0 !important; }
        div[data-testid="stExpander"] summary { padding: 4px 10px !important; font-size: 12px !important; }
        div[data-testid="stExpander"] details > div {
            padding: 6px 10px !important;
            max-height: 350px !important;
            overflow-y: auto !important;
            scrollbar-width: thin !important;
        }
        div[data-testid="stExpander"] details > div::-webkit-scrollbar {
            display: block !important;
            width: 8px !important;
        }
        div[data-testid="stExpander"] details > div::-webkit-scrollbar-thumb {
            background: #444 !important;
            border-radius: 4px !important;
        }
        /* Scroll גם בתוך status widget לתוכן ארוך */
        div[data-testid="stStatusWidget"] details > div {
            max-height: 400px !important;
            overflow-y: auto !important;
            scrollbar-width: thin !important;
        }
        div[data-testid="stStatusWidget"] details > div::-webkit-scrollbar {
            display: block !important;
            width: 8px !important;
        }
        div[data-testid="stStatusWidget"] details > div::-webkit-scrollbar-thumb {
            background: #444 !important;
            border-radius: 4px !important;
        }
        div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] { margin-bottom: 3px !important; }
        hr { margin: 4px 0 !important; }
        .settings-screen { font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# State init
# ============================================================
DEFAULTS = {
    "configured": False,
    "apps": {},
    "active_app": None,
    "history": [],
    "iframe_key": 0,
    "attached_images": [],
    "attached_urls": [],
    "ai_provider": "anthropic",  # ברירת מחדל: Anthropic Claude
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# Helpers
# ============================================================
def get_secret(key, default=""):
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        return default


def clean_ascii(s):
    """מסיר תווים שאינם ASCII הדפיס - מונע UnicodeEncodeError."""
    if not s:
        return ""
    s = s.strip()
    return "".join(c for c in s if 32 <= ord(c) < 127)


def active_config():
    if not st.session_state.active_app:
        return None
    return st.session_state.apps.get(st.session_state.active_app)


# ============================================================
# GitHub helpers
# ============================================================
def gh_headers():
    raw_token = get_secret("GH_TOKEN", "")
    clean_token = clean_ascii(raw_token)
    if not clean_token:
        raise ValueError("GH_TOKEN ריק או מכיל רק תווים לא חוקיים.")
    return {
        "Authorization": f"token {clean_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Streamlit-Control-Panel",
    }


def validate_gh_token():
    try:
        headers = gh_headers()
        res = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if res.status_code == 200:
            return True, res.json().get("login", "?")
        elif res.status_code == 401:
            return False, "טוקן GitHub שגוי או פג תוקף"
        return False, f"שגיאת GitHub: {res.status_code}"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"שגיאת חיבור: {e}"


def gh_api_url():
    cfg = active_config()
    path_encoded = quote(cfg["gh_path"])
    return (
        f"https://api.github.com/repos/{cfg['gh_repo']}"
        f"/contents/{path_encoded}"
        f"?ref={cfg['gh_branch']}"
    )


def fetch_current_code():
    res = requests.get(gh_api_url(), headers=gh_headers(), timeout=20)
    res.raise_for_status()
    data = res.json()
    code = base64.b64decode(data["content"]).decode("utf-8")
    return code, data["sha"]


def commit_to_github(new_code, sha, instruction):
    cfg = active_config()
    safe_instruction = clean_ascii(instruction[:50]) or "update"
    commit_msg = f"Auto-update via Control Panel: {safe_instruction}"
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(new_code.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": cfg["gh_branch"],
    }
    res = requests.put(gh_api_url(), headers=gh_headers(), json=payload, timeout=30)
    res.raise_for_status()
    return res.json()["commit"]["sha"]


# ============================================================
# AI Providers - בדיקת זמינות
# ============================================================
PROVIDER_INFO = {
    "anthropic": {
        "name": "🟣 Anthropic Claude",
        "secrets": ["ANTHROPIC_API_KEY"],
        "signup": "https://console.anthropic.com",
        "note": "מומלץ! 5$ קרדיט חינם בהרשמה. עובד מעולה בעברית."
    },
    "google": {
        "name": "🔵 Google Gemini",
        "secrets": ["GOOGLE_API_KEY"],
        "signup": "https://aistudio.google.com/app/apikey",
        "note": "חינמי עם מגבלות נדיבות."
    },
    "azure": {
        "name": "☁️ Azure OpenAI",
        "secrets": ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY", "AZURE_OPENAI_DEPLOYMENT"],
        "signup": "https://portal.azure.com",
        "note": "אם יש לחברה שלך גישה ל-Azure - דרוש מנהל IT."
    },
    "openai": {
        "name": "🟢 OpenAI",
        "secrets": ["OPENAI_API_KEY"],
        "signup": "https://platform.openai.com/api-keys",
        "note": "הקלאסי. דורש טעינת קרדיט."
    },
}


def provider_available(provider_id):
    """בודק אם כל ה-secrets הנדרשים לספק קיימים (לפני בדיקת תוקף)."""
    info = PROVIDER_INFO[provider_id]
    return all(bool(clean_ascii(get_secret(s, ""))) for s in info["secrets"])


def validate_anthropic():
    api_key = clean_ascii(get_secret("ANTHROPIC_API_KEY", ""))
    if not api_key:
        return False, "המפתח ריק"
    if not api_key.startswith("sk-ant-"):
        return False, "המפתח לא מתחיל ב-'sk-ant-'"
    try:
        # קריאה זולה - שולחים בקשה קטנה למודל הזול ביותר (Haiku 4.5)
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "hi"}]
            },
            timeout=10,
        )
        if res.status_code == 200:
            return True, f"מפתח תקין ({api_key[:10]}...{api_key[-4:]})"
        elif res.status_code in (401, 403):
            return False, "המפתח שגוי או פג תוקף"
        elif res.status_code == 429:
            return False, "חרגת ממכסה"
        return False, f"שגיאה {res.status_code}: {res.text[:100]}"
    except Exception as e:
        return False, f"שגיאת חיבור: {e}"


def validate_google():
    api_key = clean_ascii(get_secret("GOOGLE_API_KEY", ""))
    if not api_key:
        return False, "המפתח ריק"
    try:
        res = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            timeout=10,
        )
        if res.status_code == 200:
            return True, f"מפתח תקין ({api_key[:6]}...{api_key[-4:]})"
        elif res.status_code in (400, 401, 403):
            return False, "המפתח שגוי או פג תוקף"
        return False, f"שגיאה {res.status_code}"
    except Exception as e:
        return False, f"שגיאת חיבור: {e}"


def validate_azure():
    endpoint = clean_ascii(get_secret("AZURE_OPENAI_ENDPOINT", ""))
    api_key = clean_ascii(get_secret("AZURE_OPENAI_KEY", ""))
    deployment = clean_ascii(get_secret("AZURE_OPENAI_DEPLOYMENT", ""))
    if not (endpoint and api_key and deployment):
        return False, "אחד מ-3 ה-Secrets חסר"
    try:
        url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-01"
        res = requests.post(
            url,
            headers={"api-key": api_key, "Content-Type": "application/json"},
            json={"messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15,
        )
        if res.status_code == 200:
            return True, f"חיבור פעיל ל-{deployment}"
        elif res.status_code == 401:
            return False, "המפתח שגוי"
        elif res.status_code == 404:
            return False, f"Deployment '{deployment}' לא נמצא"
        return False, f"שגיאה {res.status_code}: {res.text[:100]}"
    except Exception as e:
        return False, f"שגיאת חיבור: {e}"


def validate_openai():
    api_key = clean_ascii(get_secret("OPENAI_API_KEY", ""))
    if not api_key:
        return False, "המפתח ריק"
    if not (api_key.startswith("sk-") or api_key.startswith("sk_")):
        return False, "המפתח לא מתחיל ב-'sk-'"
    try:
        res = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        if res.status_code == 200:
            return True, f"מפתח תקין ({api_key[:7]}...{api_key[-4:]})"
        elif res.status_code in (401, 403):
            return False, "המפתח שגוי או נמחק"
        elif res.status_code == 429:
            return False, "חרגת ממכסה / אין קרדיט"
        return False, f"שגיאה {res.status_code}"
    except Exception as e:
        return False, f"שגיאת חיבור: {e}"


VALIDATORS = {
    "anthropic": validate_anthropic,
    "google": validate_google,
    "azure": validate_azure,
    "openai": validate_openai,
}


# ============================================================
# AI Providers - שליחת בקשה לעדכון קוד
# ============================================================
def build_system_prompt():
    return (
        "You are an expert Python/Streamlit developer. "
        "Update the given Streamlit app code per the user's instruction. "
        "Return ONLY the complete updated Python file. "
        "Do NOT add explanations or wrap in markdown fences. "
        "Preserve original structure and imports unless changes are required. "
        "If reference images are provided, use them as visual guidance. "
        "Output must be valid Python that runs as-is."
    )


def build_user_text(original_code, instruction, extra_urls=None):
    user_text = f"Current code:\n\n{original_code}\n\n---\n\n"
    user_text += f"User instruction (may be in Hebrew):\n{instruction}\n\n"
    if extra_urls:
        user_text += "\nReference URLs:\n"
        for u in extra_urls:
            user_text += f"- {u}\n"
    user_text += "\nReturn the full updated file."
    return user_text


def call_anthropic(original_code, instruction, images=None, extra_urls=None):
    api_key = clean_ascii(get_secret("ANTHROPIC_API_KEY", ""))
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY חסר")

    user_text = build_user_text(original_code, instruction, extra_urls)
    content = [{"type": "text", "text": user_text}]

    if images:
        for fname, img_bytes in images:
            mime = "image/png"
            lower = fname.lower()
            if lower.endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            elif lower.endswith(".gif"):
                mime = "image/gif"
            elif lower.endswith(".webp"):
                mime = "image/webp"
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            content.insert(0, {
                "type": "image",
                "source": {"type": "base64", "media_type": mime, "data": b64},
            })

    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-opus-4-7",
            "max_tokens": 16000,
            "system": build_system_prompt(),
            "messages": [{"role": "user", "content": content}],
        },
        timeout=300,
    )
    res.raise_for_status()
    return res.json()["content"][0]["text"]


def call_google(original_code, instruction, images=None, extra_urls=None):
    api_key = clean_ascii(get_secret("GOOGLE_API_KEY", ""))
    if not api_key:
        raise ValueError("GOOGLE_API_KEY חסר")

    user_text = build_user_text(original_code, instruction, extra_urls)
    parts = [{"text": build_system_prompt() + "\n\n" + user_text}]

    if images:
        for fname, img_bytes in images:
            mime = "image/png"
            lower = fname.lower()
            if lower.endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            elif lower.endswith(".gif"):
                mime = "image/gif"
            elif lower.endswith(".webp"):
                mime = "image/webp"
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            parts.append({"inline_data": {"mime_type": mime, "data": b64}})

    res = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": parts}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 16000},
        },
        timeout=300,
    )
    res.raise_for_status()
    return res.json()["candidates"][0]["content"]["parts"][0]["text"]


def call_azure(original_code, instruction, images=None, extra_urls=None):
    endpoint = clean_ascii(get_secret("AZURE_OPENAI_ENDPOINT", ""))
    api_key = clean_ascii(get_secret("AZURE_OPENAI_KEY", ""))
    deployment = clean_ascii(get_secret("AZURE_OPENAI_DEPLOYMENT", ""))
    if not (endpoint and api_key and deployment):
        raise ValueError("חסרים Secrets של Azure")

    user_text = build_user_text(original_code, instruction, extra_urls)
    user_content = [{"type": "text", "text": user_text}]

    if images:
        for fname, img_bytes in images:
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            mime = "image/png"
            lower = fname.lower()
            if lower.endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })

    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-01"
    res = requests.post(
        url,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
            "max_tokens": 16000,
        },
        timeout=300,
    )
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]


def call_openai(original_code, instruction, images=None, extra_urls=None):
    from openai import OpenAI
    api_key = clean_ascii(get_secret("OPENAI_API_KEY", ""))
    if not api_key:
        raise ValueError("OPENAI_API_KEY חסר")

    client = OpenAI(api_key=api_key)
    user_text = build_user_text(original_code, instruction, extra_urls)
    user_content = [{"type": "text", "text": user_text}]

    if images:
        for fname, img_bytes in images:
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            mime = "image/png"
            lower = fname.lower()
            if lower.endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=16000,
    )
    return completion.choices[0].message.content


PROVIDER_CALLERS = {
    "anthropic": call_anthropic,
    "google": call_google,
    "azure": call_azure,
    "openai": call_openai,
}


def call_ai(original_code, instruction, images=None, extra_urls=None):
    provider = st.session_state.ai_provider
    caller = PROVIDER_CALLERS[provider]
    result = caller(original_code, instruction, images, extra_urls)
    return strip_code_fences(result)


def strip_code_fences(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def validate_python(code):
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} (line {e.lineno})"


def safe_iframe(url, height=None):
    if hasattr(st, "iframe"):
        st.iframe(url, height=height)
    else:
        import streamlit.components.v1 as components
        components.iframe(url, height=height or 800, scrolling=True)


# ============================================================
# מסך הגדרות
# ============================================================
if not st.session_state.configured:
    st.markdown('<div class="settings-screen">', unsafe_allow_html=True)
    st.markdown("# 🔧 הגדרות סביבת עבודה")

    # ===== בדיקת GitHub =====
    raw_gh = get_secret("GH_TOKEN", "")
    has_gh = bool(clean_ascii(raw_gh))
    gh_valid = False
    gh_info = ""
    if has_gh:
        gh_valid, gh_info = validate_gh_token()

    # ===== בדיקת זמינות ספקי AI =====
    available_providers = {}
    for pid, info in PROVIDER_INFO.items():
        if provider_available(pid):
            valid, msg = VALIDATORS[pid]()
            available_providers[pid] = {"valid": valid, "msg": msg, "info": info}

    # ===== שורת סטטוס =====
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("**🤖 ספקי AI**")
        if available_providers:
            for pid, data in available_providers.items():
                if data["valid"]:
                    st.success(f"✅ {data['info']['name']}: {data['msg']}")
                else:
                    st.error(f"❌ {data['info']['name']}: {data['msg']}")
        else:
            st.error("❌ אין אף ספק AI מוגדר")

    with col_s2:
        st.markdown("**🐙 GitHub**")
        if has_gh:
            if gh_valid:
                st.success(f"✅ תקין (משתמש: {gh_info})")
            else:
                st.error(f"❌ {gh_info}")
        else:
            st.error("❌ GH_TOKEN חסר")

    # ===== הוראות אם חסרים ספקים =====
    if not available_providers or not any(d["valid"] for d in available_providers.values()):
        with st.expander("ℹ️ איך להוסיף ספק AI? (4 אפשרויות)", expanded=True):
            st.markdown("""
            **לך ל-Streamlit > Manage app > Settings > Secrets והוסף לפחות אחד מאלה:**

            **🟣 Anthropic Claude (מומלץ!)** - עובד מעולה בעברית, 5$ קרדיט חינם
            - הרשם ב-https://console.anthropic.com
            - צור API key
            - הוסף ל-Secrets:
            ```toml
            ANTHROPIC_API_KEY = "sk-ant-..."
            ```

            **🔵 Google Gemini** - חינמי עם מגבלות נדיבות
            - לך ל-https://aistudio.google.com/app/apikey
            - "Create API Key"
            - הוסף ל-Secrets:
            ```toml
            GOOGLE_API_KEY = "AIza..."
            ```

            **☁️ Azure OpenAI** - אם החברה שלך נותנת לך גישה
            - דרוש ממנהל ה-IT שיפעיל Azure OpenAI Service
            - הוסף ל-Secrets:
            ```toml
            AZURE_OPENAI_ENDPOINT = "https://....openai.azure.com"
            AZURE_OPENAI_KEY = "..."
            AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
            ```

            **🟢 OpenAI** - הקלאסי
            ```toml
            OPENAI_API_KEY = "sk-..."
            ```

            **בכל מקרה צריך גם:**
            ```toml
            GH_TOKEN = "ghp_..."
            ```
            """)

    # ===== בחירת ספק פעיל =====
    valid_providers = {pid: d for pid, d in available_providers.items() if d["valid"]}
    if valid_providers:
        provider_options = list(valid_providers.keys())
        provider_labels = [valid_providers[p]["info"]["name"] for p in provider_options]

        # אם הספק הנוכחי לא תקין - עבור לראשון התקין
        if st.session_state.ai_provider not in valid_providers:
            st.session_state.ai_provider = provider_options[0]

        current_idx = provider_options.index(st.session_state.ai_provider)
        selected_label = st.selectbox(
            "ספק AI פעיל:",
            options=provider_labels,
            index=current_idx,
            key="provider_select",
        )
        # שמירת הספק שנבחר
        for pid in provider_options:
            if valid_providers[pid]["info"]["name"] == selected_label:
                st.session_state.ai_provider = pid
                break

    secrets_ok = bool(valid_providers) and gh_valid

    # ===== רשימת אפליקציות =====
    if st.session_state.apps:
        st.markdown("### 📚 רשימת אפליקציות")
        for app_name in list(st.session_state.apps.keys()):
            app_cfg = st.session_state.apps[app_name]
            is_active = (app_name == st.session_state.active_app)
            marker = "⭐ " if is_active else ""
            with st.expander(f"{marker}📱 {app_name}", expanded=False):
                st.markdown(f"**GitHub:** `{app_cfg['gh_repo']}` | **Branch:** `{app_cfg['gh_branch']}` | **File:** `{app_cfg['gh_path']}`")
                st.markdown(f"**Streamlit:** {app_cfg['streamlit_url']}")
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("🗑 מחק", key=f"del_{app_name}"):
                        del st.session_state.apps[app_name]
                        if st.session_state.active_app == app_name:
                            st.session_state.active_app = None
                        st.rerun()
                with col_y:
                    if not is_active and st.button("⭐ הפוך לפעיל", key=f"act_{app_name}"):
                        st.session_state.active_app = app_name
                        st.rerun()

    # ===== הוספת אפליקציה חדשה =====
    has_apps = bool(st.session_state.apps)
    with st.expander("➕ הוסף אפליקציה חדשה", expanded=not has_apps):
        new_name = st.text_input("שם תיאורי:", placeholder="Tube Calculator")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**🐙 GitHub**")
            gh_repo_in = st.text_input("Repository (username/repo):", placeholder="OKsVlad888/Tube_Calculator", key="new_gh_repo")
            gh_branch_in = st.text_input("Branch:", value="main", key="new_branch")
            gh_path_in = st.text_input("נתיב לקובץ הראשי:", value="streamlit_app.py", key="new_path")
        with col_b:
            st.markdown("**🎈 Streamlit Cloud**")
            sl_url_in = st.text_input("URL מלא:", placeholder="https://...streamlit.app/", key="new_url")

        if st.button("💾 שמור אפליקציה", disabled=not secrets_ok):
            errors = []
            if not new_name.strip():
                errors.append("⚠️ יש להזין שם")
            if not gh_repo_in.strip() or "/" not in gh_repo_in:
                errors.append("⚠️ פורמט Repository שגוי - צריך `username/repo`")
            if "github.com" in gh_repo_in:
                errors.append("⚠️ אל תכלול `https://github.com/`")
            if not sl_url_in.strip():
                errors.append("⚠️ יש להזין URL")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.session_state.apps[new_name.strip()] = {
                    "gh_repo": clean_ascii(gh_repo_in.strip()),
                    "gh_branch": clean_ascii(gh_branch_in.strip()) or "main",
                    "gh_path": gh_path_in.strip() or "streamlit_app.py",
                    "streamlit_url": clean_ascii(sl_url_in.strip().rstrip("/")),
                }
                if not st.session_state.active_app:
                    st.session_state.active_app = new_name.strip()
                st.success(f"✅ '{new_name.strip()}' נשמרה!")
                st.rerun()

    # ===== כפתור התחל =====
    if st.session_state.apps and st.session_state.active_app:
        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.info(f"📌 פעיל: **{st.session_state.active_app}** | AI: **{PROVIDER_INFO[st.session_state.ai_provider]['name']}**")
        with col_btn:
            if st.button("▶ התחל", type="primary", use_container_width=True, disabled=not secrets_ok):
                st.session_state.configured = True
                st.rerun()
    elif st.session_state.apps:
        st.warning("⚠️ יש לבחור אפליקציה פעילה (⭐)")
    else:
        st.warning("⚠️ הוסף לפחות אפליקציה אחת")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ============================================================
# המסך הראשי
# ============================================================
st.markdown('<div class="main-screen">', unsafe_allow_html=True)

col_work, col_preview = st.columns(2, gap="small")

# צד ימין: אזור עבודה
with col_work:
    h_cols = st.columns([5, 0.8, 0.8])
    with h_cols[0]:
        st.markdown("## אזור עבודה")
    with h_cols[1]:
        st.markdown('<div class="icon-btn">', unsafe_allow_html=True)
        with st.popover("➕", help="צרף תמונה או לינק"):
            st.markdown("### 📎 צירוף קבצים")
            uploaded_file = st.file_uploader(
                "תמונה:", type=["png", "jpg", "jpeg", "gif", "webp"],
                key=f"up_{len(st.session_state.attached_images)}",
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                if st.button("➕ הוסף תמונה", key="add_img"):
                    st.session_state.attached_images.append((uploaded_file.name, uploaded_file.getvalue()))
                    st.rerun()
            st.markdown("---")
            extra_url_input = st.text_input(
                "לינק לאפליקציה:", placeholder="https://...",
                key="extra_url", label_visibility="collapsed",
            )
            if st.button("➕ הוסף לינק", key="add_url"):
                if extra_url_input.strip():
                    st.session_state.attached_urls.append(extra_url_input.strip())
                    st.rerun()
            if st.session_state.attached_images or st.session_state.attached_urls:
                st.markdown("**צורפו:**")
                for i, (fname, _) in enumerate(st.session_state.attached_images):
                    c1, c2 = st.columns([5, 1])
                    c1.markdown(f"🖼 `{fname[:25]}`")
                    if c2.button("✖", key=f"rm_img_{i}"):
                        st.session_state.attached_images.pop(i)
                        st.rerun()
                for i, url in enumerate(st.session_state.attached_urls):
                    c1, c2 = st.columns([5, 1])
                    c1.markdown(f"🔗 `{url[:25]}...`" if len(url) > 25 else f"🔗 `{url}`")
                    if c2.button("✖", key=f"rm_url_{i}"):
                        st.session_state.attached_urls.pop(i)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with h_cols[2]:
        st.markdown('<div class="icon-btn">', unsafe_allow_html=True)
        if st.button("⚙️", help="הגדרות"):
            st.session_state.configured = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    provider_label = PROVIDER_INFO[st.session_state.ai_provider]["name"]
    st.caption(f"🎯 אפליקציה: **{st.session_state.active_app}** | AI: {provider_label}")

    n_imgs = len(st.session_state.attached_images)
    n_urls = len(st.session_state.attached_urls)
    if n_imgs or n_urls:
        chip_html = ""
        if n_imgs:
            chip_html += f'<span class="attachment-chip">🖼 {n_imgs} תמונות</span>'
        if n_urls:
            chip_html += f'<span class="attachment-chip">🔗 {n_urls} לינקים</span>'
        st.markdown(chip_html, unsafe_allow_html=True)

    instruction = st.text_area(
        "הנחיות לשינוי הקוד:",
        placeholder="הקלד כאן את השינוי הרצוי...",
        height=130, key="instruction_input",
    )

    submitted = st.button("שלח הנחיה", type="primary", use_container_width=True)

    if submitted:
        if not instruction.strip():
            st.warning("⚠️ יש להזין הנחיה")
        else:
            with st.status("🔄 מעבד...", expanded=True) as status:
                try:
                    status.update(label="📥 שולף קוד מ-GitHub...")
                    original_code, file_sha = fetch_current_code()
                    st.write(f"✅ נשלפו {len(original_code):,} תווים")

                    n_att = len(st.session_state.attached_images) + len(st.session_state.attached_urls)
                    status.update(label=f"🤖 שולח ל-{provider_label} ({n_att} צרופות)...")
                    new_code = call_ai(
                        original_code, instruction,
                        images=st.session_state.attached_images,
                        extra_urls=st.session_state.attached_urls,
                    )
                    st.write(f"✅ קוד מעודכן ({len(new_code):,} תווים)")

                    status.update(label="🔍 בודק תחביר...")
                    ok, err = validate_python(new_code)
                    if not ok:
                        status.update(label=f"❌ קוד פגום: {err}", state="error")
                        st.warning(
                            "⚠️ ה-AI החזיר קוד שבור. בדרך כלל זה קורה כשהקוד ארוך מדי "
                            "וה-AI לא הספיק לסיים. נסה שוב או חלק את ההנחיה לחלקים קטנים."
                        )
                        with st.expander("📄 הקוד שהתקבל (לבדיקה)"):
                            # תצוגה גלילתית באמצעות div עם גובה קבוע
                            st.markdown(
                                f'<div style="max-height:400px;overflow-y:auto;'
                                f'border:1px solid #444;border-radius:6px;padding:10px;'
                                f'background:#0e1117;">'
                                f'<pre style="margin:0;color:#FAFAFA;font-size:11px;'
                                f'white-space:pre-wrap;direction:ltr;text-align:left;">'
                                f'{new_code[:50000].replace("<", "&lt;").replace(">", "&gt;")}'
                                f'</pre></div>',
                                unsafe_allow_html=True,
                            )
                        st.stop()
                    st.write("✅ תקין")

                    status.update(label="📤 מעלה ל-GitHub...")
                    commit_sha = commit_to_github(new_code, file_sha, instruction)
                    st.write(f"✅ Commit: `{commit_sha[:7]}`")

                    st.session_state.history.append({
                        "ts": datetime.now().strftime("%H:%M:%S"),
                        "app": st.session_state.active_app,
                        "instruction": instruction,
                        "commit": commit_sha[:7],
                        "provider": st.session_state.ai_provider,
                    })
                    st.session_state.attached_images = []
                    st.session_state.attached_urls = []
                    st.session_state.iframe_key += 1

                    status.update(label="✅ הושלם! Streamlit יתפרס תוך 1-3 דקות", state="complete")

                except ValueError as e:
                    status.update(label="❌ הגדרות פגומות", state="error")
                    st.error(str(e))
                except requests.HTTPError as e:
                    status.update(label="❌ שגיאת HTTP", state="error")
                    if e.response is not None:
                        if e.response.status_code == 404:
                            st.error("הקובץ לא נמצא בריפו (404). בדוק 'נתיב לקובץ הראשי' בהגדרות.")
                        elif e.response.status_code in (401, 403):
                            st.error("שגיאת אימות (401/403). הטוקן/מפתח שגוי או פג תוקף.")
                        elif e.response.status_code == 429:
                            st.error("חרגת ממכסה (429). ייתכן שאין קרדיט.")
                        else:
                            st.code(e.response.text[:500])
                except UnicodeEncodeError:
                    status.update(label="❌ תווים לא חוקיים", state="error")
                    st.error("אחד ה-Secrets מכיל תווים לא ASCII. ייצר מחדש והדבק.")
                except Exception as e:
                    err_name = type(e).__name__
                    err_msg = str(e)
                    if "AuthenticationError" in err_name or "401" in err_msg or "403" in err_msg:
                        status.update(label="❌ אימות נכשל", state="error")
                        st.error(f"המפתח של {provider_label} לא תקף. עבור להגדרות (⚙️) ובדוק.")
                    else:
                        status.update(label=f"❌ {err_name}", state="error")
                        st.exception(e)

    if st.session_state.history:
        with st.expander(f"📜 היסטוריה ({len(st.session_state.history)})"):
            for h in reversed(st.session_state.history[-10:]):
                p = h.get("provider", "?")
                st.markdown(f"`{h['ts']}` · `{h['commit']}` · [{p}] · {h['instruction'][:50]}")

# צד שמאל: תצוגת האפליקציה
with col_preview:
    h_cols2 = st.columns([6, 0.8])
    with h_cols2[0]:
        st.markdown("## תצוגת אפליקציה (Preview)")
    with h_cols2[1]:
        st.markdown('<div class="icon-btn">', unsafe_allow_html=True)
        if st.button("🔄", help="רענן תצוגה"):
            st.session_state.iframe_key += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    cfg = active_config()
    if cfg:
        base_url = cfg["streamlit_url"].rstrip("/")
        embed_url = (
            f"{base_url}/?embed=true"
            f"&embed_options=show_padding"
            f"&embed_options=disable_scrolling"
            f"&embed_options=hide_loading_screen"
            f"&_r={st.session_state.iframe_key}"
        )
        safe_iframe(embed_url, height=2000)
    else:
        st.error("לא הוגדרה אפליקציה פעילה")

st.markdown('</div>', unsafe_allow_html=True)
