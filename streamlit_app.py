
import streamlit as st
import streamlit.components.v1 as components

# הגדרת עמוד רחב (IDE בדפדפן)
st.set_page_config(layout="wide", page_title="Streamlit Control Panel")

# יצירת שתי עמודות (אזור עבודה משמאל, תצוגת אפליקציה מימין)
col1, col2 = st.columns(2)

# עמודה שמאלית - אזור העבודה
with col1:
    st.header("אזור עבודה")
    instruction = st.text_area("הנחיות לשינוי הקוד:", placeholder="הקלד כאן את השינוי הרצוי...")
    submitted = st.button("שלח הנחיה")
    if submitted:
        st.write("✅ ההנחיה נקלטה (בשלב זה לא מתבצעת פעולה).")

# עמודה ימנית - תצוגת האפליקציה הראשית
with col2:
    st.header("תצוגת אפליקציה (Preview)")
    # TODO: עדכן את כתובת ה-URL של האפליקציה הראשית (כאן כתובת פיקטיבית)
    app_url = "https://<שם-משתמש>.streamlit.app?embed=true"
    components.iframe(app_url, width=700, height=800)
