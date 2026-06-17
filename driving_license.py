import streamlit as st
import pandas as pd
import random

# ==========================================
# 🔒 GITHUB SECURITY CONFIGURATION (လုံခြုံရေးအပိုင်း)
# ==========================================
if "sheet_id" in st.secrets:
    SHEET_ID = st.secrets["sheet_id"]
else:
    # သင့်စက်ထဲမှာ စမ်းသပ်နေစဉ်အတွင်း အလုပ်လုပ်နိုင်ရန် ယာယီသတ်မှတ်ချက်
    SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g" 

TAB_NAME = "Quiz_Questions"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={TAB_NAME}"
# ==========================================

def load_data():
    try:
        # Sheet ထဲက စာသားတွေကို ဒေါင်းလုဒ်ဆွဲသည့်စနစ်
        df = pd.read_csv(SHEET_URL, keep_default_na=False)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error("Google Sheet ဖတ်ရတာ အဆင်မပြေပါဘူး။ Link သို့မဟုတ် အင်တာနက်လိုင်းကို ပြန်စစ်ပေးပါ။")
        return None

st.set_page_config(page_title="Driver License Quiz App", page_icon="🚗", layout="wide")
st.title("🚗 Driver License Quiz App")
st.subheader("အင်္ဂလိပ်/မြန်မာ ၂ ဘာသာသုံး လိုင်စင်စာမေးပွဲ လေ့ကျင့်ခန်း")
st.write("---")

df = load_data()

if df is not None:
    # အမှန်တကယ် ဒေတာ ရှိ/မရှိ စစ်ဆေးခြင်း
    all_questions = df.to_dict(orient='records')
    
    # ပထမဆုံး Row မှာ ခေါင်းစဉ်တွေပဲ ပါပြီး ဒေတာ အလွတ်ဖြစ်နေရင် ဖယ်ထုတ်ရန်
    all_questions = [q for q in all_questions if str(q.get('question', '')).strip() != ""]

    if len(all_questions) > 0:
        # --- Session State များ ကနဦးသတ်မှတ်ခြင်း ---
        if 'quiz_questions' not in st.session_state:
            st.session_state.quiz_questions = all_questions
            st.session_state.current_index = 0
            st.session_state.user_answers = {}      
            st.session_state.checked_list = {}        
            st.session_state.submitted = False
            st.session_state.show_translation = False

        questions = st.session_state.quiz_questions
        current_idx = st.session_state.current_index

        # --- Sidebar မေးခွန်းနံပါတ် ခလုတ်များ ---
        st.sidebar.title("🔢 Question Navigator")
        st.sidebar.write(f"မေးခွန်းအရေအတွက် (စုစုပေါင်း - {len(questions)} ခု):")
        
        cols_per_row = 5
        for i in range(0, len(questions), cols_per_row):
            row_cols = st.sidebar.columns(cols_per_row)
            for j in range(cols_per_row):
                btn_idx = i + j
                if btn_idx < len(questions):
                    is_answered = btn_idx in st.session_state.user_answers
                    label = f"{btn_idx + 1}📝" if is_answered else f"{btn_idx + 1}"
                    
                    if btn_idx == current_idx:
                        label = f"👉 {btn_idx + 1}"
                    
                    if row_cols[j].button(label, key=f"nav_{btn_idx}"):
                        st.session_state.current_index = btn_idx
                        st.rerun()

        # --- မေးခွန်းဖြေဆိုဆဲ အပိုင်း ---
        if not st.session_state.submitted:
            q = questions[current_idx]
            
            show_mm = st.checkbox("🔄 Translate to Myanmar (မြန်မာလိုဖတ်ရန်)", value=st.session_state.show_translation)
            st.session_state.show_translation = show_mm

            st.markdown(f"### **Question {current_idx + 1} / {len(questions)}**")
            
            # 📸 ပုံထည့်သွင်းပြသခြင်းပိုင်း
            img_url = str(q.get('image_url', '')).strip()
            if img_url and img_url != "nan" and img_url.startswith("http"):
                st.image(img_url, use_container_width=True)
            
            labels = ["A", "B", "C", "D"]
            
            q_text = q.get('question', '')
            q_text_mm = q.get('question_mm', '')
            
            if show_mm and q_text_mm:
                st.markdown(f"#### 🇲🇲 {q_text_mm}")
                options_dict = {
                    "A": f"A. {q.get('option_a_mm', q.get('option_a', ''))}",
                    "B": f"B. {q.get('option_b_mm', q.get('option_b', ''))}",
                    "C": f"C. {q.get('option_c_mm', q.get('option_c', ''))}",
                    "D": f"D. {q.get('option_d_mm', q.get('option_d', ''))}"
                }
            else:
                st.markdown(f"#### 🇬🇧 {q_text}")
                options_dict = {
                    "A": f"A. {q.get('option_a', '')}",
                    "B": f"B. {q.get('option_b', '')}",
                    "C": f"C. {q.get('option_c', '')}",
                    "D": f"D. {q.get('option_d', '')}"
                }
            
            previous_ans = st.session_state.user_answers.get(current_idx, None)
            default_idx = 0 if previous_ans is None else labels.index(previous_ans)

            is_checked = st.session_state.checked_list.get(current_idx, False)
            
            user_choice = st.radio(
                "Select your answer:", 
                options=labels, 
                index=default_idx, 
                format_func=lambda x: options_dict[x],
                key=f"q_{current_idx}_{show_mm}",
                disabled=is_checked
            )
            
            st.session_state.user_answers[current_idx] = user_choice

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if current_idx > 0:
                    if st.button("⬅️ Previous"):
                        st.session_state.current_index -= 1
                        st.rerun()

            with col2:
                if current_idx < len(questions) - 1:
                    if st.button("Next ➡️"):
                        st.session_state.current_index += 1
                        st.rerun()
                else:
                    if st.button("🎯 Submit All Answers", type="primary"):
                        st.session_state.submitted = True
                        st.rerun()

            with col3:
                if not is_checked:
                    if st.button("🎯 Check Answer"):
                        st.session_state.checked_list[current_idx] = True
                        st.rerun()

            # အဖြေစစ်ခြင်း
            correct_ans = str(q.get('correct_answer', '')).strip().upper()
            if is_checked:
                if user_choice == correct_ans:
                    st.success(f"🟢 Correct! Your answer: {user_choice}")
                else:
                    st.error(f"🔴 Incorrect. Your answer: {user_choice}")
                    st.info(f"💡 Correct Answer is: **{correct_ans}**")

        # --- အဖြေအားလုံး တင်သွင်းပြီးချိန် ---
        elif st.session_state.submitted:
            st.success("🎉 Quiz Completed! ရလဒ်များကို အောက်တွင် စစ်ဆေးနိုင်ပါပြီ။")
            
            correct_count = 0
            for idx, q in enumerate(questions):
                user_ans = st.session_state.user_answers.get(idx, None)
                correct_ans = str(q.get('correct_answer', '')).strip().upper()
                if user_ans == correct_ans:
                    correct_count += 1
                    
            st.metric(label="📊 Total Score", value=f"{correct_count} / {len(questions)}")
            
            passing_score = int(len(questions) * 0.9) if len(questions) > 1 else 1
            if correct_count >= passing_score:
                st.balloons()
                st.success(f"🏆 ဂုဏ်ယူပါတယ်! သင်စာမေးပွဲ အောင်မြင်ပါသည်။")
            else:
                st.warning(f"⚠️ ကြိုးစာပါဦး! စာမေးပွဲအောင်ရန် အနည်းဆုံး {passing_score} မှတ် လိုအပ်ပါသည်။")

            st.subheader("🗒️ Detailed Review (အသေးစိတ် ပြန်လည်ဆန်းစစ်ချက်)")
            st.write("---")

            for idx, q in enumerate(questions):
                user_ans = st.session_state.user_answers.get(idx, "Not Answered")
                correct_ans = str(q.get('correct_answer', '')).strip().upper()
                is_correct = user_ans == correct_ans
                
                img_url = str(q.get('image_url', '')).strip()
                if img_url and img_url != "nan" and img_url.startswith("http"):
                    st.image(img_url, use_container_width=True)
                q_title = q.get('question', 'No Question')
                q_title_mm = q.get('question_mm', '')
                
                if is_correct:
                    st.markdown(f"🟢 **Q{idx + 1}: {q_title}**")
                    if q_title_mm: st.markdown(f"_*မြန်မာ:* {q_title_mm}_")
                    st.write(f"Your Answer: **{user_ans}** (Correct)")
                else:
                    st.markdown(f"🔴 **Q{idx + 1}: {q_title}**")
                    if q_title_mm: st.markdown(f"_*မြန်မာ:* {q_title_mm}_")
                    st.write(f"Your Answer: ~~{user_ans}~~")
                    st.markdown(f"💡 **Correct Answer: {correct_ans}**")
                    
                st.write("---")
                
            if st.button("🔄 Restart Quiz", type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    else:
        st.info("Google Sheet ရဲ့ 'Quiz_Questions' Tab ထဲတွင် မေးခွန်းများ မတွေ့ရသေးပါခင်ဗျာ။ စာသားများ ပြန်လည်စစ်ဆေးပေးပါ။")