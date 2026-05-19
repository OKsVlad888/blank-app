
import streamlit as st
import streamlit.components.v1 as components

# הגדרת עמוד רחב (שני חלקים)
st.set_page_config(layout="wide", page_title="Streamlit Control Panel")

# CSS: רקע אפור, וכרטיס לבן (שני צדדים) עם גבול וצל
st.markdown("""
<style>
    .stApp {background-color: #f0f2f6;} /* רקע כללי - אפור בהיר */
    [data-testid="column"] {
        background-color: #FFFFFF !important;
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        box-shadow: 0 0 8px rgba(0,0,0,0.1);
        padding: 20px;
        margin: 10px 5px;
    }
</style>
""", unsafe_allow_html=True)

# יצירת שני טורים (אזורים) זה לצד זה
col1, col2 = st.columns(2, gap="medium")

# עמודה שמאלית - אזור עבודה (הכנסת הנחיות)
with col1:
    st.header("אזור עבודה")
    instruction = st.text_area("הנחיות לשינוי הקוד:", placeholder="הקלד כאן את השינוי הרצוי...")
    if st.button("שלח הנחיות"):
        st.write("⚙️ ההנחיה נקלטה (כרגע אין פעולת AI).")

# עמודה ימנית - אזור תצוגת האפליקציה הראשית
with col2:
    st.header("תצוגת אפליקציה (Preview)")
    app_url = "https://<שם-משתמש>.streamlit.app?embed=true"  # <<-- עדכן כאן לכתובת האפליקציה הראשית שלך
    st.iframe(app_url, height=800)
