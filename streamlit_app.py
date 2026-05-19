import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# הגדרת עמוד רחב (IDE בדפדפן) + רקע כהה
# ============================================================
st.set_page_config(
    layout="wide",
    page_title="Streamlit Control Panel",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS מותאם אישית:
# - כיוון RTL לכל הדף
# - רקע כהה
# - מסגרת אפורה סביב כל עמודה (כרטיס)
# - מסגרת אדומה סביב תיבת הטקסט
# ============================================================
st.markdown(
    """
    <style>
        /* רקע כהה לכל האפליקציה + כיוון מימין לשמאל */
        .stApp {
            background-color: #0e1117;
            direction: rtl;
        }

        /* יישור טקסטים לימין וצבע בהיר */
        h1, h2, h3, h4, p, label, .stMarkdown {
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
        }

        /* מסגרת "כרטיס" סביב כל עמודה */
        div[data-testid="stColumn"] > div {
            border: 1px solid #3a3a3a;
            border-radius: 10px;
            padding: 24px;
            background-color: #0e1117;
            min-height: 850px;
        }

        /* תיבת טקסט: מסגרת אדומה, רקע כהה, טקסט לבן, כיוון RTL */
        .stTextArea textarea {
            border: 1.5px solid #8B0000 !important;
            background-color: #1a1a1a !important;
            color: #FAFAFA !important;
            text-align: right;
            direction: rtl;
            border-radius: 6px;
        }

        /* תווית של תיבת הטקסט - יישור לימין */
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

        /* הסתרת תפריט עליון של Streamlit ופוטר (אופציונלי, ליישור עיצובי) */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# יצירת שתי עמודות.
# שים לב: בעקבות direction: rtl למעלה,
# col1 יוצג בצד ימין (אזור עבודה) ו-col2 בצד שמאל (תצוגת אפליקציה).
# ============================================================
col1, col2 = st.columns(2, gap="medium")

# -------- צד ימין: אזור עבודה --------
with col1:
    st.header("אזור עבודה")
    instruction = st.text_area(
        "הנחיות לשינוי הקוד:",
        placeholder="הקלד כאן את השינוי הרצוי...",
        height=170,
    )
    submitted = st.button("שלח הנחיה")
    if submitted:
        st.success("✅ ההנחיה נקלטה (בשלב זה לא מתבצעת פעולה).")

# -------- צד שמאל: תצוגת האפליקציה --------
with col2:
    st.header("תצוגת אפליקציה (Preview)")
    # TODO: עדכן את כתובת ה-URL של האפליקציה הראשית שברצונך לצפות בה
    app_url = "https://<שם-משתמש>.streamlit.app?embed=true"
    components.iframe(app_url, height=780)
