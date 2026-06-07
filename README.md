# 多益800分 · 經濟英文週報

每週從 **BBC**、**CNN** 抓取經濟、股市、國際情勢報導，整理成中英對照閱讀、多益800級單字表（詞性、中文、英文解釋、例句、發音），並支援影片中英字幕、複習與筆記。

## 功能

- RSS 探索 BBC Business / World、CNN Money / World
- 正文擷取 + 段落級中英翻譯
- 多益800導向單字抽取（Free Dictionary API + 發音音檔）
- 影片嵌入與中英字幕（原生 transcript 或正文分段）
- SQLite 儲存：文章、單字、字幕、筆記、複習紀錄
- Streamlit 網站：閱讀、單字表、翻卡複習、筆記

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
