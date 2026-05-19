import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# הגדרת עמוד רחב + רקע כהה
# ============================================================
st.set_page_config(
    layout="wide",
    page_title="Streamlit Control Panel",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS מותאם אישית:
# - כיוון RTL, רקע כהה
# - מסגרת אפורה סביב כל עמודה (כרטיס) - בגובה ה-viewport המלא
# - מסגרת אדומה סביב תיבת הטקסט
# - ביטול הגלילה האנכית של הדף ללא שינוי גודל הגופנים
# ============================================================
st.markdown(
    """
    <style>
        /* מניעת גלילה של הדף עצמו */
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

        /* הקטנת ה-padding של המכל הראשי כדי שכל התוכן יכנס למסך */
        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-top: 1rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }

        /* יישור טקסטים לימין + צבע בהיר (ללא שינוי גודל!) */
        h1, h2, h3, h4, p, label, .stMarkdown {
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
        }

        /* מסגרת "כרטיס" סביב כל עמודה - בגובה ה-viewport */
        div[data-testid="stColumn"] > div {
            border: 1px solid #3a3a3a;
            border-radius: 10px;
            padding: 20px;
            background-color: #0e1117;
            height: calc(100vh - 40px);
            overflow: hidden;
        }

        /* תיבת טקסט: מסגרת אדומה, רקע כהה, RTL */
        .stTextArea textarea {
            border: 1.5px solid #8B0000 !important;
            background-color: #1a1a1a !important;
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
            border-radius: 6px;
        }

        .stTextArea label {
            text-align: right;
            width: 100%;
        }

        /* עיצוב הכפתור */
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

        /* iframe ממלא את הגובה הזמין בעמודה */
        div[data-testid="stIFrame"] iframe,
        .element-container iframe {
            height: calc(100vh - 170px) !important;
            width: 100% !important;
        }

        /* הסתרת ה-chrome של Streamlit */
        #MainMenu, footer, header {
            visibility: hidden;
            height: 0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# יצירת שתי עמודות (בעקבות RTL: col1 = ימין, col2 = שמאל)
# ============================================================
col1, col2 = st.columns(2, gap="medium")

# -------- צד ימין: אזור עבודה --------
with col1:
    st.header("אזור עבודה")
    instruction = st.text_area(
        "הנחיות לשינוי הקוד:",
        placeholder="הקלד כאן את השינוי הרצוי...",
        height=140,
    )
    submitted = st.button("שלח הנחיה")
    if submitted:
        st.success("✅ ההנחיה נקלטה (בשלב זה לא מתבצעת פעולה).")

# -------- צד שמאל: תצוגת האפליקציה --------
with col2:
    st.header("תצוגת אפליקציה (Preview)")
    # TODO: עדכן את כתובת ה-URL של האפליקציה הראשית שברצונך לצפות בה
    app_url = "https://<שם-משתמש>.streamlit.app?embed=true"
    components.iframe(app_url, height=620)
