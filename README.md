# 📝 東淦新員工入職培訓考核及問卷系統 (jo-onboarding-quiz)

An Automated Enterprise Onboarding Assessment & Employee Feedback Web System for Jumbo Orient.  
專為東淦工程有限公司 (Jumbo Orient) 打造之新員工入職培訓考核、滿意度調查與數據導出系統。

---

## 🌐 項目簡介 / System Overview

**jo-onboarding-quiz** 是一個基於 Streamlit 開發的企業級入職培訓互動 Web 系統。系統整合了「入職培訓考核測驗」、「培訓滿意度評估」及「員工興趣調查」，並能即時繪製生成合規之 PDF 報告，協助 HR 高效完成新員工訓練驗收與 ESG/員工活動數據收集。

**jo-onboarding-quiz** is an enterprise onboarding assessment and feedback application developed for Jumbo Orient employees using Streamlit. Built to streamline HR training workflows, it combines knowledge quizzes, training satisfaction surveys, and corporate engagement data collection with automated, compliant PDF report generation.

---

## 🛠️ 核心特色 / Key Features

* **三階段引導式流程 (3-Step Guided Workflow)**
  * 採用 Session State 控管「第一部分：測驗 ➔ 第二部分：問卷調查 ➔ 第三部分：報告導出及發送」，確保流程嚴謹且易於操作。
  * Enforces a structured step-by-step submission flow to ensure assessment integrity and smooth user experience.

* **即時自動評分機制 (Real-time Automated Grading)**
  * 支援單選、多選及條款配對題，提交後即時計算得分與 75% 合格率狀態（例如 15/20 分判定 PASS/FAIL）。
  * Dynamically evaluates responses for single, multiple, and grouped sub-questions, instantly calculating score and pass status.

* **合規 PDF 報告生成 (Compliant PDF Report Generation)**
  * 自動擷取香港標準時間 (UTC+8)，將個人資料、答題成績、滿意度分數及開放式建議整合繪製成 PDF 文件 (`JO-HR-REC-2026-V1`)。
  * Automatically embeds local time stamps (HKT) and survey data into standard, printable PDF records for enterprise archiving.

* **快捷提交管道 (One-Click Email & WhatsApp Submission)**
  * 內建安全門禁機制，確保員工先下載 PDF 報告後解鎖發送按鈕；支援一鍵開啟 Outlook (`mailto:`) 及 WhatsApp 對話框，方便員工隨信附上附件。
  * Features a conditional download lock to ensure users save their PDF before launching pre-formatted Outlook or WhatsApp messaging links.

* **響應式跨平台支援 (Responsive Mobile-Friendly Design)**
  * 適應電腦寫字樓環境與手機觸控操作，問卷滑塊與多選框自動對齊，提升整體使用體驗。
  * Fully accessible on both desktop browsers and mobile devices with seamless touch controls.

---

## 🚀 系統流程 / Application Workflow

1. **第一部分：入職培訓測驗 (Part I: Onboarding Quiz)**
   * 輸入員工通行碼、姓名、職員編號及組別。
   * 完成 11 道規章制度與品質目標問題並勾選誠信聲明。
2. **第二部分：問卷及興趣調查 (Part II: Feedback & Engagement Survey)**
   * 檢視測驗得分，填寫 1–5 分滿意度量表、運動/義工愛好多選項及開放式建議。
3. **第三部分：下載與提交 (Part III: Download & Send)**
   * 點擊下載生成之 PDF 報告檔。
   * 點擊「開啟 Outlook」或展開「WhatsApp」一鍵將報告發送至 HR 部門 (`hrd@jumboorient.com.hk`)。

---

## 📄 文件與數據規範 / Document Standards

* **管控編號 (Document ID)**: `JO-HR-REC-2026-V1`
* **收件對象 (HR Email)**: `hrd@jumboorient.com.hk`
* **合規標準 (Compliance)**: Integrated Management System (ISO 9001 / 14001 / 45001) Controlled Records
