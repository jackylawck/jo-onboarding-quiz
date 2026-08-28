# 📝 東淦新員工入職培訓考核及問卷系統 (jo-onboard-quiz)

An Automated Enterprise Onboarding Assessment & Employee Feedback Web System for Jumbo Orient.  
專為東淦工程有限公司 (Jumbo Orient Development Limited) 打造之新員工入職培訓考核、滿意度調查、受控 PDF 報告生成與後端自動化電郵提交系統。

---

## 🌐 項目簡介 / System Overview

**jo-onboard-quiz** 是一個基於 Streamlit 開發的獨立企業級 Web 系統。系統整合了「入職培訓考核測驗」、「培訓滿意度評估」及「員工興趣調查」，並能即時繪製生成受控繁體中文 PDF 報告 (`JO-HR-REC-2026-V1`)。員工完成後只需一鍵點擊，後端即透過 Python SMTP 自動將報告及 PDF 附件直接寄送至 HR 部門 (`hrd@jumboorient.com.hk`)，實現完全無紙化與自動化管理。

---

## 🛠️ 核心特色 / Key Features

* **全自動一鍵後端提交 (One-Click Automated Email Submission via SMTP)**
  * 員工完成測驗與問卷後，點擊按鈕即可由後端自動打包 PDF 報告並直接以電郵發送至 HR，無需開啟任何外部郵件軟體或手動拖曳附件。
* **機密題庫後端隔離保護 (Secure Secrets Management)**
  * 題目、正確答案及敏感驗證金鑰完全儲存於 Streamlit Secrets 後端，前端不暴露任何題庫代碼與評分邏輯。
* **即時自動評分機制 (Real-time Automated Grading)**
  * 支援單選、多選及條款配對題，提交後即時計算得分與 75% 合格率狀態（15/20 分判定 PASS/FAIL）。
* **合規受控 PDF 報告生成 (Compliant IMS Controlled PDF)**
  * 自動擷取香港標準時間 (UTC+8)，將個人資料、答題成績、滿意度分數及開放式建議整合繪製成標準向量 PDF 文件 (`JO-HR-REC-2026-V1`)。
* **跨平台響應式體驗 (Responsive Mobile & Desktop Friendly)**
  * 適應寫字樓電腦螢幕與手機流動端操作，問卷滑塊、多選框與版面自動對齊。

---

## 🚀 系統流程 / Application Workflow

```text
[員工通行碼登入] ➔ [第一部分：入職培訓測驗] ➔ [第二部分：問卷及興趣調查] ➔ [第三部分：一鍵發送至 HR & 下載 PDF]

```

1. **登入驗證 (Access Verification)**
* 輸入員工通行碼進入系統。


2. **第一部分：入職培訓測驗 (Part I: Onboarding Quiz)**
* 填寫姓名、職員編號、選擇組別，完成規章制度與品質目標測驗並勾選誠信聲明。


3. **第二部分：問卷及興趣調查 (Part II: Feedback & Engagement Survey)**
* 檢視測驗即時得分（達標 15 分合格），填寫 1–5 分培訓滿意度評估、運動/義工愛好及開放式建議。


4. **第三部分：一鍵提交與備份 (Part III: Submit & Archiving)**
* 點擊 **「🚀 點此一鍵自動送出報告至 HR 電郵」**，後端即時打包 PDF 報告並寄送給 HRD。
* 提供 **「💾 下載 PDF 報告」** 供員工自行備份，並附有 WhatsApp 備用通訊管道。



---

## ⚙️ Secrets 設定規範 / Configuration (`.streamlit/secrets.toml`)

```toml
# 1. 員工通行碼 (自訂內部驗證密鑰)
ACCESS_CODE = "your_company_passcode"

# 2. HR 接收電郵
HR_RECEIVER = "hrd@jumboorient.com.hk"

# 3. 郵件伺服器與寄件帳號設定 (M365 SMTP)
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_sender_account@jumboorient.com.hk"
SENDER_PASSWORD = "your_smtp_app_password"

# 4. 完整題庫 JSON (字串格式)
QUESTIONS_JSON = '''[ ...題庫內容... ]'''

```

---

## 📄 文件與數據規範 / Document Standards

* **管控編號 (Document ID)**: `JO-HR-REC-2026-V1`
* **收件對象 (HR Email)**: `hrd@jumboorient.com.hk`
* **合規標準 (Compliance)**: Integrated Management System (ISO 9001 / ISO 14001 / ISO 45001) Controlled Records


