# 多益800分 · 經濟英文 + 日文 JLPT 週報

同一網站、側欄切換 **多益800** 與 **日文 N5–N1**。

## 日文模組（N5–N1）

每週各級各抓取 1 篇，來源分級參考 [免費日文新聞資源推薦](https://vocus.cc/article/6837b674fd8978000142bdb4)：

| 等級 | 來源 |
|------|------|
| N5 | NHKやさしいことばニュース |
| N4 | 毎日小学生新聞 |
| N3 | Yahoo!ニュース |
| N2 | NHKニュース |
| N1 | 朝日新聞·社説 |

功能：日中對照、單字（詞性/讀音/例句/發音）、文法、聽力、小考、單字 PDF、複習、筆記。

```bash
python main.py fetch-weekly-japanese   # N5–N1 各 1 篇
python main.py fetch-weekly-all          # 多益 + 日文
python main.py import-japanese --url "https://www3.nhk.or.jp/news/easy/..." --level N5
```

## 多益模組

每週 BBC / CNN 經濟、股市、國際新聞（見下方快速開始）。

## 快速開始

```bash
cd 多益800分專案
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 匯入示範 BBC 文章
python main.py import-url --url "https://www.bbc.com/news/articles/cwy2yq0dj58o" --source BBC

# 或每週自動抓取
python main.py fetch-weekly

# 啟動網站
python main.py serve
```

或雙擊 `啟動學習站.bat`。

## 每週排程

```powershell
schtasks /Create /TN "Toeic800Weekly" /TR "powershell -File scripts\weekly_task.ps1" /SC WEEKLY /D MON /ST 08:00
```

## 環境變數

複製 `.env.example` 為 `.env`：

| 變數 | 說明 |
|------|------|
| `OPENAI_API_KEY` | 選填，啟用後翻譯品質更佳 |
| `TRANSLATOR` | `google`（預設）或 `openai` |
| `WEEKLY_ARTICLE_LIMIT` | 每週抓取篇數，預設 6 |
| `VOCAB_PER_ARTICLE` | 每篇單字數，預設 15 |

## 單字表格式

對齊多益單字本風格：

| 單字 | 詞性 | 中文 | 英文解釋 | 例句（英） | 例句（中） | 音標 / 發音 |

## 資料庫

預設 `data/toeic800.db`，可在網站側欄「管理」手動抓取或匯入 URL。

## 備註

- 未找到您提到的 PDF 範本檔，目前單字卡採常見多益800欄位；若您上傳 PDF，可再對齊版面。
- BBC/CNN 影片若無公開 transcript，會以文章段落產生輔助中英字幕。

## 免責聲明與版權說明

本 App 為**非官方多益風格學習工具**，與 ETS／IIBC **無任何關係**。**TOEIC®** 為 ETS 註冊商標。

### TOEIC 擬真練習

每日練習題目為本專案**原創擬真練習**，僅參考 [IIBC 公開格式說明](https://www.iibc-global.org/english/toeic/test/lr/about/format.html)（Part 5–7 題型、主題類別），**非** ETS／IIBC 官方試題，亦**未**複製商業機構題庫或考古題原文。本 App **不提供**官方認證、成績換算或任何形式的官方背書。

### 新聞閱讀

BBC、CNN 等新聞內容之著作權屬原出版者。本 App 提供之連結、摘要與學習輔助功能，**不得**視為可任意重製、公開散播全文之授權。請優先至原文網站閱讀。

### 單字與例句

文章單字釋義與例句為學習輔助；**例句為原創撰寫**（非新聞原文摘錄）。英文朗讀採第三方 Neural TTS 合成，僅供學習聽力。

### 一般聲明

以上說明**不構成法律意見**。若計畫商業化或公開大量散播內容，請自行諮詢專業法律／智財顧問。
