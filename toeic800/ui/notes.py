"""筆記回顧。"""
from __future__ import annotations

import streamlit as st

from toeic800.db.database import ToeicDatabase


def render_notes_page(db: ToeicDatabase) -> None:
    notes = db.list_notes()
    if not notes:
        st.info("尚無筆記")
        return

    for n in notes:
        with st.expander(
            f"{n.get('vocab_word') or n.get('article_title') or '筆記'} · {n['updated_at'][:16]}"
        ):
            new_text = st.text_area("內容", value=n["note_text"], key=f"note_edit_{n['id']}")
            c1, c2 = st.columns(2)
            if c1.button("更新", key=f"upd_{n['id']}"):
                db.update_note(n["id"], new_text.strip())
                st.success("已更新")
                st.rerun()
            if c2.button("刪除", key=f"del_{n['id']}"):
                db.delete_note(n["id"])
                st.rerun()
