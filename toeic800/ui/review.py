"""複習佇列 — 輸入中文確認答題。"""

from __future__ import annotations



from pathlib import Path



import streamlit as st



from toeic800.db.database import ToeicDatabase

from toeic800.processing.tts import ensure_tts

from toeic800.processing.vocab_examples import enrich_vocab_example

from toeic800.processing.vocab_quiz import check_ja_answer, check_zh_answer

from toeic800.processing.vocabulary import ensure_pronunciation

from toeic800.processing.vocab_selection import filter_active_vocabulary

from toeic800.ui.context import is_japanese, jlpt_level, learning_track





def render_review_page(db: ToeicDatabase) -> None:

    track = learning_track()

    level = jlpt_level() if is_japanese() else None

    toeic = not is_japanese()



    st.markdown("### 單字複習")

    st.caption(

        "看英文 → 輸入中文意思 → 確認答題 → 查看完整釋義並評分"

        if toeic

        else "看日文 → 輸入中文或讀音 → 確認答題"

    )



    limit = st.slider("本輪題數", 5, 30, 15, key="review_limit")

    queue = db.review_queue(limit=limit * 3, track=track, jlpt_level=level)
    queue = filter_active_vocabulary(queue, toeic=toeic)
    queue = queue[:limit]

    if not queue:
        st.info("尚無單字可複習（請至文章閱讀 → 單字管理納入學習）")

        return



    _init_review_session(len(queue))



    idx = st.session_state.review_idx % len(queue)

    card = queue[idx]

    card_id = card["id"]

    mastery = db.get_vocab_mastery(card_id)

    checked_key = f"review_checked_{card_id}"

    result_key = f"review_result_{card_id}"



    if "review_score" not in st.session_state:

        st.session_state.review_score = 0

    if "review_answered" not in st.session_state:

        st.session_state.review_answered = 0



    c1, c2, c3 = st.columns(3)

    c1.metric("進度", f"{idx + 1} / {len(queue)}")

    c2.metric("本輪答對", st.session_state.review_score)

    c3.metric("掌握度", f"{mastery}/5")



    st.progress((idx + 1) / len(queue))

    st.markdown(f"## {card['word']}")

    st.caption(card.get("article_title", ""))



    if toeic:

        audio = ensure_pronunciation(card["word"], accent="US")

        if audio and Path(audio).exists():

            st.audio(audio)



    input_label = "請輸入中文意思" if toeic else "請輸入中文意思或讀音"

    user_ans = st.text_input(

        input_label,

        key=f"review_input_{card_id}",

        placeholder="例如：通貨膨脹、波動性…",

        disabled=bool(st.session_state.get(checked_key)),

    )



    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:

        check = st.button(

            "確認答案",

            type="primary",

            key=f"review_check_{card_id}",

            disabled=bool(st.session_state.get(checked_key)),

        )

    with btn_col2:

        skip = st.button("跳過", key=f"review_skip_{card_id}")



    if check:

        if not user_ans.strip():

            st.warning("請先輸入中文意思。")

        else:

            card_ref = enrich_vocab_example(card) if toeic else card

            if toeic:

                ok, msg = check_zh_answer(user_ans, card_ref.get("meaning_zh") or "")

            else:

                ok, msg = check_ja_answer(

                    user_ans,

                    card_ref.get("meaning_zh") or "",

                    card_ref.get("meaning_en") or "",

                )

            st.session_state[checked_key] = True

            st.session_state[result_key] = {"ok": ok, "msg": msg}

            st.session_state.review_answered += 1

            if ok:

                st.session_state.review_score += 1

            st.rerun()



    if st.session_state.get(checked_key):

        result = st.session_state.get(result_key) or {}

        if result.get("ok"):

            st.success(result.get("msg", "正確"))

        else:

            st.error(result.get("msg", "尚未答對"))



        card_display = enrich_vocab_example(card) if toeic else card

        with st.expander("📖 完整釋義", expanded=not result.get("ok")):

            st.markdown(f"*{card_display.get('phonetic') or ''}* · {card_display.get('pos') or ''}")

            st.write("**中文：**", card_display.get("meaning_zh") or "—")

            label2 = "讀音" if is_japanese() else "英文"

            st.write(f"**{label2}：**", card_display.get("meaning_en") or "—")

            if card_display.get("example_en"):

                st.write("**例句（原創）：**", card_display["example_en"])

                st.caption(card_display.get("example_zh") or "")

                if toeic:

                    ex_path = ensure_tts(card_display["example_en"], lang="en", accent="US")

                    if ex_path and Path(ex_path).exists():

                        st.audio(ex_path)



        st.markdown("**掌握程度**（0 完全不會 → 5 已熟練）")

        cols = st.columns(6)

        for i, col in enumerate(cols):

            if col.button(str(i), key=f"m_{card_id}_{i}"):

                db.log_review(card_id, i)

                _advance_review(len(queue))

                st.rerun()



        if st.button("下一題 →", type="primary", key=f"review_next_{card_id}"):

            _advance_review(len(queue))

            st.rerun()



    if skip:

        _advance_review(len(queue))

        st.rerun()





def _init_review_session(queue_len: int) -> None:

    if "review_idx" not in st.session_state:

        st.session_state.review_idx = 0

    if "review_queue_len" not in st.session_state:

        st.session_state.review_queue_len = queue_len

    elif st.session_state.review_queue_len != queue_len:

        st.session_state.review_idx = 0

        st.session_state.review_score = 0

        st.session_state.review_answered = 0

        st.session_state.review_queue_len = queue_len

        _clear_card_state()





def _advance_review(queue_len: int) -> None:

    st.session_state.review_idx += 1

    _clear_card_state()

    if st.session_state.review_idx >= queue_len:

        st.session_state.review_idx = 0

        st.toast("本輪複習完成！")





def _clear_card_state() -> None:

    for k in list(st.session_state.keys()):

        sk = str(k)

        if sk.startswith("review_checked_") or sk.startswith("review_result_"):

            st.session_state.pop(k, None)


