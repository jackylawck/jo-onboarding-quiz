import streamlit as st
import json
import urllib.parse
from fpdf import FPDF
import os

st.set_page_config(page_title="入職培訓問卷", page_icon="📝")

# ---------------------------------------------------------
# 1. 前端門禁驗證 (Access Code)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 企業內部培訓系統")
    user_code = st.text_input("請輸入員工通行碼以開始測驗：", type="password")
    if st.button("確認"):
        if user_code == st.secrets.get("ACCESS_CODE", "jo2026"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("通行碼錯誤！請重新輸入或聯絡 HR。")
    st.stop()

# ---------------------------------------------------------
# 2. 從 Streamlit Secrets 讀取題庫 JSON
# ---------------------------------------------------------
@st.cache_data
def get_questions():
    questions_str = st.secrets["QUESTIONS_JSON"]
    return json.loads(questions_str)

questions = get_questions()

# ---------------------------------------------------------
# 3. PDF 生成函數 (記憶體中繪製，支援中文)
# ---------------------------------------------------------
def generate_pdf(name, dept, score, total, pass_rate, is_pass):
    pdf = FPDF()
    pdf.add_page()
    
    font_path = "NotoSansTC-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font("NotoSansTC", "", font_path)
        pdf.set_font("NotoSansTC", size=12)
    else:
        pdf.set_font("Helvetica", size=12)

    pdf.cell(200, 10, txt="新員工入職培訓考核結果", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"姓名：{name}", ln=True)
    pdf.cell(200, 10, txt=f"組別：{dept}", ln=True)
    pdf.cell(200, 10, txt=f"答對得分：{score} / {total}", ln=True)
    pdf.cell(200, 10, txt=f"合格率：{pass_rate:.1f}%", ln=True)
    status_str = "合格 (PASS)" if is_pass else "不合格 (FAIL)"
    pdf.cell(200, 10, txt=f"考核結果：{status_str}", ln=True)
    
    return bytes(pdf.output())

# ---------------------------------------------------------
# 4. 問卷 UI 畫面渲染
# ---------------------------------------------------------
st.title("📝 新員工入職培訓問卷")

user_answers = {}

with st.form("quiz_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名 *")
    with col2:
        dept = st.text_input("組別 *")
        
    st.divider()
    
    for q in questions:
        if q["type"] == "single":
            user_answers[q["id"]] = st.radio(q["question"], q["options"], key=f"q_{q['id']}")
        elif q["type"] == "multiple":
            user_answers[q["id"]] = st.multiselect(q["question"], q["options"], key=f"q_{q['id']}")
        elif q["type"] == "group_single":
            st.subheader(q["question"])
            sub_ans = {}
            for sub_q in q["sub_questions"]:
                sub_ans[sub_q["sub_id"]] = st.selectbox(
                    sub_q["label"], sub_q["options"], key=f"q_{sub_q['sub_id']}"
                )
            user_answers[q["id"]] = sub_ans
            
    submit_button = st.form_submit_button("提交問卷 (Submit)")

# ---------------------------------------------------------
# 5. 提交後處理：計分 + 下載 PDF + 開啟 Outlook 寄信
# ---------------------------------------------------------
if submit_button:
    if not name or not dept:
        st.warning("請先填寫姓名與組別！")
    else:
        score = 0
        total_items = 20  # 總計 20 分
        
        for q in questions:
            user_ans = user_answers[q["id"]]
            correct_ans = q["answer"] if "answer" in q else None
            
            # 單選題：答對得 1 分
            if q["type"] == "single":
                if [user_ans] == correct_ans:
                    score += 1
                    
            # 多選題：選對 1 個正確選項得 1 分
            elif q["type"] == "multiple":
                for option in user_ans:
                    if option in correct_ans:
                        score += 1
                        
            # 第 3 題（質量目標）：6 個子項各 1 分
            elif q["type"] == "group_single":
                for sub_q in q["sub_questions"]:
                    user_sub_ans = user_ans[sub_q["sub_id"]]
                    if user_sub_ans == sub_q["answer"]:
                        score += 1

        pass_rate = (score / total_items) * 100
        is_pass = score >= 16  # 16 分即達 80% 合格
        status_str = "合格 (PASS)" if is_pass else "不合格 (FAIL)"
        
        # 前端結果展示
        st.success(f"提交成功！得分：{score} / {total_items}（合格率：{pass_rate:.1f}%）")
        if is_pass:
            st.balloons()
            st.success("🎉 恭喜通過入職培訓考核！")
        else:
            st.error("⚠️ 未達 16 分 (80%) 合格標準。")
            
        st.divider()
        st.subheader("📩 請完成以下步驟發送結果給 HR 部門：")

        # 步驟一：下載 PDF 檔案
        pdf_bytes = generate_pdf(name, dept, score, total_items, pass_rate, is_pass)
        st.download_button(
            label="步驟 1：📥 下載考核紀錄 PDF (請隨信附上)",
            data=pdf_bytes,
            file_name=f"入職培訓紀錄_{name}.pdf",
            mime="application/pdf"
        )

        # 步驟二：自動組裝 Outlook 郵件 (mailto)
        email_to = st.secrets.get("HR_EMAIL", "hrd@jumboorient.com.hk")
        email_subject = f"【入職培訓結果】{dept} - {name} ({status_str})"
        
        email_body = f"""HR 同事：

我是 {dept} 的 {name}。
我已完成新員工入職培訓問卷考核，考核結果如下：

• 姓名：{name}
• 組別：{dept}
• 答對得分：{score} / {total_items}
• 合格率：{pass_rate:.1f}%
• 考核結果：{status_str}

（附件已附上「入職培訓紀錄_{name}.pdf」檔案）
"""
        # 轉碼為 URL 安全格式
        mailto_url = f"mailto:{email_to}?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"

        st.write("")
        st.markdown(
            f'<a href="{mailto_url}" target="_blank" style="text-decoration:none;">'
            f'<button style="background-color:#0078D4; color:white; padding:12px 24px; border:none; border-radius:6px; font-size:16px; font-weight:bold; cursor:pointer;">'
            f'步驟 2：📧 點擊此處直接開啟 Outlook 發送信件'
            f'</button></a>',
            unsafe_allow_url_safe=True
        )
