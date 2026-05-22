"""
Streamlit Control Panel - Automation for Streamlit App Updates
==============================================================
לוח בקרה לעדכון אוטומטי של אפליקציות Streamlit דרך AI + GitHub.
 
תכונות:
- 🔄 רענון תצוגה
- ⚙️ הגדרות (כולל מעבר בין אפליקציות מרובות)
- ➕ צירוף תמונה ו/או לינק להמחשה ל-AI
 
Secrets נדרשים (Manage app > Secrets):
    OPENAI_API_KEY = "sk-..."
    GH_TOKEN = "ghp_..."
"""
 
import ast
import base64
from datetime import datetime
 
import requests
import streamlit as st
import streamlit.components.v1 as components
 
# ============================================================
# הגדרת עמוד
# ============================================================
st.set_page_config(
    layout="wide",
    page_title="Streamlit Control Panel",
    initial_sidebar_state="collapsed",
)
 
# ============================================================
# CSS: RTL + רקע כהה + מסגרות + ביטול גלילה
# ============================================================
st.markdown(
    """
    <style>
        html, body {
            overflow: hidden !important;
            height: 100vh;
        }
        .stApp {
            background-color: #0e1117;
            direction: rtl;
            overflow: hidden;
            height: 100vh;
        }
        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-top: 1rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        h1, h2, h3, h4, p, label, .stMarkdown {
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
        }
        div[data-testid="stColumn"] > div {
            border: 1px solid #3a3a3a;
            border-radius: 10px;
            padding: 20px;
            background-color: #0e1117;
            height: calc(100vh - 40px);
            overflow-y: auto;
        }
        .stTextArea textarea {
            border: 1.5px solid #8B0000 !important;
            background-color: #1a1a1a !important;
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
            border-radius: 6px;
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
        }
        .stButton button {
            background-color: #1a1a1a;
            color: #FAFAFA;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 8px 18px;
        }
        .stButton button:hover {
            border-color: #888;
            background-color: #262730;
            color: #FAFAFA;
        }
        /* כפתורי אייקון - עיגול */
        .icon-button button {
            border-radius: 8px !important;
            padding: 6px 10px !important;
            font-size: 18px !important;
            min-height: 38px !important;
        }
        div[data-testid="stIFrame"] iframe,
        .element-container iframe {
            height: calc(100vh - 170px) !important;
            width: 100% !important;
            border-radius: 6px;
            background: #ffffff;
        }
        #MainMenu, footer, header {
            visibility: hidden;
            height: 0 !important;
        }
        div[data-testid="stStatusWidget"] {
            background-color: #1a1a1a !important;
            border: 1px solid #3a3a3a !important;
        }
        /* Popover styling */
        div[data-testid="stPopover"] button {
            border-radius: 8px !important;
            padding: 6px 10px !important;
            font-size: 18px !important;
        }
        /* Selectbox עבור בחירת אפליקציה פעילה */
        .stSelectbox label {
            text-align: right;
            width: 100%;
        }
        /* תגי תמונות מצורפות */
        .attachment-chip {
            display: inline-block;
            background: #1a1a1a;
            border: 1px solid #8B0000;
            border-radius: 12px;
            padding: 4px 10px;
            margin: 4px;
            color: #FAFAFA;
            font-size: 12px;
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
    "apps": {},                  # dict: app_name -> {gh_repo, gh_branch, gh_path, streamlit_url}
    "active_app": None,          # שם האפליקציה הפעילה
    "history": [],
    "iframe_key": 0,             # למניעת cache של iframe
    "attached_images": [],       # list של (filename, bytes)
    "attached_urls": [],         # list של URLs
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
 
# ============================================================
# Helpers
# ============================================================
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        return default
 
 
def active_config():
    """ההגדרות של האפליקציה הפעילה."""
    if not st.session_state.active_app:
        return None
    return st.session_state.apps.get(st.session_state.active_app)
 
 
def gh_headers():
    return {
        "Authorization": f"token {get_secret('GH_TOKEN')}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
 
 
def gh_api_url():
    cfg = active_config()
    return (
        f"https://api.github.com/repos/{cfg['gh_repo']}"
        f"/contents/{cfg['gh_path']}"
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
    """פנייה ל-OpenAI לעדכון הקוד - כולל תמונות ולינקים אם צורפו."""
    from openai import OpenAI
 
    client = OpenAI(api_key=get_secret("OPENAI_API_KEY"))
 
    system_prompt = (
        "You are an expert Python/Streamlit developer. "
        "Update the given Streamlit app code per the user's instruction. "
        "Return ONLY the complete updated Python file. "
        "Do NOT add explanations or wrap in markdown fences (no ```python). "
        "Preserve original structure and imports unless changes are required. "
        "If the user provides reference images, use them as visual guidance for the desired result. "
        "If the user provides reference URLs, consider them as live examples to learn from. "
        "Output must be valid Python that runs as-is."
    )
 
    # בניית תוכן המשתמש - יכול להכיל טקסט + תמונות
    user_text = f"Current code:\n\n{original_code}\n\n---\n\n"
    user_text += f"User instruction (may be in Hebrew):\n{instruction}\n\n"
 
    if extra_urls:
        user_text += "\nReference URLs (live apps to learn from):\n"
        for u in extra_urls:
            user_text += f"- {u}\n"
 
    user_text += "\nReturn the full updated file."
 
    user_content = [{"type": "text", "text": user_text}]
 
    # הוספת תמונות (GPT-4o vision)
    if images:
        for fname, img_bytes in images:
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            # זיהוי mime type
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
    commit_msg = f"Auto-update via Control Panel: {instruction[:60]}"
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(new_code.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": cfg["gh_branch"],
    }
    res = requests.put(gh_api_url(), headers=gh_headers(), json=payload, timeout=20)
    res.raise_for_status()
    return res.json()["commit"]["sha"]
 
 
# ============================================================
# מסך הגדרות (הפעלה ראשונה / עריכה)
# ============================================================
if not st.session_state.configured:
    st.title("🔧 הגדרות סביבת עבודה")
 
    secrets_ok = bool(get_secret("OPENAI_API_KEY")) and bool(get_secret("GH_TOKEN"))
 
    if not secrets_ok:
        st.error(
            "❌ **חסרים Secrets ב-Streamlit Cloud!**\n\n"
            "עבור ל-`Manage app > Settings > Secrets` והגדר:\n"
            "```toml\n"
            'OPENAI_API_KEY = "sk-..."\n'
            'GH_TOKEN = "ghp_..."\n'
            "```"
        )
    else:
        st.success("✅ Secrets קיימים: `OPENAI_API_KEY`, `GH_TOKEN`")
 
    st.markdown("---")
    st.subheader("📚 רשימת אפליקציות")
    st.caption("אפשר להגדיר מספר אפליקציות ולעבור ביניהן בלי לערוך הגדרות בכל פעם.")
 
    # רשימת האפליקציות הקיימות
    if st.session_state.apps:
        for app_name in list(st.session_state.apps.keys()):
            app_cfg = st.session_state.apps[app_name]
            with st.expander(f"📱 {app_name}", expanded=False):
                st.markdown(f"**GitHub:** `{app_cfg['gh_repo']}` | **Branch:** `{app_cfg['gh_branch']}` | **File:** `{app_cfg['gh_path']}`")
                st.markdown(f"**Streamlit:** {app_cfg['streamlit_url']}")
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button(f"🗑 מחק", key=f"del_{app_name}"):
                        del st.session_state.apps[app_name]
                        if st.session_state.active_app == app_name:
                            st.session_state.active_app = None
                        st.rerun()
                with col_y:
                    if st.button(f"⭐ הפוך לפעיל", key=f"act_{app_name}"):
                        st.session_state.active_app = app_name
                        st.rerun()
 
    # טופס הוספת אפליקציה חדשה
    st.markdown("---")
    st.subheader("➕ הוסף אפליקציה חדשה")
 
    new_name = st.text_input("שם תיאורי לאפליקציה:", placeholder="Tube Calculator")
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
            "נתיב לקובץ הראשי בריפו:",
            value="streamlit_app.py",
            key="new_path",
            help="הקובץ המדויק שה-AI יעדכן (לדוגמה 'app (40).py')",
        )
    with col_b:
        st.markdown("**🎈 Streamlit Cloud**")
        sl_url_in = st.text_input(
            "כתובת האפליקציה (URL):",
            placeholder="https://tubecalculator-agc4wsx6yajjx6htfv8syk.streamlit.app/",
            key="new_url",
        )
 
    if st.button("💾 שמור אפליקציה", type="secondary", disabled=not secrets_ok):
        # ולידציה
        errors = []
        if not new_name.strip():
            errors.append("⚠️ יש להזין שם לאפליקציה")
        if not gh_repo_in.strip() or "/" not in gh_repo_in:
            errors.append("⚠️ פורמט Repository שגוי. צריך להיות: `username/repo`")
        if "github.com" in gh_repo_in:
            errors.append("⚠️ אל תכלול `https://github.com/` ב-Repository - רק `username/repo`")
        if not sl_url_in.strip():
            errors.append("⚠️ יש להזין URL של Streamlit")
 
        if errors:
            for e in errors:
                st.error(e)
        else:
            st.session_state.apps[new_name.strip()] = {
                "gh_repo": gh_repo_in.strip(),
                "gh_branch": gh_branch_in.strip() or "main",
                "gh_path": gh_path_in.strip() or "streamlit_app.py",
                "streamlit_url": sl_url_in.strip().rstrip("/"),
            }
            if not st.session_state.active_app:
                st.session_state.active_app = new_name.strip()
            st.success(f"✅ '{new_name.strip()}' נשמרה!")
            st.rerun()
 
    # התחל
    st.markdown("---")
    if st.session_state.apps and st.session_state.active_app:
        st.info(f"📌 אפליקציה פעילה: **{st.session_state.active_app}**")
        if st.button("▶ התחל", type="primary"):
            st.session_state.configured = True
            st.rerun()
    elif st.session_state.apps:
        st.warning("⚠️ יש לבחור אפליקציה פעילה ('⭐ הפוך לפעיל')")
    else:
        st.warning("⚠️ עדיין לא הוגדרה אפליקציה. הוסף לפחות אפליקציה אחת.")
 
    st.stop()
 
 
# ============================================================
# המסך הראשי - שתי עמודות
# ============================================================
col1, col2 = st.columns(2, gap="medium")
 
# =========================================================
# צד ימין: אזור עבודה
# =========================================================
with col1:
    # שורת כותרת עם 3 כפתורי אייקון
    head_cols = st.columns([4, 0.7, 0.7])
    with head_cols[0]:
        st.header("אזור עבודה")
    with head_cols[1]:
        st.markdown('<div class="icon-button">', unsafe_allow_html=True)
        with st.popover("➕", help="צרף תמונה או לינק"):
            st.markdown("### 📎 צירוף קבצים והפניות")
 
            # העלאת תמונה
            uploaded_file = st.file_uploader(
                "העלה תמונה (PNG/JPG):",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key=f"uploader_{len(st.session_state.attached_images)}",
            )
            if uploaded_file is not None:
                if st.button("➕ הוסף תמונה", key="add_img_btn"):
                    st.session_state.attached_images.append(
                        (uploaded_file.name, uploaded_file.getvalue())
                    )
                    st.rerun()
 
            st.markdown("---")
 
            # הזנת URL נוסף
            extra_url_input = st.text_input(
                "לינק לאפליקציה (לדוגמא לבעיה):",
                placeholder="https://...",
                key="extra_url_input",
            )
            if st.button("➕ הוסף לינק", key="add_url_btn"):
                if extra_url_input.strip():
                    st.session_state.attached_urls.append(extra_url_input.strip())
                    st.rerun()
 
            # תצוגה של מה שצורף
            if st.session_state.attached_images or st.session_state.attached_urls:
                st.markdown("---")
                st.markdown("**צורפו:**")
                for i, (fname, _) in enumerate(st.session_state.attached_images):
                    cc = st.columns([5, 1])
                    cc[0].markdown(f"🖼 `{fname}`")
                    if cc[1].button("✖", key=f"rm_img_{i}"):
                        st.session_state.attached_images.pop(i)
                        st.rerun()
                for i, url in enumerate(st.session_state.attached_urls):
                    cc = st.columns([5, 1])
                    cc[0].markdown(f"🔗 `{url[:40]}...`" if len(url) > 40 else f"🔗 `{url}`")
                    if cc[1].button("✖", key=f"rm_url_{i}"):
                        st.session_state.attached_urls.pop(i)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with head_cols[2]:
        st.markdown('<div class="icon-button">', unsafe_allow_html=True)
        if st.button("⚙️", help="הגדרות / החלפת אפליקציה"):
            st.session_state.configured = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
 
    # תווית של האפליקציה הפעילה
    st.caption(f"🎯 אפליקציה פעילה: **{st.session_state.active_app}**")
 
    # אם יש קבצים מצורפים - הצג תקציר
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
        height=140,
        key="instruction_input",
    )
 
    submitted = st.button("שלח הנחיה", type="primary", use_container_width=True)
 
    if submitted:
        if not instruction.strip():
            st.warning("⚠️ יש להזין הנחיה לפני השליחה")
        else:
            with st.status("🔄 מעבד...", expanded=True) as status:
                try:
                    # 1. שליפה
                    status.update(label="📥 שולף קוד נוכחי מ-GitHub...")
                    original_code, file_sha = fetch_current_code()
                    st.write(f"✅ נשלפו {len(original_code):,} תווים (sha: `{file_sha[:7]}`)")
 
                    # 2. AI
                    n_attach = len(st.session_state.attached_images) + len(st.session_state.attached_urls)
                    status.update(label=f"🤖 שולח ל-AI ({n_attach} צרופות)...")
                    new_code = call_ai(
                        original_code,
                        instruction,
                        images=st.session_state.attached_images,
                        extra_urls=st.session_state.attached_urls,
                    )
                    st.write(f"✅ התקבל קוד מעודכן ({len(new_code):,} תווים)")
 
                    # 3. validation
                    status.update(label="🔍 בודק תקינות תחביר...")
                    ok, err = validate_python(new_code)
                    if not ok:
                        status.update(label=f"❌ הקוד פגום: {err}", state="error")
                        with st.expander("הקוד שהתקבל (לבדיקה):"):
                            st.code(new_code, language="python")
                        st.stop()
                    st.write("✅ הקוד תקין תחבירית")
 
                    # 4. commit
                    status.update(label="📤 מעלה ל-GitHub...")
                    commit_sha = commit_to_github(new_code, file_sha, instruction)
                    st.write(f"✅ Commit הצליח: `{commit_sha[:7]}`")
 
                    # 5. שמירה בהיסטוריה + ניקוי צרופות
                    st.session_state.history.append({
                        "ts": datetime.now().strftime("%H:%M:%S"),
                        "app": st.session_state.active_app,
                        "instruction": instruction,
                        "commit": commit_sha[:7],
                    })
                    st.session_state.attached_images = []
                    st.session_state.attached_urls = []
 
                    status.update(
                        label="✅ הושלם! Streamlit יתפרס תוך 1-3 דקות",
                        state="complete",
                    )
 
                except requests.HTTPError as e:
                    status.update(label=f"❌ שגיאת GitHub: {e}", state="error")
                    if e.response is not None:
                        st.code(e.response.text)
                except Exception as e:
                    status.update(label=f"❌ שגיאה: {type(e).__name__}", state="error")
                    st.exception(e)
 
    # היסטוריה
    if st.session_state.history:
        with st.expander(f"📜 היסטוריה ({len(st.session_state.history)})"):
            for h in reversed(st.session_state.history[-15:]):
                st.markdown(
                    f"`{h['ts']}` · **{h.get('app','?')}** · `{h['commit']}` · {h['instruction'][:80]}"
                )
 
 
# =========================================================
# צד שמאל: תצוגת האפליקציה
# =========================================================
with col2:
    head_cols2 = st.columns([5, 0.7])
    with head_cols2[0]:
        st.header("תצוגת אפליקציה (Preview)")
    with head_cols2[1]:
        st.markdown('<div class="icon-button">', unsafe_allow_html=True)
        if st.button("🔄", help="רענן תצוגה"):
            st.session_state.iframe_key += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
 
    cfg = active_config()
    if cfg:
        # מוסיף timestamp כדי שהדפדפן יטען מחדש
        embed_url = f"{cfg['streamlit_url']}/?embed=true&_r={st.session_state.iframe_key}"
        components.iframe(embed_url, height=620, scrolling=True)
    else:
        st.error("לא הוגדרה אפליקציה פעילה")
 
