"""平假名・片假名 50 音資料。"""
from __future__ import annotations

from typing import Literal

KanaType = Literal["hiragana", "katakana"]

# (行名, [(平假名, 片假名, 羅馬字), ...])
GOJUON: list[tuple[str, list[tuple[str, str, str]]]] = [
    (
        "あ行",
        [
            ("あ", "ア", "a"),
            ("い", "イ", "i"),
            ("う", "ウ", "u"),
            ("え", "エ", "e"),
            ("お", "オ", "o"),
        ],
    ),
    (
        "か行",
        [
            ("か", "カ", "ka"),
            ("き", "キ", "ki"),
            ("く", "ク", "ku"),
            ("け", "ケ", "ke"),
            ("こ", "コ", "ko"),
        ],
    ),
    (
        "さ行",
        [
            ("さ", "サ", "sa"),
            ("し", "シ", "shi"),
            ("す", "ス", "su"),
            ("せ", "セ", "se"),
            ("そ", "ソ", "so"),
        ],
    ),
    (
        "た行",
        [
            ("た", "タ", "ta"),
            ("ち", "チ", "chi"),
            ("つ", "ツ", "tsu"),
            ("て", "テ", "te"),
            ("と", "ト", "to"),
        ],
    ),
    (
        "な行",
        [
            ("な", "ナ", "na"),
            ("に", "ニ", "ni"),
            ("ぬ", "ヌ", "nu"),
            ("ね", "ネ", "ne"),
            ("の", "ノ", "no"),
        ],
    ),
    (
        "は行",
        [
            ("は", "ハ", "ha"),
            ("ひ", "ヒ", "hi"),
            ("ふ", "フ", "fu"),
            ("へ", "ヘ", "he"),
            ("ほ", "ホ", "ho"),
        ],
    ),
    (
        "ま行",
        [
            ("ま", "マ", "ma"),
            ("み", "ミ", "mi"),
            ("む", "ム", "mu"),
            ("め", "メ", "me"),
            ("も", "モ", "mo"),
        ],
    ),
    (
        "や行",
        [
            ("や", "ヤ", "ya"),
            ("ゆ", "ユ", "yu"),
            ("よ", "ヨ", "yo"),
        ],
    ),
    (
        "ら行",
        [
            ("ら", "ラ", "ra"),
            ("り", "リ", "ri"),
            ("る", "ル", "ru"),
            ("れ", "レ", "re"),
            ("ろ", "ロ", "ro"),
        ],
    ),
    (
        "わ行",
        [
            ("わ", "ワ", "wa"),
            ("を", "ヲ", "wo"),
            ("ん", "ン", "n"),
        ],
    ),
]

# 濁音・半濁音（進階）
DAKUON: list[tuple[str, list[tuple[str, str, str]]]] = [
    (
        "が行",
        [
            ("が", "ガ", "ga"),
            ("ぎ", "ギ", "gi"),
            ("ぐ", "グ", "gu"),
            ("げ", "ゲ", "ge"),
            ("ご", "ゴ", "go"),
        ],
    ),
    (
        "ざ行",
        [
            ("ざ", "ザ", "za"),
            ("じ", "ジ", "ji"),
            ("ず", "ズ", "zu"),
            ("ぜ", "ゼ", "ze"),
            ("ぞ", "ゾ", "zo"),
        ],
    ),
    (
        "だ行",
        [
            ("だ", "ダ", "da"),
            ("ぢ", "ヂ", "di"),
            ("づ", "ヅ", "du"),
            ("で", "デ", "de"),
            ("ど", "ド", "do"),
        ],
    ),
    (
        "ば行",
        [
            ("ば", "バ", "ba"),
            ("び", "ビ", "bi"),
            ("ぶ", "ブ", "bu"),
            ("べ", "ベ", "be"),
            ("ぼ", "ボ", "bo"),
        ],
    ),
    (
        "ぱ行",
        [
            ("ぱ", "パ", "pa"),
            ("ぴ", "ピ", "pi"),
            ("ぷ", "プ", "pu"),
            ("ぺ", "ペ", "pe"),
            ("ぽ", "ポ", "po"),
        ],
    ),
]


def all_kana(*, include_dakuon: bool = False) -> list[dict[str, str]]:
    rows = list(GOJUON)
    if include_dakuon:
        rows = rows + DAKUON
    out: list[dict[str, str]] = []
    for row_name, chars in rows:
        for h, k, r in chars:
            out.append(
                {
                    "row": row_name,
                    "hiragana": h,
                    "katakana": k,
                    "romaji": r,
                }
            )
    return out


def kana_char(item: dict[str, str], kana_type: KanaType) -> str:
    return item["hiragana"] if kana_type == "hiragana" else item["katakana"]
