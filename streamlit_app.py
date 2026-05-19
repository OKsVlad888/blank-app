import streamlit as st
import openai, requests, base64
from PIL import Image

# 📝 הגדרות בסיסיות
GH_PATH = st.secrets.get("GH_PATH", "app.py")  # נתיב הקובץ בקוד (ברירת מחדל app.py)st.set_page_config(layout="wide", page_title="לוח בקרה - עדכון קוד")
openai.api_key = OPENAI_API_KEY

# כותרות וממשק בסיסי
col1, col2 = st.columns(2)
with col1:
    st.header("אזור עבודה")
    # בחירת תמונת מסך (אופציונלי)
    image_file = st.file_uploader("📷 תמונת מסך עם סימונים (אופציונלי):", type=["png", "jpg", "jpeg"])
    instruction = st.text_area("הנחיה (שינוי מבוקש בקוד):", placeholder="למשל: שנה את כותרת העמוד לצבע כחול")
    submit = st.button("🚀 שלח הנחיה")
    commit_change = False  # דגל להמשך לוגיקה

    if submit and instruction.strip() == "" and image_file is None:
        st.error("❗ יש להזין הנחיה טקסטואלית או תמונה עם הסברים לביצוע שינוי.")
    elif submit:
        # שלב 1: שליפת הקוד הנוכחי מהריפו
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_PATH}?ref={GH_BRANCH}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            st.error("⚠️ שגיאה בשליפת הקוד מהריפו. אנא בדוק את GH_REPO, GH_BRANCH, GH_PATH ונסי/ה מחדש.")
        else:
            file_data = res.json()
            original_code = base64.b64decode(file_data["content"].encode()).decode()
            original_sha = file_data["sha"]

            # שלב 2: הכנה לפרומפט (כולל פענוח תמונה אם קיימת)
            image_annotation_text = ""
            if image_file:
                try:
                    # פתיחת תמונה ופענוח בסיסי (TODO: חיבור למודל תמונה עבור הבנה מלאה)
                    img = Image.open(image_file)
                    # ניתן לשלב OCR או Vision API כאן; כעת הצגה למטרות דמו בלבד
                    st.info("⚠️ עיבוד הנחיות מתמונה יתמך בעדכון עתידי. ממשיך בביצוע הנחיה טקסטואלית בלבד.")
                except Exception as e:
                    st.warning("⚠️ שגיאה בקריאת התמונה, יתבצע רק עיבוד טקסטואלי.")
            
            # שלב 3: יצירת קוד מעודכן עם מודל Copilot (GPT)
            # הודעת מערכת למודל - התמקדות בקוד בלבד
            system_msg = ("אתה מסייע בכתיבת קוד. ענה רק עם קוד Python מעודכן הרלוונטי לשינוי המבוקש, ללא הסברים.")
            user_prompt = f"""הקוד הנוכחי הוא:\n```python\n{original_code}\n```\n"""
            if instruction:
                user_prompt += f"\nהשינוי המבוקש: {instruction}\n"
            if image_annotation_text:
                user_prompt += f"\nהערות מתוך תמונה: {image_annotation_text}\n"
            user_prompt += "\nאנא תן רק את הקוד המעודכן הנדרש."
            try:
                with st.spinner("יוצר שינוי בקוד באמצעות AI..."):
                    response = openai.ChatCompletion.create(
                        model="gpt-4",  # שימוש במודל GPT-4 (מקביל ל-GPT-5.5 לחשיבה מעמיקה ב-Copilot)
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0  # שמירה על עקביות
                    )
                new_code = response["choices"][0]["message"]["content"]
            except Exception as e:
                st.error(f"❌ שגיאה בקריאת המודל: {e}")
                new_code = None

            if new_code:
                # שלב 4: בקרת איכות אוטומטית (Self-Review)
                review_msg = f"הקוד המוצע הוא:\n```python\n{new_code}\n```\nבדוק אם הקוד פותר את הדרישה המלאה, והאם יש בו שגיאות או חלקים חסרים."
                try:
                    review_response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "user", "content": review_msg}
                        ],
                        temperature=0
                    )
                    review_notes = review_response["choices"][0]["message"]["content"]
                except Exception as e:
                    review_notes = "שגיאה בביקורת אוטומטית."
                
                # שלב 5: הצגת השינויים למשתמש לאישור
                st.subheader("👁️‍🗨️ שינויים מוצעים:")
                st.code(new_code, language="python")
                # הצגת הערות המודל (אם יש תוכן משמעותי)
                if review_notes:
                    st.write("**הערות אוטומטיות על השינוי:**")
                    st.write(review_notes)
                # כפתור אישור commit
                if st.button("✅ אשר ועדכן (Commit)"):
                    commit_change = True

    # אם המשתמש אישר commit, לבצע עדכון בריפו
    if commit_change:
        st.write("💾 מבצע עדכון בריפוזיטורי GitHub... אנא המתן.")
        try:
            # הכנת תוכן לקודד Base64 עבור ה-API
            encoded_content = base64.b64encode(new_code.encode()).decode()
            commit_msg = f"Update via Copilot UI ({instruction[:30]}...)" if instruction else "Update via Copilot UI"
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
                st.error(f"⚠️ שגיאה בביצוע commit: {res_commit.status_code} - {res_commit.text}")
        except Exception as e:
            st.error(f"⚠️ שגיאה בעת התחברות ל-GitHub: {e}")

        # שלב 7: Streamlit Cloud יזהה את ה-commit ויפרס את האפליקציה מחדש
        st.write("⏳ ממתין לרענון האפליקציה עם השינויים... (ייתכן מספר שניות)")
        # <אופציונלי: כאן ניתן להכניס בדיקת GET ל-URL לוודא שהאפליקציה עלתה כשורה>

with col2:
    st.header("תצוגת אפליקציה (Preview)")
    app_url = f"https://{GH_REPO.split('/')[0]}.streamlit.app/"  # URL בסיסי, עשוי להשתנות לפי הגדרות Streamlit
    # אם branch אינו main, ייתכן שצריך לעדכן את הקישור ל-Streamlit לפי הגדרות האפליקציה
    components = st.container()
    try:
        # הטמעת האפליקציה החיה באמצעות iframe
        st.components.v1.iframe(f"{app_url}?embed=true", height=800)
    except Exception as e:
        st.error("⚠️ שגיאה בטעינת תצוגת האפליקציה. ייתכן שה-URL אינו נכון.")
    # כפתור להורדת קובץ הקוד העדכני (מהריפו)
    if 'original_code' in locals() and 'new_code' in locals():
        file_to_download = new_code if commit_change and new_code else original_code
        st.download_button("💾 הורד קובץ קוד עדכני", file_to_download, file_name=GH_PATH, mime="text/x-python")

# נדרשים מפתחות: OPENAI_API_KEY, GH_TOKEN, GH_REPO (למשל "User/Repo"), GH_BRANCH (לא חובה, ברירת מחדל "main")
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
GH_TOKEN = st.secrets["GH_TOKEN"]
GH_REPO = st.secrets["GH_REPO"]
GH_BRANCH = st.secrets.get("GH_BRANCH", "main")
