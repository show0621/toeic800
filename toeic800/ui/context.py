"""UI 共用：學習模組與 JLPT 等級。"""
from __future__ import annotations

import streamlit as st

from toeic800 import config


def learning_track() -> str:
    """toeic | japanese"""
    t = st.session_state.get("learning_track", "多益800")
    return "japanese" if t == "日文 N5–N1" else "toeic"


def jlpt_level() -> str:
    return st.session_state.get("jlpt_level", "N5")


def is_japanese() -> bool:
    return learning_track() == "japanese"
