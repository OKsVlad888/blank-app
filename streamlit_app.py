
import streamlit as st
import openai, requests, base64
from PIL import Image

# 📝 הגדרות בסיסיות וטעינת Secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]   # טעינת מפתח OpenAI מה-Secrets
GH_TOKEN = st.secrets["GH_TOKEN"]
GH_REPO = st.secrets["GH_REPO"]
GH_BRANCH = st.secrets.get("GH_BRANCH", "main")
GH_PATH = st.secrets.get("GH_PATH", "streamlit_app.py")

# הגדרת עמוד רחב (תצוגה מסך מלא)
st.set_page_config(layout="wide", page_title="לוח בקרה - עדכון קוד")
# הגדרת מפתח ה-API לספריית OpenAI
openai.api_key = OPENAI_API_KEY

# יצירת שני טורי עמוד (אזור עבודה ואזור תצוגה)
col1, col2 = st.columns(2)

# עמודה שמאלית - אזור עבודה
with col1:
    st.header("אזור עבודה")
    image_file = st.file_uploader("📷 תמונת מסך עם סימונים (אופציונלי):", type=["png", "jpg", "jpeg"])
    instruction = st.text_area("הנחיה (שינוי מבוקש בקוד):", placeholder="לדוגמה: שנה את כותרת העמוד לצבע כחול")
    submit = st.button("🚀 שלח הנחיה")
    commit_change = False  # דגל שמעיד האם בוצע commit

    if submit:
        if not instruction.strip() and image_file is None:
            st.error("❗ יש להזין הנחיה טקסטואלית או לצרף תמונה עם סימונים לפני המשך.")
        else:
            # שלב 1: שליפת הקוד העדכני מה-Repo של GitHub
            headers = {"Authorization": f"token {GH_TOKEN}"}
            url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_PATH}?ref={GH_BRANCH}"
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                st.error("⚠️ שגיאה בשליפת הקוד מהריפו. בדוק את GH_REPO, GH_BRANCH, GH_PATH ונסה שוב.")
            else:
                file_data = res.json()
                original_code = base64.b64decode(file_data["content"]).decode()
                original_sha = file_data["sha"]

                # שלב 2: הכנת פרומפט עבור המודל (משלבת קוד נוכחי + הדרישה ותיאור מהתמונה)
                image_annotation_text = ""
                if image_file is not None:
                    st.info("⚠️ (תכונה עתידית) כרגע לא מעבדים אוטומטית סימונים מתמונה. מתבצע עיבוד של הטקסט בלבד.")
                user_prompt = f"הקוד הנוכחי הוא:\n```python\n{original_code}\n```\n"
                if instruction:
                    user_prompt += f"\nהשינוי המבוקש: {instruction}\n"
                if image_annotation_text:
                    user_prompt += f"\nהערות מתוך תמונה: {image_annotation_text}\n"
                user_prompt += "\nאנא החזר רק את הקוד המעודכן הדרוש."

                # שלב 3: הפעלת מודל AI (GPT-4) לקבלת הקוד המעודכן
                try:
                    with st.spinner("יוצר שינוי בקוד באמצעות OpenAI..."):
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "אתה מסייע בכתיבת קוד, החזר רק קוד Python חדש על סמך הבקשה."},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0
                        )
                    new_code = response["choices"][0]["message"]["content"]
                except Exception as e:
                    st.error(f"❌ שגיאה בקריאת מודל OpenAI: {e}")
                    new_code = None

                # שלב 4: בקרת איכות אוטומטית (בעזרת המודל עצמו)
                review_notes = ""
                if new_code:
                    review_prompt = f"הקוד המוצע:\n```python\n{new_code}\n```\nהאם הוא פותר במלואו את הדרישה? האם קיימות בעיות בקוד?"
                    try:
                        review_response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[{"role": "user", "content": review_prompt}],
                            temperature=0
                        )
                        review_notes = review_response["choices"][0]["message"]["content"]
                    except Exception as e:
                        review_notes = ""
                    # הצגת הקוד המוצע והערות (אם יש)
                    st.subheader("👁️‍🗨️ שינויים מוצעים בקוד:")
                    st.code(new_code, language="python")
                    if review_notes:
                        st.write("**הערות אוטומטיות:**")
                        st.write(review_notes)
                    # כפתור לאישור השינוי וביצוע commit
                    if st.button("✅ אשר ועדכן (Commit)"):
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
                                st.success("✅ השינוי נשמר בהצלחה במאגר GitHub!")
                                commit_change = True
                            else:
                                st.error(f"⚠️ שגיאה בהעלאת Commit: {res_commit.status_code} - {res_commit.text}")
                        except Exception as e:
                            st.error(f"⚠️ שגיאת חיבור ל-GitHub: {e}")
                        st.write("⏳ ממתין לרענון התצוגה עם השינוי...")

# עמודה ימנית - תצוגת אפליקציה (Preview)
with col2:
    st.header("תצוגת אפליקציה (Preview)")
    app_url = f"https://{GH_REPO.split('/')[0]}.streamlit.app/"
    try:
        st.iframe(f"{app_url}?embed=true", height=800)
    except Exception as e:
        st.error("⚠️ שגיאה בטעינת ה-Preview. (בדוק את URL האפליקציה).")
    # אפשרות להוריד את קובץ הקוד המעודכן
    if 'original_code' in locals():
        file_to_download = new_code if commit_change and 'new_code' in locals() and new_code else original_code
        st.download_button("💾 הורד קובץ קוד", file_to_download, file_name=GH_PATH, mime="text/x-python")
