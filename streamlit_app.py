"""
Streamlit Control Panel - Automation for Streamlit App Updates
==============================================================
לוח בקרה לעדכון אוטומטי של אפליקציות Streamlit דרך AI + GitHub.
 
תיקונים בגרסה זו:
- UnicodeEncodeError: ניקוי טוקן GitHub מתווים שאינם ASCII
- st.iframe במקום st.components.v1.iframe (החדש)
- embed_options מעודכנים להסתרת toolbar/footer
- Layout משופר: אזור עבודה דחוס למעלה, תצוגה תופסת את כל המסך
- ביטול מוחלט של כל scroll bars
"""
 
import ast
import base64
import re
from datetime import datetime
 
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
# CSS משופר - ביטול מוחלט של scroll bars + RTL + responsive
# ============================================================
st.markdown(
    """
    <style>
        /* ========== ביטול גלילה גלובלית ========== */
        html, body, .stApp {
            overflow: hidden !important;
            height: 100vh !important;
            max-height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        html::-webkit-scrollbar,
        body::-webkit-scrollbar,
        .stApp::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
        }
 
        .stApp {
            background-color: #0e1117;
            direction: rtl;
        }
 
        /* ========== מכל ראשי - מילוי 100% של החלון ========== */
        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding: 0.5rem 0.8rem !important;
            max-width: 100% !important;
            height: 100vh !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
        }
 
        /* ========== טיפוגרפיה ========== */
        h1, h2, h3, h4, p, label, .stMarkdown {
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
        }
        h2 {
            font-size: clamp(20px, 2vw, 30px) !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.2 !important;
        }
 
        /* ========== עמודות בגובה מלא ========== */
        div[data-testid="stHorizontalBlock"] {
            height: calc(100vh - 20px) !important;
            gap: 10px !important;
            overflow: hidden !important;
        }
        div[data-testid="stColumn"] {
            height: 100% !important;
            overflow: hidden !important;
        }
        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
            border: 1px solid #3a3a3a;
            border-radius: 10px;
            padding: 12px 16px;
            background-color: #0e1117;
            height: 100% !important;
            box-sizing: border-box;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
        }
        div[data-testid="stColumn"] *::-webkit-scrollbar {
            display: none !important;
        }
        div[data-testid="stColumn"] * {
            scrollbar-width: none !important;
        }
 
        /* ========== תיבת טקסט אדומה ========== */
        .stTextArea textarea {
            border: 1.5px solid #8B0000 !important;
            background-color: #1a1a1a !important;
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
            border-radius: 6px;
            font-size: 14px !important;
        }
        .stTextInput input {
            background-color: #1a1a1a !important;
            color: #FAFAFA !important;
            border: 1px solid #444 !important;
            text-align: right;
            direction: ltr;
        }
        .stTextArea label, .stTextInput label {
            text-align: right;
            width: 100%;
            font-size: 13px !important;
        }
 
        /* ========== כפתורים ========== */
        .stButton button {
            background-color: #1a1a1a;
            color: #FAFAFA;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 14px;
        }
        .stButton button:hover {
            border-color: #888;
            background-color: #262730;
        }
        .stButton button[kind="primary"] {
            background-color: #8B0000;
            border-color: #8B0000;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #a00000;
            border-color: #a00000;
        }
 
        /* ========== כפתורי אייקון קטנים ========== */
        .icon-btn .stButton button,
        .icon-btn div[data-testid="stPopover"] button {
            min-height: 34px !important;
            height: 34px !important;
            width: 38px !important;
            padding: 0 !important;
            font-size: 16px !important;
            border-radius: 6px !important;
        }
 
        /* ========== iframe גובה מלא ========== */
        div[data-testid="stIFrame"],
        iframe {
            flex: 1 !important;
            min-height: 0 !important;
            border: none !important;
        }
        iframe {
            height: 100% !important;
            min-height: calc(100vh - 120px) !important;
            width: 100% !important;
            border-radius: 6px !important;
            background: #0e1117 !important;
        }
 
        /* ========== הסתרת ה-chrome של Streamlit ========== */
        #MainMenu, footer, header,
        [data-testid="stToolbar"], 
        [data-testid="stDecoration"] {
            visibility: hidden !important;
            height: 0 !important;
            display: none !important;
        }
 
        /* ========== Caption קטן ========== */
        .stCaption, [data-testid="stCaption"] {
            font-size: 11px !important;
            color: #888 !important;
            margin: 4px 0 !important;
        }
 
        /* ========== Chips לצרופות ========== */
        .attachment-chip {
            display: inline-block;
            background: #1a1a1a;
            border: 1px solid #8B0000;
            border-radius: 12px;
            padding: 2px 10px;
            margin: 2px;
            color: #FAFAFA;
            font-size: 11px;
        }
 
        /* ========== Status widget ========== */
        div[data-testid="stStatusWidget"] {
            background-color: #1a1a1a !important;
            border: 1px solid #3a3a3a !important;
            font-size: 12px !important;
        }
 
        /* ========== Alert (error/warning) compact ========== */
        div[data-testid="stAlert"] {
            padding: 8px 12px !important;
            font-size: 13px !important;
        }
 
        /* ========== Expander דחוס ========== */
        div[data-testid="stExpander"] {
            border: 1px solid #3a3a3a;
            border-radius: 6px;
            margin-top: 6px;
        }
        div[data-testid="stExpander"] summary {
            padding: 6px 10px !important;
            font-size: 12px !important;
        }
 
        /* ========== הקטנת margins ========== */
        div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
            margin-bottom: 4px !important;
        }
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
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
 
# ============================================================
# Helpers - תיקון Unicode + GitHub + AI
# ============================================================
def get_secret(key, default=""):
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        return default
 
 
def clean_ascii(s):
    """
    מנקה מחרוזת מכל תו שאינו ASCII הדפיס (32-126).
    מונע UnicodeEncodeError ב-HTTP headers.
    """
    if not s:
        return ""
    # הסר תווי בקרה, רווחים מיוחדים, BOM, וכו'
    s = s.strip()
    # השאר רק תווי ASCII דפיסים
    cleaned = "".join(c for c in s if 32 <= ord(c) < 127)
    return cleaned
 
 
def active_config():
    if not st.session_state.active_app:
        return None
    return st.session_state.apps.get(st.session_state.active_app)
 
 
def gh_headers():
    """
    בונה headers עם טוקן מנוקה - מונע UnicodeEncodeError.
    """
    raw_token = get_secret("GH_TOKEN", "")
    clean_token = clean_ascii(raw_token)
    if not clean_token:
        raise ValueError(
            "GH_TOKEN ריק או מכיל רק תווים לא חוקיים. "
            "ייצר מחדש את הטוקן ב-GitHub והדבק שוב ב-Secrets של Streamlit."
        )
    return {
        "Authorization": f"token {clean_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Streamlit-Control-Panel",
    }
 
 
def validate_token():
    """
    בודק את הטוקן מול GitHub API.
    מחזיר (True, username) אם תקין, (False, error_message) אחרת.
    """
    try:
        headers = gh_headers()
        res = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if res.status_code == 200:
            return True, res.json().get("login", "?")
        elif res.status_code == 401:
            return False, "טוקן GitHub שגוי או פג תוקף"
        else:
            return False, f"שגיאת GitHub: {res.status_code}"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"שגיאת חיבור: {e}"
 
 
def gh_api_url():
    cfg = active_config()
    # ה-path עלול להכיל רווחים/תווים מיוחדים - נדאג ל-URL encoding
    from urllib.parse import quote
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
 
 
def call_ai(original_code, instruction, images=None, extra_urls=None):
    from openai import OpenAI
 
    api_key = clean_ascii(get_secret("OPENAI_API_KEY", ""))
    if not api_key:
        raise ValueError("OPENAI_API_KEY חסר או לא תקין")
 
    client = OpenAI(api_key=api_key)
 
    system_prompt = (
        "You are an expert Python/Streamlit developer. "
        "Update the given Streamlit app code per the user's instruction. "
        "Return ONLY the complete updated Python file. "
        "Do NOT add explanations or wrap in markdown fences. "
        "Preserve original structure and imports unless changes are required. "
        "If reference images are provided, use them as visual guidance. "
        "Output must be valid Python that runs as-is."
    )
 
    user_text = f"Current code:\n\n{original_code}\n\n---\n\n"
    user_text += f"User instruction (may be in Hebrew):\n{instruction}\n\n"
 
    if extra_urls:
        user_text += "\nReference URLs:\n"
        for u in extra_urls:
            user_text += f"- {u}\n"
 
    user_text += "\nReturn the full updated file."
 
    user_content = [{"type": "text", "text": user_text}]
 
    if images:
        for fname, img_bytes in images:
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            mime = "image/png"
            lower = fname.lower()
            if lower.endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            elif lower.endswith(".gif"):
                mime = "image/gif"
            elif lower.endswith(".webp"):
                mime = "image/webp"
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })
 
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
    )
    return strip_code_fences(completion.choices[0].message.content)
 
 
def commit_to_github(new_code, sha, instruction):
    cfg = active_config()
    # ה-commit message - מנקה כדי שיהיה ASCII
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
 
 
def safe_iframe(url, height=None):
    """
    תאימות לאחור: משתמש ב-st.iframe (חדש) אם קיים, אחרת בישן.
    """
    if hasattr(st, "iframe"):
        st.iframe(url, height=height, scrolling=True)
    else:
        import streamlit.components.v1 as components
        components.iframe(url, height=height or 800, scrolling=True)
 
 
# ============================================================
# מסך הגדרות
# ============================================================
if not st.session_state.configured:
    st.title("🔧 הגדרות סביבת עבודה")
 
    raw_openai = get_secret("OPENAI_API_KEY", "")
    raw_gh = get_secret("GH_TOKEN", "")
    has_openai = bool(clean_ascii(raw_openai))
    has_gh = bool(clean_ascii(raw_gh))
 
    # בדיקת תקינות secrets
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if has_openai:
            st.success("✅ OPENAI_API_KEY נמצא")
        else:
            st.error("❌ OPENAI_API_KEY חסר/פגום")
    with col_s2:
        if has_gh:
            # בדיקה מול GitHub
            valid, info = validate_token()
            if valid:
                st.success(f"✅ GH_TOKEN תקין (משתמש: {info})")
            else:
                st.error(f"❌ GH_TOKEN לא תקין: {info}")
                st.info(
                    "🔧 **תיקון:** לך ל-https://github.com/settings/tokens, "
                    "מחק את הטוקן הישן וצור חדש (עם הרשאת `repo`). "
                    "אז עבור ל-Streamlit > Manage app > Settings > Secrets והדבק שוב."
                )
        else:
            st.error("❌ GH_TOKEN חסר")
 
    if not (has_openai and has_gh):
        st.markdown(
            "**הגדר Secrets ב-Streamlit Cloud:**\n"
            "```toml\n"
            'OPENAI_API_KEY = "sk-..."\n'
            'GH_TOKEN = "ghp_..."\n'
            "```"
        )
 
    secrets_ok = has_openai and has_gh
 
    st.markdown("---")
    st.subheader("📚 רשימת אפליקציות")
 
    if st.session_state.apps:
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
 
    st.markdown("---")
    st.subheader("➕ הוסף אפליקציה חדשה")
 
    new_name = st.text_input("שם תיאורי:", placeholder="Tube Calculator")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🐙 GitHub**")
        gh_repo_in = st.text_input(
            "Repository (username/repo):",
            placeholder="OKsVlad888/Tube_Calculator",
            key="new_gh_repo",
        )
        gh_branch_in = st.text_input("Branch:", value="main", key="new_branch")
        gh_path_in = st.text_input(
            "נתיב לקובץ הראשי:",
            value="streamlit_app.py",
            key="new_path",
            help="לדוגמה: 'app (40).py'",
        )
    with col_b:
        st.markdown("**🎈 Streamlit Cloud**")
        sl_url_in = st.text_input(
            "URL מלא:",
            placeholder="https://tubecalculator-agc4wsx6yajjx6htfv8syk.streamlit.app/",
            key="new_url",
        )
 
    if st.button("💾 שמור אפליקציה", disabled=not secrets_ok):
        errors = []
        if not new_name.strip():
            errors.append("⚠️ יש להזין שם")
        if not gh_repo_in.strip() or "/" not in gh_repo_in:
            errors.append("⚠️ פורמט Repository שגוי - צריך `username/repo`")
        if "github.com" in gh_repo_in:
            errors.append("⚠️ אל תכלול `https://github.com/` ב-Repository")
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
 
    st.markdown("---")
    if st.session_state.apps and st.session_state.active_app:
        st.info(f"📌 אפליקציה פעילה: **{st.session_state.active_app}**")
        if st.button("▶ התחל", type="primary"):
            st.session_state.configured = True
            st.rerun()
    elif st.session_state.apps:
        st.warning("⚠️ יש לבחור אפליקציה פעילה")
    else:
        st.warning("⚠️ הוסף לפחות אפליקציה אחת")
 
    st.stop()
 
 
# ============================================================
# המסך הראשי - 2 עמודות שוות
# ============================================================
col_work, col_preview = st.columns(2, gap="small")
 
# =========================================================
# צד ימין: אזור עבודה
# =========================================================
with col_work:
    # שורת כותרת + כפתורי אייקון
    h_cols = st.columns([5, 0.8, 0.8])
    with h_cols[0]:
        st.markdown("## אזור עבודה")
    with h_cols[1]:
        st.markdown('<div class="icon-btn">', unsafe_allow_html=True)
        with st.popover("➕", help="צרף תמונה או לינק"):
            st.markdown("### 📎 צירוף קבצים")
            uploaded_file = st.file_uploader(
                "תמונה:",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key=f"up_{len(st.session_state.attached_images)}",
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                if st.button("➕ הוסף תמונה", key="add_img"):
                    st.session_state.attached_images.append(
                        (uploaded_file.name, uploaded_file.getvalue())
                    )
                    st.rerun()
            st.markdown("---")
            extra_url_input = st.text_input(
                "לינק לאפליקציה:",
                placeholder="https://...",
                key="extra_url",
                label_visibility="collapsed",
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
 
    st.caption(f"🎯 אפליקציה פעילה: **{st.session_state.active_app}**")
 
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
        height=130,
        key="instruction_input",
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
                    status.update(label=f"🤖 שולח ל-AI ({n_att} צרופות)...")
                    new_code = call_ai(
                        original_code,
                        instruction,
                        images=st.session_state.attached_images,
                        extra_urls=st.session_state.attached_urls,
                    )
                    st.write(f"✅ קוד מעודכן ({len(new_code):,} תווים)")
 
                    status.update(label="🔍 בודק תחביר...")
                    ok, err = validate_python(new_code)
                    if not ok:
                        status.update(label=f"❌ קוד פגום: {err}", state="error")
                        with st.expander("הקוד שהתקבל:"):
                            st.code(new_code, language="python")
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
                    })
                    st.session_state.attached_images = []
                    st.session_state.attached_urls = []
                    st.session_state.iframe_key += 1
 
                    status.update(
                        label="✅ הושלם! Streamlit יתפרס תוך 1-3 דקות",
                        state="complete",
                    )
 
                except ValueError as e:
                    status.update(label=f"❌ הגדרות פגומות", state="error")
                    st.error(str(e))
                except requests.HTTPError as e:
                    status.update(label=f"❌ שגיאת GitHub", state="error")
                    if e.response is not None:
                        if e.response.status_code == 404:
                            st.error("הקובץ לא נמצא בריפו. בדוק את 'נתיב לקובץ הראשי' בהגדרות.")
                        elif e.response.status_code == 401:
                            st.error("הטוקן של GitHub שגוי או פג תוקף. ייצר חדש והדבק ב-Secrets.")
                        else:
                            st.code(e.response.text[:500])
                except UnicodeEncodeError:
                    status.update(label="❌ תווים לא חוקיים בטוקן", state="error")
                    st.error(
                        "ה-GH_TOKEN ב-Secrets מכיל תווים לא ASCII. "
                        "ייצר טוקן חדש ב-https://github.com/settings/tokens והדבק שוב."
                    )
                except Exception as e:
                    status.update(label=f"❌ {type(e).__name__}", state="error")
                    st.exception(e)
 
    if st.session_state.history:
        with st.expander(f"📜 היסטוריה ({len(st.session_state.history)})"):
            for h in reversed(st.session_state.history[-10:]):
                st.markdown(
                    f"`{h['ts']}` · `{h['commit']}` · {h['instruction'][:60]}"
                )
 
# =========================================================
# צד שמאל: תצוגת האפליקציה
# =========================================================
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
        # embed=true עם כל ה-flags להסתרת toolbar/footer
        # ה-parameters הנכונים לפי תיעוד Streamlit Cloud עדכני
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
 
