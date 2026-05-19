
import streamlit as st
import streamlit.components.v1 as components

# הגדרת עמוד רחב (מסך מפוצל)
st.set_page_config(layout="wide", page_title="Streamlit Control Panel")

# CSS פנימי - עיצוב מסגרות לבנות עם שוליים וצל (כמו כרטיסיות)
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    [data-testid="column"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        margin: 10px;
        border: 1px solid #e6e6e6;
        box-shadow: 0 0 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# יצירת שני אזורי תוכן זה לצד זה
col1, col2 = st.columns(2)

# עמודה שמאלית - אזור עבודה
with col1:
    st.header("אזור עבודה")
    instruction = st.text_area("הנחיות לשינוי הקוד:", placeholder="הקלד כאן את השינוי הרצוי...")
    if st.button("שלח הנחיות"):
        st.write("⚙️ ההנחיה נקלטה (כרגע אין פעולת AI).")

# עמודה ימנית - אזור תצוגה
with col2:
    st.header("תצוגת אפליקציה (Preview)")
    app_url = "https://<שם-משתמש>.streamlit.app?embed=true"  # <<-- עדכן כאן את ה-URL של האפליקציה הראשית שלך
    components.iframe(app_url, width=700, height=800)
