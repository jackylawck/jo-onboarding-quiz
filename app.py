import streamlit as st
import json
import urllib.parse
from fpdf import FPDF
import os
import textwrap
from datetime import datetime, timezone, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

st.set_page_config(page_title="東淦新員工入職培訓考核及問卷系統", page_icon="📝", layout="centered")

# ---------------------------------------------------------
# 1. 前端門禁驗證 (支援 URL 參數自動解鎖 & 手動輸入)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

query_params = st.query_params
passed_key = query_params.get("key", "").lower()
valid_access_code = st.secrets.get("ACCESS_CODE", "jo1996").lower()

if passed_key in [valid_access_code, "hr1", "jo1996"]:
    st.session_state.authenticated = True

if not st.session_state.authenticated:
    st.title("🔒 東淦新員工入職培訓考核及問卷系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    user_code = st.text_input("請輸入員工通行碼以開始測驗：", type="password")
    if st.button("確認進入"):
        if user_code.lower() in [valid_access_code, "hr1", "jo1996"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("通行碼錯誤！請重新輸入或由公司內部 SharePoint 入口進入。")
    st.stop()

# ---------------------------------------------------------
# 2. Session State 流程與狀態控管
# ---------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}

if "email_sent" not in st.session_state:
    st.session_state.email_sent = False

# ---------------------------------------------------------
# 3. 讀取測驗題庫 (完全由 Secrets 保密)
# ---------------------------------------------------------
@st.cache_data
def get_questions():
    questions_str = st.secrets["QUESTIONS_JSON"]
    return json.loads(questions_str)

questions = get_questions()

DEPT_OPTIONS = [
    "請選擇組別", "管理層", "寫字樓", "人力資源組", "行政組", "計量組", 
    "規劃驗證組", "發判組", "項目組", "施工組", "工程組", 
    "安全及環保組", "營運審計組", "會計組", "物控組", "倉管組", "其他"
]

def clean_text(val):
    if not val:
        return "無"
    cleaned = str(val).replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
    return cleaned if cleaned else "無"

def print_safe_text(pdf, text, max_chars=32):
    lines = textwrap.wrap(clean_text(text), width=max_chars)
    if not lines:
        pdf.cell(0, 6, txt="無", ln=1)
    else:
        for line in lines:
            pdf.cell(0, 6, txt=line, ln=1)

# ---------------------------------------------------------
# 4. PDF 生成函數 (繁體中文合規受控檔案)
# ---------------------------------------------------------
def generate_pdf(basic_info, quiz_result, survey_data, submit_time_str):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    font_path = "NotoSansTC-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font("NotoSansTC", "", font_path)
        pdf.set_font("NotoSansTC", size=11)
    else:
        pdf.set_font("Helvetica", size=11)

    # Header
    pdf.set_font_size(9)
    pdf.cell(0, 5, txt="Jumbo Orient Development Limited - IMS Controlled Record", ln=1, align="R")
    pdf.cell(0, 5, txt="Document ID: JO-HR-REC-2026-V1 | Confidential", ln=1, align="R")
    pdf.ln(3)

    # 標題
    pdf.set_font_size(16)
    pdf.cell(0, 10, txt="新員工入職培訓考核及問卷報告", ln=1, align="C")
    pdf.ln(5)
    
    # 個人基本資料 & 得分
    pdf.set_font_size(11)
    status_str = "合格 (PASS)" if quiz_result['is_pass'] else "不合格 (FAIL)"
    pdf.cell(0, 7, txt=f"姓名：{basic_info['name']}", ln=1)
    pdf.cell(0, 7, txt=f"職員編號：{basic_info['emp_id']}", ln=1)
    pdf.cell(0, 7, txt=f"組別：{basic_info['dept']}", ln=1)
    pdf.cell(0, 7, txt=f"考核時間：{submit_time_str}", ln=1)
    pdf.cell(0, 7, txt=f"測驗得分：{quiz_result['score']} / {quiz_result['total']} ({quiz_result['pass_rate']:.1f}%) - {status_str}", ln=1)
    pdf.ln(4)

    # 一、基本培訓評估問題
    pdf.set_font_size(12)
    pdf.cell(0, 8, txt="一、基本培訓評估問題", ln=1)
    pdf.set_font_size(10)
    pdf.cell(0, 6, txt=f"1. 培訓整體滿意度：{survey_data.get('s1_q1', '')} / 5", ln=1)
    pdf.cell(0, 6, txt=f"2. 培訓內容符合期望：{survey_data.get('s1_q2', '')} / 5", ln=1)
    pdf.cell(0, 6, txt=f"3. 培訓師表現：{survey_data.get('s1_q3', '')} / 5", ln=1)
    print_safe_text(pdf, f"4. 需要改進或增補內容：{survey_data.get('s1_q4', '無')}")
    pdf.ln(3)

    # 二、個人興趣及公司活動
    pdf.set_font_size(12)
    pdf.cell(0, 8, txt="二、個人興趣及公司活動", ln=1)
    pdf.set_font_size(10)
    pdf.cell(0, 6, txt=f"1. 運動活動興趣：{survey_data.get('s2_q1', '')} / 5", ln=1)
    sports_str = ", ".join(survey_data.get('s2_q2', []))
    if survey_data.get('s2_q2_other'): sports_str += f" ({survey_data.get('s2_q2_other')})"
    print_safe_text(pdf, f"2. 運動愛好：{sports_str if sports_str else '無'}")
    pdf.cell(0, 6, txt=f"3. 義工活動意願：{survey_data.get('s2_q3', '')} / 5", ln=1)
    vol_str = ", ".join(survey_data.get('s2_q4', []))
    if survey_data.get('s2_q4_other'): vol_str += f" ({survey_data.get('s2_q4_other')})"
    print_safe_text(pdf, f"4. 公益活動興趣：{vol_str if vol_str else '無'}")
    pdf.cell(0, 6, txt=f"5. 協助籌辦活動興趣：{survey_data.get('s2_q5', '')} / 5", ln=1)
    print_safe_text(pdf, f"6. 工作與生活平衡看法：{survey_data.get('s2_q6', '無')}")
    print_safe_text(pdf, f"7. 未來公司活動建議：{survey_data.get('s2_q7', '無')}")
    pdf.ln(3)

    # 三、開放式問題
    pdf.set_font_size(12)
    pdf.cell(0, 8, txt="三、開放式問題", ln=1)
    pdf.set_font_size(10)
    print_safe_text(pdf, f"1. 對公司文化的看法：{survey_data.get('s3_q1', '無')}")
    print_safe_text(pdf, f"2. 公司優勢與改進建議：{survey_data.get('s3_q2', '無')}")
    print_safe_text(pdf, f"3. 希望獲得的額外支持/資源：{survey_data.get('s3_q3', '無')}")
    print_safe_text(pdf, f"4. 對公司未來發展方向的建議：{survey_data.get('s3_q4', '無')}")
    print_safe_text(pdf, f"5. 其他建議或意見：{survey_data.get('s3_q5', '無')}")
    pdf.ln(5)

    pdf.set_font_size(8)
    print_safe_text(pdf, "聲明：本文件為內部培訓紀錄，由員工本人確認填答。個人資料僅供內部人力資源管理用途。", max_chars=45)

    return bytes(pdf.output())

# ---------------------------------------------------------
# 5. 後端自動寄送電郵函數 (Python SMTP)
# ---------------------------------------------------------
def send_email_direct(b_info, q_res, status_str, pdf_bytes):
    smtp_server = st.secrets.get("SMTP_SERVER", "smtp.office365.com")
    smtp_port = int(st.secrets.get("SMTP_PORT", 587))
    sender_email = st.secrets.get("SENDER_EMAIL", "hrd@jumboorient.com.hk")
    sender_password = st.secrets.get("SENDER_PASSWORD", "")
    receiver_email = st.secrets.get("HR_RECEIVER", "hrd@jumboorient.com.hk")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"【入職培訓結果】{b_info['dept']} - {b_info['name']} ({b_info['emp_id']})"

    body = f"""Dear HR,

員工已透過系統完成新員工入職培訓考核與意見調查，詳情如下：
• 姓名：{b_info['name']}
• 職員編號：{b_info['emp_id']}
• 組別：{b_info['dept']}
• 測驗得分：{q_res['score']} / {q_res['total']} ({status_str})
• 提交時間：{st.session_state.quiz_data.get('submit_time', '')}

PDF 完整考核報告檔案已作為附件隨信附上。"""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 加入 PDF 附件
    filename = f"入職培訓紀錄_{b_info['name']}.pdf"
    part = MIMEApplication(pdf_bytes, Name=filename)
    part['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(part)

    # 透過 SMTP 發送
    with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# =========================================================
# 第一部分：新員工入職培訓測驗
# =========================================================
if st.session_state.step == 1:
    st.title("📝 東淦新員工入職培訓考核及問卷系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    st.subheader("第一部分：新員工入職培訓測驗")
    
    with st.form("step1_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("姓名 *")
        with col2:
            emp_id = st.text_input("職員編號 *")
        with col3:
            dept = st.selectbox("組別 *", DEPT_OPTIONS)
            
        st.divider()
        user_answers = {}
        
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

        st.divider()
        declaration = st.checkbox("本人確認上述資料正確，並由本人獨立完成測驗。 *")

        submit_step1 = st.form_submit_button("提交測驗並檢視得分 ➔")

    if submit_step1:
        if not name or not emp_id or dept == "請選擇組別":
            st.warning("請先完整填寫姓名、職員編號並選擇組別！")
        elif not declaration:
            st.warning("請先勾選個人確認聲明方可提交！")
        else:
            score = 0
            total_items = 20
            for q in questions:
                user_ans = user_answers[q["id"]]
                correct_ans = q["answer"] if "answer" in q else None
                if q["type"] == "single":
                    if [user_ans] == correct_ans: score += 1
                elif q["type"] == "multiple":
                    for option in user_ans:
                        if option in correct_ans: score += 1
                elif q["type"] == "group_single":
                    for sub_q in q["sub_questions"]:
                        if user_ans[sub_q["sub_id"]] == sub_q["answer"]: score += 1

            pass_rate = (score / total_items) * 100
            is_pass = score >= 15
            
            hk_tz = timezone(timedelta(hours=8))
            now_hk = datetime.now(hk_tz)
            submit_time_str = now_hk.strftime("%Y-%m-%d %H:%M:%S")

            st.session_state.quiz_data = {
                "basic_info": {"name": name, "emp_id": emp_id, "dept": dept},
                "quiz_result": {"score": score, "total": total_items, "pass_rate": pass_rate, "is_pass": is_pass},
                "submit_time": submit_time_str
            }
            st.session_state.step = 2
            st.rerun()

# =========================================================
# 第二部分：培訓滿意度問卷與員工興趣調查
# =========================================================
elif st.session_state.step == 2:
    q_res = st.session_state.quiz_data["quiz_result"]
    b_info = st.session_state.quiz_data["basic_info"]
    
    st.title("📊 第二部分：測驗得分結果與問卷調查")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    
    st.info(f"👤 員工：{b_info['name']} ({b_info['emp_id']}) | 組別：{b_info['dept']}")
    st.success(f"🎯 測驗得分：{q_res['score']} / {q_res['total']}（合格率：{q_res['pass_rate']:.1f}%）")
    if q_res['is_pass']:
        st.balloons()
        st.success("🎉 恭喜通過入職培訓考核！")
    else:
        st.error("⚠️ 未達 15 分 (75%) 合格標準。")
        
    st.divider()
    st.subheader("請繼續完成以下意見調查，完成後即可生成 PDF 及發送結果：")
    
    with st.form("step2_form"):
        st.markdown("### 一、基本培訓評估問題")
        st.caption("請根據您的感受，對以下項目打分（1分 = 非常不同意，5分 = 非常同意）")
        s1_q1 = st.select_slider("1. 我對本次培訓的整體滿意度。*", options=[1, 2, 3, 4, 5], value=5)
        s1_q2 = st.select_slider("2. 培訓內容符合您的期望。*", options=[1, 2, 3, 4, 5], value=5)
        s1_q3 = st.select_slider("3. 培訓師的表現好。*", options=[1, 2, 3, 4, 5], value=5)
        s1_q4 = st.text_area("4. 有哪些內容您認為需要改進或增補？")

        st.markdown("### 二、個人興趣及公司活動")
        st.caption("請根據您的感受，對以下項目打分（1分 = 非常不同意，5分 = 非常同意）")
        s2_q1 = st.select_slider("1. 您對參加運動活動十分感興趣。*", options=[1, 2, 3, 4, 5], value=3)
        s2_q2 = st.multiselect("2. 您有哪些運動愛好？ (多選)", ["足球", "籃球", "游泳", "跑步", "單車", "羽毛球", "龍舟", "瑜伽", "沒有運動習慣"])
        s2_q2_other = st.text_input("2. 運動愛好 (其他說明)：")
        s2_q3 = st.select_slider("3. 您願意參加公司舉辦的義工活動。*", options=[1, 2, 3, 4, 5], value=3)
        s2_q4 = st.multiselect("4. 您希望參加的公益活動有什麼？ (多選)", ["環保活動", "社區服務", "教育支援", "健康推廣活動", "慈善募捐", "動物保護", "文化交流", "沒有"])
        s2_q4_other = st.text_input("4. 公益活動 (其他說明)：")
        s2_q5 = st.select_slider("5. 您有興趣協助公司籌辦活動。*", options=[1, 2, 3, 4, 5], value=3)
        s2_q6 = st.text_area("6. 您對於工作與生活平衡的看法是什麼？")
        s2_q7 = st.text_area("7. 您對於未來公司活動有什麼建議？")

        st.markdown("### 三、開放式問題")
        s3_q1 = st.text_area("1. 您對於公司文化的看法是什麼？")
        s3_q2 = st.text_area("2. 您認為公司有哪些優勢，哪些方面需要改進？")
        s3_q3 = st.text_area("3. 您希望在公司能夠獲得哪些額外的支持或資源？")
        s3_q4 = st.text_area("4. 您對於公司未來的發展方向有什麼建議？")
        s3_q5 = st.text_area("5. 其他建議或意見？")

        submit_step2 = st.form_submit_button("完成問卷並進入送出頁面 ➔")

    if submit_step2:
        st.session_state.survey_data = {
            "s1_q1": s1_q1, "s1_q2": s1_q2, "s1_q3": s1_q3, "s1_q4": s1_q4,
            "s2_q1": s2_q1, "s2_q2": s2_q2, "s2_q2_other": s2_q2_other,
            "s2_q3": s2_q3, "s2_q4": s2_q4, "s2_q4_other": s2_q4_other,
            "s2_q5": s2_q5, "s2_q6": s2_q6, "s2_q7": s2_q7,
            "s3_q1": s3_q1, "s3_q2": s3_q2, "s3_q3": s3_q3, "s3_q4": s3_q4, "s3_q5": s3_q5
        }
        st.session_state.step = 3
        st.session_state.email_sent = False
        st.rerun()

# =========================================================
# 第三部分：一鍵發送與報告下載
# =========================================================
elif st.session_state.step == 3:
    b_info = st.session_state.quiz_data["basic_info"]
    q_res = st.session_state.quiz_data["quiz_result"]
    s_data = st.session_state.survey_data
    sub_time = st.session_state.quiz_data.get("submit_time", "")
    
    status_str = "合格 (PASS)" if q_res["is_pass"] else "不合格 (FAIL)"
    
    st.title("🎉 第三部分：考核與問卷完成！")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    st.subheader(f"成績摘要：{q_res['score']} / {q_res['total']}（{status_str}）")
    
    pdf_bytes = generate_pdf(b_info, q_res, s_data, sub_time)
    
    st.divider()
    st.subheader("📤 第一步：一鍵提交報告至 HR")
    
    if not st.session_state.email_sent:
        if st.button("🚀 點此一鍵自動送出報告至 HR 電郵 (自動附加 PDF 報告)", type="primary", use_container_width=True):
            with st.spinner("系統正在自動打包 PDF 並寄出至 hrd@jumboorient.com.hk ..."):
                try:
                    send_email_direct(b_info, q_res, status_str, pdf_bytes)
                    st.session_state.email_sent = True
                    st.success("🎉 提交成功！考核與問卷報告已直接發送至 HR 電郵 (hrd@jumboorient.com.hk)。")
                    st.balloons()
                except Exception as e:
                    st.error(f"⚠️ 自動發送失敗，請點選下方按鈕手動下載或寄送。錯誤資訊：{e}")
    else:
        st.success("✅ 報告已成功寄送至 HR 電郵！")

    st.divider()
    st.subheader("📥 備份與手動下載 (選填)")
    st.download_button(
        label=f"💾 下載「入職培訓紀錄_{b_info['name']}.pdf」自行存檔",
        data=pdf_bytes,
        file_name=f"入職培訓紀錄_{b_info['name']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    with st.expander("💬 備用提交方式 (WhatsApp 或手動寄信)"):
        wa_phone = "85295423912"
        wa_msg = f"Dear HR,\n我是 {b_info['dept']} 的 {b_info['name']} ({b_info['emp_id']})。我已完成新員工入職培訓問卷考核（得分：{q_res['score']}/{q_res['total']}，{status_str}）。"
        wa_url = f"https://wa.me/{wa_phone}?text={urllib.parse.quote(wa_msg)}"
        st.markdown(
            f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
            f'<button style="background-color:#25D366; color:white; padding:10px 16px; border:none; border-radius:6px; font-size:14px; font-weight:bold; cursor:pointer; width:100%; margin-top:8px;">'
            f'💬 透過 WhatsApp 通知 HR (9542 3912)'
            f'</button></a>',
            unsafe_allow_html=True
        )

    st.write("")
    if st.button("🔄 重新填寫問卷"):
        st.session_state.step = 1
        st.session_state.quiz_data = {}
        st.session_state.email_sent = False
        st.rerun()
