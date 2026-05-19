import streamlit as st
import openai, requests, base64
from PIL import Image

# 📝 הגדרות בסיסיות וטעינת Secrets
    image_file = st.file_uploader("📷 תמונת מסך עם סימונים (אופציונלי):", type=["png", "jpg", "jpeg"])OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # מפתח ה-API של OpenAI
    instruction = st.text_area("הנחיה (שינוי מבוקש בקוד):", placeholder="למשל: שנה את כותרת העמוד לצבע כחול")
    submit = st.button("🚀 שלח הנחיה")
    commit_change = False  # דגל אם בוצע commit

    if submit and instruction.strip() == "" and image_file is None:
        st.error("❗ יש להזין הנחיה טקסטואלית או תמונה עם סימונים כדי להמשיך.")
    elif submit:
        # שלב 1: שליפת הקוד הנוכחי מהריפו GitHub
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_PATH}?ref={GH_BRANCH}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            st.error("⚠️ שגיאה בשליפת הקוד מהריפו. בדוק את GH_REPO, GH_BRANCH, GH_PATH ונסה שוב.")
        else:
            file_data = res.json()
            original_code = base64.b64decode(file_data["content"].encode()).decode()
            original_sha = file_data["sha"]

            # שלב 2: הכנת פרומפט למודל AI (כולל תמונה אם יש)
            image_annotation_text = ""
            if image_file is not None:
                st.info("⚠️ עיבוד תמונה לא נתמך עדיין - ממשיך עם ההנחיה הטקסטואלית בלבד.")
            user_prompt = f"הקוד הנוכחי הוא:\n```python\n{original_code}\n```\n"
            if instruction:
                user_prompt += f"\nהשינוי המבוקש: {instruction}\n"
            if image_annotation_text:
                user_prompt += f"\nהערות מתוך תמונה: {image_annotation_text}\n"
            user_prompt += "\nאנא הפק רק את הקוד המעודכן הדרוש."

            # שלב 3: יצירת קוד מעודכן עם מודל AI
            try:
                with st.spinner("יוצר שינוי בקוד באמצעות AI..."):
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "אתה מסייע בכתיבת קוד. החזר רק קוד Python מעודכן בהתאם לבקשה."},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0
                    )
                new_code = response["choices"][0]["message"]["content"]
            except Exception as e:
                st.error(f"❌ שגיאה בקריאת המודל: {e}")
                new_code = None

            if new_code:
                # שלב 4: בקרת איכות אוטומטית (Self-Review)
                review_prompt = f"הקוד המוצע:\n```python\n{new_code}\n```\nבדוק אם הוא פותר את הדרישה במלואה והאם יש בו בעיות."
                try:
                    review_response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": review_prompt}],
                        temperature=0
                    )
                    review_notes = review_response["choices"][0]["message"]["content"]
                except Exception as e:
                    review_notes = ""
                st.subheader("👁️‍🗨️ שינויים מוצעים:")
                st.code(new_code, language="python")
                if review_notes:
                    st.write("**הערות אוטומטיות על השינוי:**")
                    st.write(review_notes)
                if st.button("✅ אשר ועדכן (Commit)"):
                    commit_change = True
                    try:
                        encoded_content = base64.b64encode(new_code.encode()).decode()
                        commit_msg = f"Update via Copilot UI: {instruction[:30]}..." if instruction else "Update via Copilot UI"
                        payload = {
                            "message": commit_msg,
                            "content": encoded_content,
                            "sha": original_sha,
                            "branch": GH_BRANCH
                        }
                        res_commit = requests.put(url, headers=headers, json=payload)
                        if res_commit.status_code in (200, 201):
                            st.success("✅ השינוי נשמר בריפו בהצלחה!")
                        else:
                            st.error(f"⚠️ שגיאה בביצוע commit: {res_commit.status_code}")
                    except Exception as e:
                        st.error(f"⚠️ שגיאה בעת שליחת commit ל-GitHub: {e}")
                    st.write("⏳ ממתין לרענון האפליקציה לאחר פריסה...")

# עמודה ימנית: תצוגת האפליקציה החיה (Preview)
with col2:
    st.header("תצוגת אפליקציה (Preview)")
    app_url = f"https://{GH_REPO.split('/')[0]}.streamlit.app/"
    try:
        st.iframe(f"{app_url}?embed=true", height=800)
    except Exception as e:
        st.error("⚠️ שגיאה בטעינת תצוגת האפליקציה. ייתכן שה-URL אינו נכון.")
    if 'original_code' in locals() and 'new_code' in locals():
        file_to_download = new_code if commit_change and new_code else original_code
        st.download_button("💾 הורד קובץ קוד עדכני", file_to_download, file_name=GH_PATH, mime="text/x-python")

GH_TOKEN = st.secrets["GH_TOKEN"]
GH_REPO = st.secrets["GH_REPO"]
GH_BRANCH = st.secrets.get("GH_BRANCH", "main")
GH_PATH = st.secrets.get("GH_PATH", "streamlit_app.py")

# הגדרת עמוד רחב + הגדרת OpenAI API Key
st.set_page_config(layout="wide", page_title="לוח בקרה - עדכון קוד")
openai.api_key = OPENAI_API_KEY

# יצירת שני טורים (אזור עבודה ואזור תצוגה)
col1, col2 = st.columns(2)

# עמודה שמאלית: אזור העבודה
with col1:
    st.header("אזור עבודה")
    # בחירת תמונת מסך (אופציונלי)
