# 🛡️ 系統安全、架構與法規合規宣告 (Security & Compliance Statement)

**管控編號 (Document ID)**: `JO-HR-DOC-2026-COMPLIANCE-V1`  
**適用標準**: ISO/IEC 27001:2022, ISO/IEC 42001:2023, ISO 9001:2015, HK PDPO (Cap. 486)

---

## 1. 法規適用性評估 (Regulatory Scope Assessment)

| 法規 / 標準名稱 | 適用性評估 | 合規措施落實 |
| :--- | :--- | :--- |
| **香港《個人資料（私隱）條例》(PDPO)** | **直接適用** | 明確提供 PICS 聲明、落實資料收集最小化原則、限定內部 HR 用途。 |
| **ISO/IEC 27001 (資訊安全管理)** | **直接適用** | 實施 Secrets 隔離管理、代碼無硬編碼金鑰、全鏈路 TLS 加密傳輸。 |
| **ISO 9001 / 14001 / 45001 (IMS)** | **直接適用** | 生成受控編號文件 (`JO-HR-REC-2026-V1`)，具備完整 HKT 時間戳與防偽版本號。 |
| **歐盟 AI 法案 (EU AI Act)** | **不適用 / 免責** | 本系統為確定性表單與自動計分程式，非高風險 AI 推論系統或生物識別系統。 |
| **ISO/IEC 42001 (AI 管理體系)** | **管治參照** | 確保自動化流程之透明度（Transparency）、可解釋性與人為最終監督機制。 |

---

## 2. 資安架構管控 (Security Architecture Controls)

1. **憑證與機密保護 (Secrets Isolation)**：
   * 郵件帳號、伺服器金鑰與題庫解答嚴格存放於 `st.secrets`，絕不進入 Git 版本控制。
2. **零信任前端防護 (Zero Trust Input Handling)**：
   * 採用動態 Session 比對與受控 URL 金鑰機制，杜絕未授權存取。
3. **無持久性快取 (Ephemeral Data Handling)**：
   * 評估報告於記憶體內動態合成，完成郵件遞送即自記憶體釋放，防止資料殘留。
