"""聽力 Part 3 對話驗證（原創商務場景，非新聞）。"""
from __future__ import annotations

from toeic800.processing.tts import parse_dialogue


def is_part3_dialogue(audio_text: str) -> bool:
    """有效 Part 3 對話：至少兩輪，且同時有男(M)女(W)聲。"""
    turns = parse_dialogue(audio_text or "")
    if len(turns) < 2:
        return False
    speakers = {spk for spk, _ in turns}
    return "M" in speakers and "W" in speakers


def filter_listening_pool(pool: list[dict]) -> list[dict]:
    """排除單人獨白或格式錯誤的聽力題。"""
    out: list[dict] = []
    for q in pool:
        audio = q.get("audio_text") or ""
        if not audio.strip():
            continue
        if not is_part3_dialogue(audio):
            continue
        if not q.get("question") or not q.get("answer"):
            continue
        item = dict(q)
        item.setdefault("source", "toeic_rag_original")
        item["part_type"] = "part3_dialogue"
        out.append(item)
    return out
