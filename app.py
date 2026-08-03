import streamlit as st
import json
import urllib.parse
from fpdf import FPDF
import os
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="東淦新員工入職培訓考核及問卷系統", page_icon="📝")

# ---------------------------------------------------------
# 1. 前端門禁驗證 (Access Code)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 東淦新員工入職培訓考核及問卷系統")
    st.markdown("🏢 [東淦工程有限公司 (Jumbo Orient) 官方網站](https://www.jumboorient.com.hk/)", unsafe_allow_html=True)
    st.write("")
    user_code = st.text_input("請輸入員工通行碼以開始測驗：", type="password")
    if st.button("確認"):
        if user_code == st.secrets.get("ACCESS_CODE", "jo1996"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("通行碼錯誤！請重新輸入或聯絡 HR。")
    st.stop()

# ---------------------------------------------------------
# 2. Session State 流程與狀態控管
# ---------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}

if "pdf_downloaded" not in st.session_state:
    st.session_state.pdf_downloaded = False

# ---------------------------------------------------------
# 3. 讀取測驗題庫
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

# ---------------------------------------------------------
# 4. PDF 生成函數
# ---------------------------------------------------------
def generate_pdf(basic_info, quiz_result, survey_data, submit_time_str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    font_path = "NotoSansTC-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font("NotoSansTC", "", font_path)
        pdf.set_font("NotoSansTC", size=11)
    else:
        pdf.set_font("Helvetica", size=11)

    # 文件 Header
    pdf.set_font_size(9)
    pdf.cell(190, 5, txt="Jumbo Orient Development Limited - IMS Controlled Record", ln=True, align="R")
    pdf.cell(190, 5, txt="Document ID: JO-HR-REC-2026-V1 | Confidential", ln=True, align="R")
    pdf.ln(3)

    # 標題
    pdf.set_font_size(16)
    pdf.cell(190, 10, txt="新員工入職培訓考核及問卷報告", ln=True, align="C")
    pdf.ln(5)
    
    # 個人基本資料、提交時間 & 測驗成績
    pdf.set_font_size(12)
    pdf.cell(190, 8, txt=f"姓名：{basic_info['name']}", ln=True)
    pdf.cell(190, 8, txt=f"職員編號：{basic_info['emp_id']}", ln=True)
    pdf.cell(190, 8, txt=f"組別：{basic_info['dept']}", ln=True)
    pdf.cell(190, 8, txt=f"考核/提交時間：{submit_time_str}", ln=True)
    pdf.cell(190, 8, txt=f"測驗得分：{quiz_result['score']} / {quiz_result['total']}", ln=True)
    pdf.cell(190, 8, txt=f"合格率：{quiz_result['pass_rate']:.1f}%", ln=True)
    status_str = "合格 (PASS)" if quiz_result['is_pass'] else "不合格 (FAIL)"
    pdf.cell(190, 8, txt=f"考核結果：{status_str}", ln=True)
    pdf.ln(5)

    # 一、基本培訓評估問題
    pdf.set_font_size(13)
    pdf.cell(190, 8, txt="一、基本培訓評估問題", ln=True)
    pdf.set_font_size(10)
    pdf.cell(190, 6, txt=f"1. 培訓整體滿意度：{survey_data.get('s1_q1', '')} / 5", ln=True)
    pdf.cell(190, 6, txt=f"2. 培訓內容符合期望：{survey_data.get('s1_q2', '')} / 5", ln=True)
    pdf.cell(190, 6, txt=f"3. 培訓師表現：{survey_data.get('s1_q3', '')} / 5", ln=True)
    pdf.multi_cell(190, 6, txt=f"4. 需要改進或增補內容：{clean_text(survey_data.get('s1_q4'))}")
    pdf.ln(3)

    # 二、個人興趣及公司活動
    pdf.set_font_size(13)
    pdf.cell(190, 8, txt="二、個人興趣及公司活動", ln=True)
    pdf.set_font_size(10)
    pdf.cell(190, 6, txt=f"1. 運動活動興趣：{survey_data.get('s2_q1', '')} / 5", ln=True)
    sports_str = ", ".join(survey_data.get('s2_q2', []))
    if survey_data.get('s2_q2_other'): sports_str += f" ({survey_data.get('s2_q2_other')})"
    pdf.multi_cell(190, 6, txt=f"2. 運動愛好：{clean_text(sports_str)}")
    pdf.cell(190, 6, txt=f"3. 義工活動意願：{survey_data.get('s2_q3', '')} / 5", ln=True)
    vol_str = ", ".join(survey_data.get('s2_q4', []))
    if survey_data.get('s2_q4_other'): vol_str += f" ({survey_data.get('s2_q4_other')})"
    pdf.multi_cell(190, 6, txt=f"4. 公益活動興趣：{clean_text(vol_str)}")
    pdf.cell(190, 6, txt=f"5. 協助籌辦活動興趣：{survey_data.get('s2_q5', '')} / 5", ln=True)
    pdf.multi_cell(190, 6, txt=f"6. 工作與生活平衡看法：{clean_text(survey_data.get('s2_q6'))}")
    pdf.multi_cell(190, 6, txt=f"7. 未來公司活動建議：{clean_text(survey_data.get('s2_q7'))}")
    pdf.ln(3)

    # 三、開放式問題
    pdf.set_font_size(13)
    pdf.cell(190, 8, txt="三、開放式問題", ln=True)
    pdf.set_font_size(10)
    pdf.multi_cell(190, 6, txt=f"1. 對公司文化的看法：{clean_text(survey_data.get('s3_q1'))}")
    pdf.multi_cell(190, 6, txt=f"2. 公司優勢與改進建議：{clean_text(survey_data.get('s3_q2'))}")
    pdf.multi_cell(190, 6, txt=f"3. 希望獲得的額外支持/資源：{clean_text(survey_data.get('s3_q3'))}")
    pdf.multi_cell(190, 6, txt=f"4. 對公司未來發展方向的建議：{clean_text(survey_data.get('s3_q4'))}")
    pdf.multi_cell(190, 6, txt=f"5. 其他建議或意見：{clean_text(survey_data.get('s3_q5'))}")
    pdf.ln(5)

    pdf.set_font_size(8)
    pdf.multi_cell(190, 4, txt="聲明：本文件為內部培訓紀錄，由員工本人確認填答。個人資料僅供內部人力資源管理用途。")

    return bytes(pdf.output())

def mark_as_downloaded():
    st.session_state.pdf_downloaded = True

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

        submit_step2 = st.form_submit_button("完成問卷並生成 PDF 報告 ➔")

    if submit_step2:
        st.session_state.survey_data = {
            "s1_q1": s1_q1, "s1_q2": s1_q2, "s1_q3": s1_q3, "s1_q4": s1_q4,
            "s2_q1": s2_q1, "s2_q2": s2_q2, "s2_q2_other": s2_q2_other,
            "s2_q3": s2_q3, "s2_q4": s2_q4, "s2_q4_other": s2_q4_other,
            "s2_q5": s2_q5, "s2_q6": s2_q6, "s2_q7": s2_q7,
            "s3_q1": s3_q1, "s3_q2": s3_q2, "s3_q3": s3_q3, "s3_q4": s3_q4, "s3_q5": s3_q5
        }
        st.session_state.step = 3
        st.rerun()

# =========================================================
# 第三部分：報告下載與發送
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
    
    # 動態生成 PDF 檔
    pdf_bytes = generate_pdf(b_info, q_res, s_data, sub_time)
    
    st.divider()
    st.subheader("📥 步驟 1：下載 PDF 報告檔 (必須先下載)")
    
    st.download_button(
        label=f"點此下載「入職培訓紀錄_{b_info['name']}.pdf」",
        data=pdf_bytes,
        file_name=f"入職培訓紀錄_{b_info['name']}.pdf",
        mime="application/pdf",
        on_click=mark_as_downloaded
    )
    
    st.divider()
    
    if not st.session_state.pdf_downloaded:
        st.warning("🔒 步驟 2 解鎖條件：請先點擊上方「步驟 1」按鈕下載 PDF 報告檔！")
    else:
        st.success("✅ 已順利下載 PDF 報告！請選擇下方提交方式發送給 HR：")
        st.subheader("步驟 2：選擇提交方式給 HR (電郵)")
        
        st.markdown("### ✉️ 透過 Email / Outlook 發送 (主要方式)")
        email_to = st.secrets.get("HR_EMAIL", "hrd@jumboorient.com.hk")
        email_subject = f"【入職培訓結果】{b_info['dept']} - {b_info['name']} ({b_info['emp_id']})"
        email_body = f"""Dear HR：

我是 {b_info['dept']} 的 {b_info['name']} ({b_info['emp_id']})。
我已於 {sub_time} 完成新員工入職培訓問卷考核及意見調查，結果如下：

• 姓名：{b_info['name']}
• 職員編號：{b_info['emp_id']}
• 組別：{b_info['dept']}
• 提交時間：{sub_time}
• 答對得分：{q_res['score']} / {q_res['total']}
• 合格率：{q_res['pass_rate']:.1f}%
• 考核結果：{status_str}

• 培訓整體滿意度：{s_data['s1_q1']} / 5
• 運動興趣：{s_data['s2_q1']} / 5
• 義工意願：{s_data['s2_q3']} / 5

（已下載並附上「入職培訓紀錄_{b_info['name']}.pdf」報告檔案）
"""
        mailto_url = f"mailto:{email_to}?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
        st.markdown(
            f'<a href="{mailto_url}" target="_blank" style="text-decoration:none;">'
            f'<button style="background-color:#0078D4; color:white; padding:12px 20px; border:none; border-radius:6px; font-size:16px; font-weight:bold; cursor:pointer; width:100%; margin-bottom:8px;">'
            f'📧 開啟 Outlook 寄至 hrd@jumboorient.com.hk'
            f'</button></a>',
            unsafe_allow_html=True
        )
        st.caption("⚠️ 提示：開啟 Outlook 後，請將步驟 1 下載的 PDF 報告檔案拖進郵件作為附件一同發送。")

        st.write("")
        st.write("")

        with st.expander("💬 如無法使用電郵，可點此展開透過 WhatsApp 發送給 HR"):
            st.markdown("#### 💬 方式 B：透過 WhatsApp 發送給 HR")
            wa_phone = "85295423912"
            wa_msg = f"""Dear HR,

我是 {b_info['dept']} 的 {b_info['name']} ({b_info['emp_id']})。
我已於 {sub_time} 完成新員工入職培訓問卷考核，成果如下：
• 得分：{q_res['score']} / {q_res['total']} ({status_str})
• 滿意度：{s_data['s1_q1']} / 5

（已下載 PDF 報告檔，隨後於此對話發送給您）"""
            wa_url = f"https://wa.me/{wa_phone}?text={urllib.parse.quote(wa_msg)}"
            st.markdown(
                f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
                f'<button style="background-color:#25D366; color:white; padding:12px 20px; border:none; border-radius:6px; font-size:15px; font-weight:bold; cursor:pointer; width:100%; margin-bottom:8px;">'
                f'💬 開啟 WhatsApp (9542 3912)'
                f'</button></a>',
                unsafe_allow_html=True
            )
            st.caption("⚠️ 提示：開啟 WhatsApp 對話後，請點擊加號/夾子圖示傳送剛下載的 PDF 報告。")

    st.write("")
    if st.button("🔄 重新填寫問卷"):
        st.session_state.step = 1
        st.session_state.quiz_data = {}
        st.session_state.pdf_downloaded = False
        st.rerun()
