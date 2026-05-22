"""
Streamlit Control Panel - Automation for Streamlit App Updates
==============================================================
לוח בקרה לעדכון אוטומטי של אפליקציות Streamlit דרך AI + GitHub.
 
WORK FLOW:
1. הפעלה ראשונה: בקשת לינק GitHub + לינק Streamlit
2. המשתמש מזין הנחיה בעברית/אנגלית
3. המערכת שולפת את הקוד הנוכחי מ-GitHub
4. שולחת ל-OpenAI (gpt-4o) עם ההנחיה
5. מקבלת קוד מעודכן + בודקת תקינות תחביר
6. מעלה את הקוד המעודכן ל-GitHub (commit)
7. Streamlit Cloud מתפרס אוטומטית ועדכן את ה-iframe
 
Secrets נדרשים (Manage app > Secrets):
    OPENAI_API_KEY = "sk-..."
    GH_TOKEN = "ghp_..."   # Personal Access Token עם הרשאת repo
 
requirements.txt:
    streamlit
    openai>=1.0
    requests
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
        /* Status box */
        div[data-testid="stStatusWidget"] {
            background-color: #1a1a1a !important;
            border: 1px solid #3a3a3a !important;
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
    "gh_repo": "",
    "gh_branch": "main",
    "gh_path": "streamlit_app.py",
    "streamlit_url": "",
    "history": [],
    "last_diff": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
 
# ============================================================
# Helpers - secrets, github, ai
# ============================================================
def get_secret(key, default=None):
    """קריאת secret מ-Streamlit Cloud עם fallback."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        return default
 
 
def gh_headers():
    token = get_secret("GH_TOKEN")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
 
 
def gh_api_url():
    return (
        f"https://api.github.com/repos/{st.session_state.gh_repo}"
        f"/contents/{st.session_state.gh_path}"
        f"?ref={st.session_state.gh_branch}"
    )
 
 
def fetch_current_code():
    """שליפת הקוד הנוכחי + ה-SHA מ-GitHub."""
    res = requests.get(gh_api_url(), headers=gh_headers(), timeout=20)
    res.raise_for_status()
    data = res.json()
    code = base64.b64decode(data["content"]).decode("utf-8")
    return code, data["sha"]
 
 
def strip_code_fences(text):
    """ניקוי ```python ... ``` שה-AI לפעמים מחזיר."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # להסיר את השורה הראשונה (```python)
        lines = lines[1:]
        # להסיר את השורה האחרונה אם היא ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()
 
 
def validate_python(code):
    """בדיקה שהקוד הוא Python תקני - מונע commit של קוד שבור."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} (line {e.lineno})"
 
 
def call_ai(original_code, instruction):
    """פנייה ל-OpenAI לעדכון הקוד."""
    from openai import OpenAI
 
    client = OpenAI(api_key=get_secret("OPENAI_API_KEY"))
 
    system_prompt = (
        "You are an expert Python/Streamlit developer. "
        "Your job is to update the given Streamlit app code according to the user's instruction. "
        "Return ONLY the complete updated Python file. "
        "Do NOT add explanations, do NOT wrap in markdown fences (no ```python). "
        "Preserve the original structure and imports unless the instruction requires changes. "
        "The output must be valid Python that can run as-is."
    )
    user_prompt = (
        f"Current code:\n\n{original_code}\n\n"
        f"---\n\n"
        f"User instruction (may be in Hebrew):\n{instruction}\n\n"
        f"Return the full updated file."
    )
 
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    return strip_code_fences(completion.choices[0].message.content)
 
 
def commit_to_github(new_code, sha, instruction):
    """העלאת הקוד המעודכן ל-GitHub."""
    commit_msg = f"Auto-update via Control Panel: {instruction[:60]}"
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(new_code.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": st.session_state.gh_branch,
    }
    res = requests.put(gh_api_url(), headers=gh_headers(), json=payload, timeout=20)
    res.raise_for_status()
    return res.json()["commit"]["sha"]
 
 
# ============================================================
# מסך הגדרות (הפעלה ראשונה)
# ============================================================
if not st.session_state.configured:
    st.title("🔧 הגדרות סביבת עבודה")
    st.markdown("**הפעלה ראשונה** – הזן את הפרטים הבאים לפני שמתחילים:")
 
    secrets_ok = bool(get_secret("OPENAI_API_KEY")) and bool(get_secret("GH_TOKEN"))
 
    if not secrets_ok:
        st.error(
            "❌ **חסרים Secrets ב-Streamlit Cloud!**\n\n"
            "עבור ל-`Manage app > Settings > Secrets` והגדר:\n"
            "```toml\n"
            'OPENAI_API_KEY = "sk-..."\n'
            'GH_TOKEN = "ghp_..."\n'
            "```\n"
            "ה-`GH_TOKEN` הוא Personal Access Token של GitHub עם הרשאת `repo` (קריאה+כתיבה)."
        )
    else:
        st.success("✅ Secrets קיימים: `OPENAI_API_KEY`, `GH_TOKEN`")
 
    st.markdown("---")
 
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🐙 GitHub**")
        gh_repo_in = st.text_input(
            "Repository (username/repo):",
            placeholder="OKsVlad888/Tube_Calculator",
            value=st.session_state.gh_repo,
        )
        gh_branch_in = st.text_input("Branch:", value=st.session_state.gh_branch)
        gh_path_in = st.text_input(
            "נתיב לקובץ הראשי בריפו:",
            value=st.session_state.gh_path,
            help="הקובץ שה-AI יעדכן (בדרך כלל streamlit_app.py)",
        )
 
    with col_b:
        st.markdown("**🎈 Streamlit Cloud**")
        sl_url_in = st.text_input(
            "כתובת האפליקציה (URL):",
            placeholder="https://tubecalculator-agc4wsx6yajjx6htfv8syk.streamlit.app/",
            value=st.session_state.streamlit_url,
            help="הלינק המלא של האפליקציה ב-Streamlit Cloud",
        )
 
    st.markdown("---")
    if st.button("שמור והתחל ▶", type="primary", disabled=not secrets_ok):
        if not gh_repo_in or not sl_url_in:
            st.error("⚠️ יש למלא לפחות את ה-Repository ואת ה-URL")
        elif "/" not in gh_repo_in:
            st.error("⚠️ פורמט Repository שגוי. צריך להיות: `username/repo`")
        else:
            st.session_state.gh_repo = gh_repo_in.strip()
            st.session_state.gh_branch = gh_branch_in.strip() or "main"
            st.session_state.gh_path = gh_path_in.strip() or "streamlit_app.py"
            st.session_state.streamlit_url = sl_url_in.strip().rstrip("/")
            st.session_state.configured = True
            st.rerun()
 
    st.stop()
 
 
# ============================================================
# המסך הראשי - שתי עמודות
# ============================================================
col1, col2 = st.columns(2, gap="medium")
 
# -------- צד ימין: אזור עבודה --------
with col1:
    st.header("אזור עבודה")
 
    instruction = st.text_area(
        "הנחיות לשינוי הקוד:",
        placeholder="הקלד כאן את השינוי הרצוי...",
        height=140,
        key="instruction_input",
    )
 
    btn_send, btn_cfg = st.columns([1, 1])
    with btn_send:
        submitted = st.button("שלח הנחיה", type="primary", use_container_width=True)
    with btn_cfg:
        if st.button("⚙️ הגדרות", use_container_width=True):
            st.session_state.configured = False
            st.rerun()
 
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
                    status.update(label="🤖 שולח ל-AI לעדכון הקוד...")
                    new_code = call_ai(original_code, instruction)
                    st.write(f"✅ התקבל קוד מעודכן ({len(new_code):,} תווים)")
 
                    # 3. validation
                    status.update(label="🔍 בודק תקינות תחביר...")
                    ok, err = validate_python(new_code)
                    if not ok:
                        status.update(label=f"❌ הקוד שהתקבל פגום: {err}", state="error")
                        with st.expander("הקוד שהתקבל (לבדיקה):"):
                            st.code(new_code, language="python")
                        st.stop()
                    st.write("✅ הקוד תקין תחבירית")
 
                    # 4. commit
                    status.update(label="📤 מעלה ל-GitHub...")
                    commit_sha = commit_to_github(new_code, file_sha, instruction)
                    st.write(f"✅ Commit הצליח: `{commit_sha[:7]}`")
 
                    # 5. שמירה בהיסטוריה
                    st.session_state.history.append(
                        {
                            "ts": datetime.now().strftime("%H:%M:%S"),
                            "instruction": instruction,
                            "commit": commit_sha[:7],
                        }
                    )
 
                    status.update(
                        label="✅ הושלם! Streamlit Cloud יתפרס בתוך 1-3 דקות",
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
        with st.expander(f"📜 היסטוריית עדכונים ({len(st.session_state.history)})"):
            for h in reversed(st.session_state.history[-15:]):
                st.markdown(
                    f"`{h['ts']}` · **{h['commit']}** · {h['instruction'][:90]}"
                )
 
# -------- צד שמאל: תצוגת האפליקציה --------
with col2:
    header_cols = st.columns([5, 1])
    with header_cols[0]:
        st.header("תצוגת אפליקציה (Preview)")
    with header_cols[1]:
        st.button("🔄", help="רענן תצוגה", on_click=lambda: None)
 
    embed_url = f"{st.session_state.streamlit_url}/?embed=true"
    components.iframe(embed_url, height=620, scrolling=True)
 
