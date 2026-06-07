"""SQLite 資料庫：文章、段落、單字、字幕、筆記、複習紀錄。"""
from __future__ import annotations

import json
import logging
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

from toeic800 import config

logger = logging.getLogger(__name__)
from toeic800.utils.zh_tw import ensure_zh_tw, normalize_article_zh, normalize_vocab_row

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    title_zh TEXT,
    summary_en TEXT,
    summary_zh TEXT,
    week_label TEXT NOT NULL,
    published_at TEXT,
    fetched_at TEXT DEFAULT (datetime('now')),
    has_video INTEGER DEFAULT 0,
    video_url TEXT,
    video_embed_html TEXT,
    thumbnail_url TEXT
);

CREATE TABLE IF NOT EXISTS paragraphs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    order_idx INTEGER NOT NULL,
    text_en TEXT NOT NULL,
    text_zh TEXT,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    pos TEXT,
    meaning_zh TEXT,
    meaning_en TEXT,
    phonetic TEXT,
    example_en TEXT,
    example_zh TEXT,
    audio_path TEXT,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    start_sec REAL,
    end_sec REAL,
    text_en TEXT NOT NULL,
    text_zh TEXT,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER,
    vocab_id INTEGER,
    note_text TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE SET NULL,
    FOREIGN KEY (vocab_id) REFERENCES vocabulary(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS review_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vocab_id INTEGER NOT NULL,
    mastery INTEGER DEFAULT 0,
    reviewed_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (vocab_id) REFERENCES vocabulary(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS grammar_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    pattern TEXT NOT NULL,
    meaning_zh TEXT,
    example_ja TEXT,
    example_zh TEXT,
    jlpt_level TEXT,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quiz_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    options_json TEXT NOT NULL,
    answer TEXT NOT NULL,
    qtype TEXT DEFAULT 'vocab',
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_articles_week ON articles(week_label);
CREATE INDEX IF NOT EXISTS idx_vocab_article ON vocabulary(article_id);
CREATE INDEX IF NOT EXISTS idx_notes_article ON user_notes(article_id);
"""


class ToeicDatabase:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path or config.DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._maybe_copy_seed()
        self._init_schema()

    def _maybe_copy_seed(self) -> None:
        """若主 DB 不存在但 repo 內有 seed，複製後所有人可立即載入。"""
        if self.path.exists():
            return
        seed = config.DB_SEED_PATH
        if seed.is_file():
            shutil.copy2(seed, self.path)
            logger.info("已從 seed 複製資料庫：%s → %s", seed, self.path)

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)
            self._migrate(conn)

    def _migrate(self, conn: sqlite3.Connection) -> None:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(articles)")}
        if "track" not in cols:
            conn.execute(
                "ALTER TABLE articles ADD COLUMN track TEXT DEFAULT 'toeic'"
            )
        if "jlpt_level" not in cols:
            conn.execute("ALTER TABLE articles ADD COLUMN jlpt_level TEXT")
        if "audio_url" not in cols:
            conn.execute("ALTER TABLE articles ADD COLUMN audio_url TEXT")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_articles_track ON articles(track)"
        )
        vcols = {r[1] for r in conn.execute("PRAGMA table_info(vocabulary)")}
        for col, ddl in (
            ("study_status", "ALTER TABLE vocabulary ADD COLUMN study_status TEXT DEFAULT 'auto'"),
            ("dict_source", "ALTER TABLE vocabulary ADD COLUMN dict_source TEXT"),
            ("dict_url", "ALTER TABLE vocabulary ADD COLUMN dict_url TEXT"),
        ):
            if col not in vcols:
                conn.execute(ddl)
                vcols.add(col)

    def week_label(self, dt: datetime | None = None) -> str:
        dt = dt or datetime.now()
        iso = dt.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"

    def article_exists(self, url: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM articles WHERE url = ?", (url,)
            ).fetchone()
        return row is not None

    def has_weekly_article(
        self, track: str, week_label: str, jlpt_level: str | None = None
    ) -> bool:
        sql = "SELECT 1 FROM articles WHERE track = ? AND week_label = ?"
        params: list[Any] = [track, week_label]
        if jlpt_level:
            sql += " AND jlpt_level = ?"
            params.append(jlpt_level)
        with self.connect() as conn:
            row = conn.execute(sql, params).fetchone()
        return row is not None

    def save_article_bundle(self, bundle: dict[str, Any]) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO articles (
                    source, url, title, title_zh, summary_en, summary_zh,
                    week_label, published_at, has_video, video_url,
                    video_embed_html, thumbnail_url, track, jlpt_level, audio_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    title_zh=excluded.title_zh,
                    summary_en=excluded.summary_en,
                    summary_zh=excluded.summary_zh,
                    fetched_at=datetime('now'),
                    has_video=excluded.has_video,
                    video_url=excluded.video_url,
                    video_embed_html=excluded.video_embed_html,
                    thumbnail_url=excluded.thumbnail_url,
                    track=excluded.track,
                    jlpt_level=excluded.jlpt_level,
                    audio_url=excluded.audio_url
                """,
                (
                    bundle["source"],
                    bundle["url"],
                    bundle["title"],
                    bundle.get("title_zh"),
                    bundle.get("summary_en"),
                    bundle.get("summary_zh"),
                    bundle["week_label"],
                    bundle.get("published_at"),
                    1 if bundle.get("has_video") else 0,
                    bundle.get("video_url"),
                    bundle.get("video_embed_html"),
                    bundle.get("thumbnail_url"),
                    bundle.get("track", "toeic"),
                    bundle.get("jlpt_level"),
                    bundle.get("audio_url"),
                ),
            )
            article_id = cur.lastrowid
            if article_id == 0:
                row = conn.execute(
                    "SELECT id FROM articles WHERE url = ?", (bundle["url"],)
                ).fetchone()
                article_id = int(row["id"])
                for tbl in (
                    "paragraphs",
                    "vocabulary",
                    "subtitles",
                    "grammar_points",
                    "quiz_items",
                ):
                    conn.execute(
                        f"DELETE FROM {tbl} WHERE article_id = ?", (article_id,)
                    )

            for i, para in enumerate(bundle.get("paragraphs", [])):
                conn.execute(
                    """
                    INSERT INTO paragraphs (article_id, order_idx, text_en, text_zh)
                    VALUES (?, ?, ?, ?)
                    """,
                    (article_id, i, para["en"], para.get("zh")),
                )

            for i, vocab in enumerate(bundle.get("vocabulary", [])):
                conn.execute(
                    """
                    INSERT INTO vocabulary (
                        article_id, word, pos, meaning_zh, meaning_en, phonetic,
                        example_en, example_zh, audio_path, sort_order,
                        study_status, dict_source, dict_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article_id,
                        vocab["word"],
                        vocab.get("pos"),
                        vocab.get("meaning_zh"),
                        vocab.get("meaning_en"),
                        vocab.get("phonetic"),
                        vocab.get("example_en"),
                        vocab.get("example_zh"),
                        vocab.get("audio_path"),
                        i,
                        vocab.get("study_status", "auto"),
                        vocab.get("dict_source"),
                        vocab.get("dict_url"),
                    ),
                )

            for i, sub in enumerate(bundle.get("subtitles", [])):
                conn.execute(
                    """
                    INSERT INTO subtitles (
                        article_id, start_sec, end_sec, text_en, text_zh, sort_order
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article_id,
                        sub.get("start_sec"),
                        sub.get("end_sec"),
                        sub["en"],
                        sub.get("zh"),
                        i,
                    ),
                )

            for i, gp in enumerate(bundle.get("grammar", [])):
                conn.execute(
                    """
                    INSERT INTO grammar_points (
                        article_id, pattern, meaning_zh, example_ja, example_zh,
                        jlpt_level, sort_order
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article_id,
                        gp["pattern"],
                        gp.get("meaning_zh"),
                        gp.get("example_ja"),
                        gp.get("example_zh"),
                        gp.get("jlpt_level"),
                        i,
                    ),
                )

            for i, q in enumerate(bundle.get("quiz", [])):
                conn.execute(
                    """
                    INSERT INTO quiz_items (
                        article_id, question, options_json, answer, qtype, sort_order
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article_id,
                        q["question"],
                        q["options_json"],
                        q["answer"],
                        q.get("qtype", "vocab"),
                        i,
                    ),
                )
        return int(article_id)

    def list_weeks(
        self, track: str | None = None, jlpt_level: str | None = None
    ) -> list[str]:
        sql = "SELECT DISTINCT week_label FROM articles WHERE 1=1"
        params: list[Any] = []
        if track:
            sql += " AND track = ?"
            params.append(track)
        if jlpt_level:
            sql += " AND jlpt_level = ?"
            params.append(jlpt_level)
        sql += " ORDER BY week_label DESC"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [r["week_label"] for r in rows]

    def list_articles(
        self,
        week_label: str | None = None,
        source: str | None = None,
        track: str | None = None,
        jlpt_level: str | None = None,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM articles WHERE 1=1"
        params: list[Any] = []
        if week_label:
            sql += " AND week_label = ?"
            params.append(week_label)
        if source:
            sql += " AND source LIKE ?"
            params.append(f"%{source}%")
        if track:
            sql += " AND track = ?"
            params.append(track)
        if jlpt_level:
            sql += " AND jlpt_level = ?"
            params.append(jlpt_level)
        sql += " ORDER BY published_at DESC, id DESC"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        out = [dict(r) for r in rows]
        for a in out:
            if a.get("title_zh"):
                a["title_zh"] = ensure_zh_tw(a["title_zh"])
            if a.get("summary_zh"):
                a["summary_zh"] = ensure_zh_tw(a["summary_zh"])
        return out

    def get_article(self, article_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM articles WHERE id = ?", (article_id,)
            ).fetchone()
            if not row:
                return None
            article = dict(row)
            article["paragraphs"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM paragraphs WHERE article_id = ? ORDER BY order_idx",
                    (article_id,),
                ).fetchall()
            ]
            article["vocabulary"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM vocabulary WHERE article_id = ? ORDER BY sort_order",
                    (article_id,),
                ).fetchall()
            ]
            article["subtitles"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM subtitles WHERE article_id = ? ORDER BY sort_order",
                    (article_id,),
                ).fetchall()
            ]
            article["grammar"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM grammar_points WHERE article_id = ? ORDER BY sort_order",
                    (article_id,),
                ).fetchall()
            ]
            article["quiz"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM quiz_items WHERE article_id = ? ORDER BY sort_order",
                    (article_id,),
                ).fetchall()
            ]
        return normalize_article_zh(article)

    def list_all_vocabulary(
        self,
        week_label: str | None = None,
        article_id: int | None = None,
        track: str | None = None,
        jlpt_level: str | None = None,
    ) -> list[dict[str, Any]]:
        sql = """
            SELECT v.*, a.title AS article_title, a.week_label, a.source,
                   a.jlpt_level, a.track
            FROM vocabulary v
            JOIN articles a ON a.id = v.article_id
            WHERE 1=1
        """
        params: list[Any] = []
        if week_label:
            sql += " AND a.week_label = ?"
            params.append(week_label)
        if article_id:
            sql += " AND v.article_id = ?"
            params.append(article_id)
        if track:
            sql += " AND a.track = ?"
            params.append(track)
        if jlpt_level:
            sql += " AND a.jlpt_level = ?"
            params.append(jlpt_level)
        sql += " ORDER BY a.week_label DESC, v.sort_order"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [normalize_vocab_row(dict(r)) for r in rows]

    def set_vocab_study_status(self, vocab_id: int, status: str) -> None:
        status = status if status in ("auto", "included", "excluded") else "auto"
        with self.connect() as conn:
            conn.execute(
                "UPDATE vocabulary SET study_status = ? WHERE id = ?",
                (status, vocab_id),
            )

    def update_vocab_entry(self, vocab_id: int, **fields: Any) -> None:
        allowed = {
            "word",
            "pos",
            "meaning_zh",
            "meaning_en",
            "phonetic",
            "example_en",
            "example_zh",
            "audio_path",
            "study_status",
            "dict_source",
            "dict_url",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        cols = ", ".join(f"{k} = ?" for k in updates)
        with self.connect() as conn:
            conn.execute(
                f"UPDATE vocabulary SET {cols} WHERE id = ?",
                (*updates.values(), vocab_id),
            )

    def article_has_vocab_word(self, article_id: int, word: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM vocabulary
                WHERE article_id = ? AND lower(word) = lower(?)
                """,
                (article_id, word),
            ).fetchone()
        return row is not None

    def add_vocab_entry(self, article_id: int, entry: dict[str, Any]) -> int:
        with self.connect() as conn:
            max_order = conn.execute(
                "SELECT COALESCE(MAX(sort_order), -1) FROM vocabulary WHERE article_id = ?",
                (article_id,),
            ).fetchone()[0]
            cur = conn.execute(
                """
                INSERT INTO vocabulary (
                    article_id, word, pos, meaning_zh, meaning_en, phonetic,
                    example_en, example_zh, audio_path, sort_order, study_status,
                    dict_source, dict_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article_id,
                    entry["word"],
                    entry.get("pos"),
                    entry.get("meaning_zh"),
                    entry.get("meaning_en"),
                    entry.get("phonetic"),
                    entry.get("example_en"),
                    entry.get("example_zh"),
                    entry.get("audio_path"),
                    int(max_order) + 1,
                    entry.get("study_status", "included"),
                    entry.get("dict_source"),
                    entry.get("dict_url"),
                ),
            )
            return int(cur.lastrowid)

    def add_note(
        self,
        note_text: str,
        article_id: int | None = None,
        vocab_id: int | None = None,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO user_notes (article_id, vocab_id, note_text)
                VALUES (?, ?, ?)
                """,
                (article_id, vocab_id, note_text),
            )
            return int(cur.lastrowid)

    def update_note(self, note_id: int, note_text: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE user_notes SET note_text = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (note_text, note_id),
            )

    def delete_note(self, note_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM user_notes WHERE id = ?", (note_id,))

    def list_notes(
        self, article_id: int | None = None, vocab_id: int | None = None
    ) -> list[dict[str, Any]]:
        sql = """
            SELECT n.*, a.title AS article_title, v.word AS vocab_word
            FROM user_notes n
            LEFT JOIN articles a ON a.id = n.article_id
            LEFT JOIN vocabulary v ON v.id = n.vocab_id
            WHERE 1=1
        """
        params: list[Any] = []
        if article_id:
            sql += " AND n.article_id = ?"
            params.append(article_id)
        if vocab_id:
            sql += " AND n.vocab_id = ?"
            params.append(vocab_id)
        sql += " ORDER BY n.updated_at DESC"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def log_review(self, vocab_id: int, mastery: int) -> None:
        mastery = max(0, min(5, mastery))
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO review_log (vocab_id, mastery) VALUES (?, ?)",
                (vocab_id, mastery),
            )

    def get_vocab_mastery(self, vocab_id: int) -> int:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT mastery FROM review_log
                WHERE vocab_id = ? ORDER BY reviewed_at DESC LIMIT 1
                """,
                (vocab_id,),
            ).fetchone()
        return int(row["mastery"]) if row else 0

    def review_queue(
        self, limit: int = 20, track: str | None = None, jlpt_level: str | None = None
    ) -> list[dict[str, Any]]:
        """優先複習尚未評分或掌握度較低的單字。"""
        sql = """
            SELECT v.*, a.title AS article_title, a.week_label, a.jlpt_level,
                   COALESCE(
                       (SELECT mastery FROM review_log rl
                        WHERE rl.vocab_id = v.id
                        ORDER BY rl.reviewed_at DESC LIMIT 1),
                       -1
                   ) AS last_mastery
            FROM vocabulary v
            JOIN articles a ON a.id = v.article_id
            WHERE 1=1
        """
        params: list[Any] = []
        if track:
            sql += " AND a.track = ?"
            params.append(track)
        if jlpt_level:
            sql += " AND a.jlpt_level = ?"
            params.append(jlpt_level)
        sql += " ORDER BY last_mastery ASC, a.week_label DESC, v.sort_order LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def stats(
        self, track: str | None = None, jlpt_level: str | None = None
    ) -> dict[str, int]:
        af = ""
        params: list[Any] = []
        if track:
            af += " AND a.track = ?"
            params.append(track)
        if jlpt_level:
            af += " AND a.jlpt_level = ?"
            params.append(jlpt_level)
        bf = af.replace("a.track", "track").replace("a.jlpt_level", "jlpt_level")
        with self.connect() as conn:
            articles = conn.execute(
                f"SELECT COUNT(*) c FROM articles WHERE 1=1{bf}", params
            ).fetchone()["c"]
            vocab = conn.execute(
                f"""
                SELECT COUNT(*) c FROM vocabulary v
                JOIN articles a ON a.id = v.article_id
                WHERE 1=1{af}
                """,
                params,
            ).fetchone()["c"]
            notes = conn.execute("SELECT COUNT(*) c FROM user_notes").fetchone()["c"]
            weeks = conn.execute(
                f"SELECT COUNT(DISTINCT week_label) c FROM articles WHERE 1=1{bf}",
                params,
            ).fetchone()["c"]
        return {"articles": articles, "vocabulary": vocab, "notes": notes, "weeks": weeks}
