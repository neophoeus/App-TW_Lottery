# App-TW_Lottery v2.0 (台灣彩券 AI 預測 / Taiwan Lottery AI Predictor)

![App-TW_Lottery Banner](frontend/public/favicon.ico)

A highly advanced, AI-powered prediction tool for Taiwan Lotteries including **Power Lottery (威力彩)**, **Lotto 6/49 (大樂透)**, and **Daily Cash (今彩539)**. The application scrapes the latest historical data and uses multiple machine learning strategies to calculate the most probable winning combinations.

這是一款採用多種演算法與 AI 模型開發的「台灣彩券預測工具」，支援**威力彩**、**大樂透**與**今彩539**。系統會自動抓取最新歷史開獎資料，並透過機器學習（如 LSTM、馬可夫鏈等）計算最有潛力的號碼組合。

> [!IMPORTANT]
> ### ⚡ 簡易免安裝版 (解壓縮即用) 快速通道
> **不懂 Git、npm 或 Node.js？只要跟著以下步驟即可立刻執行：**
> 1. 下載並解壓縮 **[App-TW_Lottery_Portable.zip](./App-TW_Lottery_Portable.zip)** 壓縮檔。
> 2. 確保您的 Windows 電腦安裝了 **[Python 3.10+](https://www.python.org/downloads/)**（安裝時請務必勾選 `Add Python to PATH`）。
> 3. 雙擊執行目錄底下的 **`run.bat`**。
> 4. 系統會自動初始化 AI 必要套件，並於啟動完成後**自動為您彈出瀏覽器網頁** (`http://localhost:8000`)！

---

## 🌟 Features (功能特色)

- **自動抓取最新數據 (Auto-Scraping):** The backend automatically updates the historical data CSV files to include the latest draws. / 後端能透過 `start.bat` 一鍵自動抓取最新的開獎資料。
- **多模型策略預測 (Multi-Model Strategies):**
  - **熱門分析 (Hot numbers):** Based on frequency. / 取出歷史上最常開出的數字。
  - **平衡策略 (Balanced):** Ensures a mix of odd/even and high/low numbers. / 確保單雙號、大小號的比例均衡。
  - **馬可夫鏈 (Markov Chain):** Predicts the next states based on transition probabilities of past draws. / 根據歷屆號碼出現的機率轉移矩陣預測下一期。
  - **圖形模式 (Pattern Strategy):** Analyzes historical intervals. / 分析號碼出現的規律。
  - **深度學習 LSTM (Long Short-Term Memory):** A neural network model trained on past sequences. / 使用神經網路訓練歷屆資料序列。
- **綜合「冠軍推薦」 (Ensemble Top Pick):** Casts a weighted vote across all strategies to find the ultimate golden combination. / 統計上述所有策略的預測結果，以權重投票選出共識最高的「黃金組合」。
- **現代化介面 (Modern UI):** Built with Next.js, React, and Tailwind CSS for a premium and stunning dashboard experience. / 以 Next.js 打造流暢且極具質感的動態介面。

---

## 🛠️ Tech Stack (技術架構)

### Backend (後端)

- **Python 3 / FastAPI**
- Pandas & BeautifulSoup4 (Crawling & Data Processing / 網頁爬蟲與資料處理)
- Scikit-learn & TensorFlow (Machine Learning & LSTM / 機器學習)
- Uvicorn (ASGI Server)

### Frontend (前端)

- **Next.js (React)**
- TypeScript
- Tailwind CSS
- Lucide React (Icons)

---

## 🚀 How to Run (如何啟動)

### Prerequisites (環境需求)

- **Node.js**: `v18+` (For Frontend)
- **Python**: `3.10+` (For Backend)

### Getting Started (快速啟動)

The project includes batch files optimized for both developers and regular users.
專案內建了適用於不同需求的 Windows 快捷啟動腳本。

#### 1. 簡易免安裝版 (Portable Version - Recommended for Users)
**不需要安裝 Node.js / npm，只要安裝 Python 即可使用！**
1. 確保您的電腦已安裝 **Python 3.10+**（安裝時請勾選 `Add Python to PATH`）。
2. 按兩下執行根目錄的 **`run.bat`**。
3. 腳本會自動建立虛擬環境、下載後端 AI 套件，並在啟動成功後**自動為您開啟瀏覽器**訪問 `http://localhost:8000`。

#### 2. 開發調試版 (Development Version - For Developers)
1. 確保已安裝 **Node.js** 與 **Python**。
2. 按兩下執行根目錄的 **`start.bat`**。
3. 腳本會同時啟動後端 API (Port 8000) 與前端 Next.js 開發伺服器，並開啟 `http://localhost:3000`。

> **Note:** The backend might take a few seconds to wake up the AI models (especially TensorFlow). The UI will display a loading status and smoothly retry until the API is fully ready.
>
> **注意：** 後端載入 TensorFlow 等 AI 模型需要幾秒鐘的時間，前端介面會顯示「喚醒 AI 引擎中...」並自動重試，請耐心等待。

### Manual Setup (手動啟動)

If you prefer to run them separately:
如果您想手動分別啟動：

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Data Maintenance (資料維護)

- **Manual Data Update (手動更新資料):** Click "更新資料" (Update Data) on the UI to trigger the web scraper. 點擊介面上的「更新資料」，系統會連線爬蟲抓取最新的開獎號碼。
- **Retraining the LSTM Model (重新訓練神經網路):** Run `retrain.bat` in the root folder to completely retrain the TensorFlow sequence models for all games. 使用根目錄的 `retrain.bat` 可以重新訓練所有的神經網路模型（會花費較多時間）。
- **Packing Portable Release (打包免安裝版):** Run `build_static.bat` to automatically build the frontend and move static assets to `backend/static/`. Then you can simply compress the `backend/` folder (including `static/` and `models/`), `run.bat`, and `README.md` into a ZIP file for distribution. 執行 `build_static.bat` 可自動將前端網頁編譯並複製至 `backend/static/` 目錄。之後您只需將 `backend/` 目錄、`run.bat` 與 `README.md` 壓縮為 ZIP 檔即可發佈分享給使用者。

---

## ⚠️ Disclaimer (免責聲明)

This tool is strictly for educational, research, and entertainment purposes. It does not guarantee winning any lotteries. Please play responsibly and within your means.

本工具開發僅供學術研究、程式交流與娛樂參考，**不代表或保證任何中獎機率**。彩券投資具有風險，請理性購買，量力而為。

---

## 🔧 IDE Integration & Testing (IDE 整合與測試)

This project has been updated for **Antigravity IDE** compatibility, including root workspace configurations, recommended extensions, and index exclusion lists (`.antigravityignore` / `.geminiignore`) to skip massive node modules and python environment structures.

本專案已更新以支援 **Antigravity IDE** 環境整合，包括根工作區設定、推薦擴充套件，以及排除清單（`.antigravityignore` 與 `.geminiignore`）以避免大型依賴與虛擬環境夾影響效能。

### Backend Testing (後端單元測試)

We use **`pytest`** for backend logic validation. The test suite covers data scrapers, dataset loaders, lottery prediction models, and ensembles.

我們使用 **`pytest`** 來驗證後端邏輯。測試套件涵蓋了資料爬蟲、資料集載入、彩券預測模型及綜合演算法。

To run tests / 執行測試：
```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt   # If pytest is not installed yet
pytest
```

---

© 2026 TW Lottery AI
