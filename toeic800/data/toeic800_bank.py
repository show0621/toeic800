"""多益 800–900 分擬真題庫（聽力、文法、單字、閱讀）。"""
from __future__ import annotations

from typing import Any, Literal

Skill = Literal["vocab", "grammar", "listening", "reading"]
ReadingFormat = Literal["single", "double", "triple"]

# Part 5 風格 — 單字／詞性
VOCAB_BANK: list[dict[str, Any]] = [
    {
        "question": "Mounting concerns over inflation have ___ investor sentiment across global equity markets.",
        "options": ["dampened", "dampen", "dampening", "been damp"],
        "answer": "dampened",
        "explanation_zh": "現在完成式 have + 過去分詞。",
    },
    {
        "question": "The board's decision was ___ unanimous, with only one director abstaining.",
        "options": ["virtually", "virtual", "virtue", "virtuous"],
        "answer": "virtually",
        "explanation_zh": "副詞修飾形容詞 unanimous。",
    },
    {
        "question": "Analysts warned that prolonged volatility could ___ the firm's ability to raise capital.",
        "options": ["jeopardize", "jeopardy", "jeopardizing", "jeopardized"],
        "answer": "jeopardize",
        "explanation_zh": "情態動詞 could + 動詞原形。",
    },
    {
        "question": "The merger is subject ___ regulatory approval in three jurisdictions.",
        "options": ["to", "for", "with", "on"],
        "answer": "to",
        "explanation_zh": "固定搭配 subject to（須經…批准）。",
    },
    {
        "question": "Despite robust earnings, the stock price remained ___ due to macroeconomic headwinds.",
        "options": ["sluggish", "sluggishly", "sluggard", "slug"],
        "answer": "sluggish",
        "explanation_zh": "系動詞 remained + 形容詞。",
    },
    {
        "question": "The CFO emphasized the need for greater transparency ___ financial reporting.",
        "options": ["in", "on", "at", "by"],
        "answer": "in",
        "explanation_zh": "transparency in reporting（報告透明度）。",
    },
    {
        "question": "Notwithstanding recent gains, the benchmark index is still ___ its all-time high.",
        "options": ["below", "underneath", "down", "less"],
        "answer": "below",
        "explanation_zh": "below the high（低於高點）為慣用搭配。",
    },
    {
        "question": "The company will ___ its operations in Southeast Asia to reduce overhead costs.",
        "options": ["consolidate", "consolidation", "consolidated", "consolidating"],
        "answer": "consolidate",
        "explanation_zh": "will + 動詞原形。",
    },
    {
        "question": "Shareholders expressed ___ about the proposed dilution of their equity stakes.",
        "options": ["apprehension", "apprehend", "apprehensive", "apprehensively"],
        "answer": "apprehension",
        "explanation_zh": "express + 名詞（擔憂）。",
    },
    {
        "question": "The stimulus package is intended to ___ small businesses affected by the downturn.",
        "options": ["bolster", "bolstering", "bolstered", "bolsters"],
        "answer": "bolster",
        "explanation_zh": "be intended to + 原形動詞。",
    },
    {
        "question": "A substantial ___ in commodity prices has squeezed profit margins industry-wide.",
        "options": ["surge", "surging", "surged", "surges"],
        "answer": "surge",
        "explanation_zh": "冠詞 a + 名詞 surge。",
    },
    {
        "question": "The audit revealed several ___ in the company's compliance procedures.",
        "options": ["deficiencies", "deficient", "deficiency", "deficiently"],
        "answer": "deficiencies",
        "explanation_zh": "several + 複數名詞。",
    },
    {
        "question": "Management has been ___ to divest non-core assets before year-end.",
        "options": ["instructed", "instruct", "instructing", "instruction"],
        "answer": "instructed",
        "explanation_zh": "被動語態 has been + 過去分詞。",
    },
    {
        "question": "The likelihood of a rate cut has ___ following stronger-than-expected employment data.",
        "options": ["diminished", "diminish", "diminishing", "diminution"],
        "answer": "diminished",
        "explanation_zh": "現在完成式 has diminished。",
    },
    {
        "question": "Investors are increasingly ___ toward emerging-market debt instruments.",
        "options": ["cautious", "caution", "cautiously", "cautioned"],
        "answer": "cautious",
        "explanation_zh": "be cautious toward（對…持謹慎態度）。",
    },
    {
        "question": "The firm's revenue growth was ___ by currency fluctuations in Q3.",
        "options": ["offset", "offsetting", "offsets", "offsetted"],
        "answer": "offset",
        "explanation_zh": "被動 was offset by（被…抵消）。",
    },
    {
        "question": "Regulators will ___ scrutinize banks with excessive exposure to commercial real estate.",
        "options": ["more", "most", "much", "many"],
        "answer": "more",
        "explanation_zh": "more scrutinize = 更加審查（副詞修飾動詞）。",
    },
    {
        "question": "The prospectus provides a ___ overview of the risks associated with the offering.",
        "options": ["comprehensive", "comprehensively", "comprehend", "comprehension"],
        "answer": "comprehensive",
        "explanation_zh": "形容詞修飾 overview。",
    },
    {
        "question": "Albeit modest, the recovery in manufacturing output suggests ___ momentum.",
        "options": ["renewed", "renew", "renewing", "renewal"],
        "answer": "renewed",
        "explanation_zh": "形容詞 renewed momentum（重新恢復的動能）。",
    },
    {
        "question": "The hedge fund's strategy relies heavily ___ quantitative models and algorithmic trading.",
        "options": ["on", "in", "at", "with"],
        "answer": "on",
        "explanation_zh": "rely on（依賴）。",
    },
    {
        "question": "Escalating geopolitical tensions have ___ supply chains across the semiconductor sector.",
        "options": ["disrupted", "disrupt", "disrupting", "disruption"],
        "answer": "disrupted",
        "explanation_zh": "現在完成式 have disrupted。",
    },
    {
        "question": "The underwriter set the IPO price at the ___ end of the expected range.",
        "options": ["upper", "up", "upwardly", "upmost"],
        "answer": "upper",
        "explanation_zh": "upper end of the range（區間上限）。",
    },
    {
        "question": "Proceeds from the bond issuance will be used to ___ existing high-yield debt.",
        "options": ["refinance", "refinancing", "refinanced", "refinancement"],
        "answer": "refinance",
        "explanation_zh": "be used to + 原形（用於再融資）。",
    },
    {
        "question": "The committee found the proposal commercially ___ and recommended approval.",
        "options": ["viable", "viably", "viability", "viablest"],
        "answer": "viable",
        "explanation_zh": "commercially viable（商業上可行）。",
    },
    {
        "question": "Persistent inflation has eroded household purchasing power, ___ consumer discretionary spending.",
        "options": ["curbing", "curb", "curbed", "curbs"],
        "answer": "curbing",
        "explanation_zh": "分詞片語作結果補語。",
    },
]

# Part 5/6 文法 — 介系詞、時態、一致、倒裝
GRAMMAR_BANK: list[dict[str, Any]] = [
    {
        "question": "Had the central bank intervened earlier, the currency ___ depreciated so sharply.",
        "options": [
            "would not have",
            "will not have",
            "would not",
            "did not have",
        ],
        "answer": "would not have",
        "explanation_zh": "與過去事實相反的第三類條件句。",
    },
    {
        "question": "Neither the CEO nor the directors ___ available for comment yesterday.",
        "options": ["were", "was", "is", "has been"],
        "answer": "were",
        "explanation_zh": "neither A nor B 動詞與 B 一致（directors → were）。",
    },
    {
        "question": "The report, along with its appendices, ___ submitted to the board last Friday.",
        "options": ["was", "were", "are", "have been"],
        "answer": "was",
        "explanation_zh": "主語 The report 為單數，along with 不影響動詞單複數。",
    },
    {
        "question": "Scarcely had trading resumed ___ the index plunged another two percent.",
        "options": ["when", "than", "then", "after"],
        "answer": "when",
        "explanation_zh": "Scarcely had... when...（倒裝句型）。",
    },
    {
        "question": "The contract will not take effect ___ both parties have signed it.",
        "options": ["until", "during", "while", "since"],
        "answer": "until",
        "explanation_zh": "not... until（直到…才）。",
    },
    {
        "question": "All applications must be accompanied ___ a certified copy of the applicant's passport.",
        "options": ["by", "with", "on", "for"],
        "answer": "by",
        "explanation_zh": "be accompanied by（附帶）。",
    },
    {
        "question": "The more volatile the market becomes, ___ cautious institutional investors tend to be.",
        "options": ["the", "more", "much", "most"],
        "answer": "the",
        "explanation_zh": "The more..., the... 比較句型。",
    },
    {
        "question": "It is imperative that every employee ___ the updated compliance guidelines.",
        "options": ["follow", "follows", "followed", "following"],
        "answer": "follow",
        "explanation_zh": "It is imperative that + 原形（虛擬語氣）。",
    },
    {
        "question": "The acquisition was completed in spite ___ significant opposition from minority shareholders.",
        "options": ["of", "to", "from", "with"],
        "answer": "of",
        "explanation_zh": "in spite of（儘管）。",
    },
    {
        "question": "By the time the audit concludes, the firm ___ its internal controls twice this year.",
        "options": [
            "will have reviewed",
            "will review",
            "has reviewed",
            "reviewed",
        ],
        "answer": "will have reviewed",
        "explanation_zh": "By the time + 未來完成式。",
    },
    {
        "question": "The data suggest that consumer confidence ___ since the policy announcement.",
        "options": ["has improved", "improve", "improving", "were improved"],
        "answer": "has improved",
        "explanation_zh": "since 搭配現在完成式。",
    },
    {
        "question": "No sooner ___ the earnings report published than the share price rallied.",
        "options": ["was", "were", "had", "did"],
        "answer": "was",
        "explanation_zh": "No sooner was... than...（報告為單數）。",
    },
    {
        "question": "The board is divided over whether to proceed ___ the hostile takeover bid.",
        "options": ["with", "to", "on", "by"],
        "answer": "with",
        "explanation_zh": "proceed with（繼續進行）。",
    },
    {
        "question": "Such ___ the demand for the product that the company struggled to fulfill orders.",
        "options": ["was", "were", "is", "has been"],
        "answer": "was",
        "explanation_zh": "Such was... 倒裝，demand 為不可數單數。",
    },
    {
        "question": "The analyst attributed the sell-off ___ concerns about rising borrowing costs.",
        "options": ["to", "for", "with", "on"],
        "answer": "to",
        "explanation_zh": "attribute A to B（把 A 歸因於 B）。",
    },
    {
        "question": "Not only ___ the company exceed revenue targets, but it also reduced operating expenses.",
        "options": ["did", "does", "has", "was"],
        "answer": "did",
        "explanation_zh": "Not only did... but also... 倒裝。",
    },
    {
        "question": "The warranty is valid provided that the equipment ___ by authorized personnel only.",
        "options": ["is serviced", "serviced", "services", "has service"],
        "answer": "is serviced",
        "explanation_zh": "被動語態 is serviced。",
    },
    {
        "question": "Few of the proposals submitted ___ deemed feasible by the review committee.",
        "options": ["were", "was", "is", "has been"],
        "answer": "were",
        "explanation_zh": "Few of + 複數 proposals → were。",
    },
    {
        "question": "The CEO insisted on ___ personally before any merger terms were disclosed.",
        "options": ["being briefed", "brief", "briefing", "to brief"],
        "answer": "being briefed",
        "explanation_zh": "insist on + 動名詞；被動 being briefed。",
    },
    {
        "question": "Were it not for the government bailout, the bank ___ collapsed.",
        "options": ["would have", "will have", "would", "had"],
        "answer": "would have",
        "explanation_zh": "Were it not for = If it were not for（與過去事實相反）。",
    },
    {
        "question": "The committee will convene next week to discuss matters pertaining ___ the restructuring plan.",
        "options": ["to", "with", "on", "for"],
        "answer": "to",
        "explanation_zh": "pertaining to（關於）。",
    },
    {
        "question": "Hardly anyone in the industry anticipated ___ abrupt a shift in monetary policy.",
        "options": ["so", "such", "as", "that"],
        "answer": "so",
        "explanation_zh": "so abrupt a shift = such an abrupt shift。",
    },
    {
        "question": "The subsidiary operates independently, but its financial results are consolidated ___ those of the parent.",
        "options": ["with", "to", "into", "on"],
        "answer": "with",
        "explanation_zh": "consolidated with（合併報表）。",
    },
    {
        "question": "Should the deal fail to close by December, either party ___ the agreement without penalty.",
        "options": ["may terminate", "must terminating", "would terminated", "can termination"],
        "answer": "may terminate",
        "explanation_zh": "Should...（万一…）+ 現在式表條件。",
    },
    {
        "question": "The extent ___ which the new tariffs will affect exports remains uncertain.",
        "options": ["to", "of", "for", "in"],
        "answer": "to",
        "explanation_zh": "the extent to which（…的程度）。",
    },
]

# Part 3/4 風格聽力 — audio_text 供 TTS
LISTENING_BANK: list[dict[str, Any]] = [
    {
        "audio_text": "W: The quarterly figures came in below consensus. M: Then we'd better revise our forecast before the investor call.",
        "question": "What will the speakers most likely do next?",
        "options": [
            "Update their financial projections",
            "Cancel the investor conference",
            "Hire an external auditor",
            "Issue new company shares",
        ],
        "answer": "Update their financial projections",
        "explanation_zh": "revise our forecast = 修正財測。",
    },
    {
        "audio_text": "M: Has the compliance team signed off on the revised disclosure? W: Not yet—they're still reviewing the footnotes.",
        "question": "What is the status of the disclosure?",
        "options": [
            "It is still under review",
            "It has already been approved",
            "It was rejected outright",
            "It will be drafted tomorrow",
        ],
        "answer": "It is still under review",
        "explanation_zh": "still reviewing = 仍在審查中。",
    },
    {
        "audio_text": "W: Our logistics partner notified us of a two-week delay at the port. M: That could jeopardize our ability to meet holiday demand.",
        "question": "What is the man's concern?",
        "options": [
            "Meeting seasonal customer demand",
            "Negotiating a new port contract",
            "Reducing warehouse rent",
            "Expanding into new markets",
        ],
        "answer": "Meeting seasonal customer demand",
        "explanation_zh": "holiday demand = 節慶旺季需求。",
    },
    {
        "audio_text": "M: The board wants a comprehensive risk assessment before approving the leverage increase. W: I'll coordinate with treasury and legal by Friday.",
        "question": "What does the woman offer to do?",
        "options": [
            "Organize cross-department input",
            "Approve the leverage increase",
            "Present at the shareholders' meeting",
            "Finalize the acquisition price",
        ],
        "answer": "Organize cross-department input",
        "explanation_zh": "coordinate with treasury and legal。",
    },
    {
        "audio_text": "W: Inflationary pressures are mounting, yet consumer spending has remained surprisingly resilient. M: That divergence is making policy decisions more difficult.",
        "question": "What are the speakers discussing?",
        "options": [
            "The challenge of economic policy decisions",
            "Plans to launch a new consumer product",
            "A recent merger in the retail sector",
            "Changes to employee benefit packages",
        ],
        "answer": "The challenge of economic policy decisions",
        "explanation_zh": "policy decisions more difficult。",
    },
    {
        "audio_text": "M: Should we hedge our currency exposure before the earnings release? W: Given the volatility, I'd say that's prudent.",
        "question": "What does the woman recommend?",
        "options": [
            "Taking precautions against currency risk",
            "Delaying the earnings announcement",
            "Investing in domestic equities only",
            "Renegotiating supplier contracts",
        ],
        "answer": "Taking precautions against currency risk",
        "explanation_zh": "hedge currency exposure = 避險。",
    },
    {
        "audio_text": "W: The underwriter suggested pricing the IPO at the lower end of the range. M: That might bolster demand among institutional investors.",
        "question": "Why might the man agree with the pricing strategy?",
        "options": [
            "It could attract large-scale buyers",
            "It guarantees maximum profit margins",
            "It eliminates regulatory scrutiny",
            "It reduces the number of shares offered",
        ],
        "answer": "It could attract large-scale buyers",
        "explanation_zh": "bolster demand among institutional investors。",
    },
    {
        "audio_text": "M: We've received substantial interest from sovereign wealth funds. W: Then we should prepare a more detailed prospectus.",
        "question": "What does the woman suggest?",
        "options": [
            "Providing additional documentation",
            "Declining all foreign investment",
            "Postponing the fund-raising effort",
            "Reducing the offering size",
        ],
        "answer": "Providing additional documentation",
        "explanation_zh": "prepare a more detailed prospectus。",
    },
    {
        "audio_text": "W: The audit flagged several deficiencies in our internal controls. M: We'll need to overhaul our reporting procedures immediately.",
        "question": "What action does the man propose?",
        "options": [
            "Revamping reporting processes",
            "Expanding into overseas markets",
            "Hiring additional sales staff",
            "Launching a marketing campaign",
        ],
        "answer": "Revamping reporting processes",
        "explanation_zh": "overhaul reporting procedures。",
    },
    {
        "audio_text": "M: Tariff escalation could undermine our margins in the European market. W: Perhaps we should diversify our supplier base.",
        "question": "What solution does the woman propose?",
        "options": [
            "Broadening sourcing options",
            "Raising product prices sharply",
            "Closing the European division",
            "Applying for government subsidies",
        ],
        "answer": "Broadening sourcing options",
        "explanation_zh": "diversify supplier base。",
    },
    {
        "audio_text": "W: The stimulus package should bolster small businesses affected by the downturn. M: Provided it's disbursed without excessive bureaucracy.",
        "question": "What is the man's condition for success?",
        "options": [
            "Efficient distribution of funds",
            "Higher interest rates",
            "Reduced corporate taxes",
            "Stricter lending standards",
        ],
        "answer": "Efficient distribution of funds",
        "explanation_zh": "without excessive bureaucracy = 有效率發放。",
    },
    {
        "audio_text": "M: Our benchmark index is still below its all-time high despite recent gains. W: Notwithstanding that, investor sentiment has improved.",
        "question": "What does the woman point out?",
        "options": [
            "Market confidence has gotten better",
            "The index reached a record level",
            "Trading volume has collapsed",
            "Interest rates will rise soon",
        ],
        "answer": "Market confidence has gotten better",
        "explanation_zh": "investor sentiment has improved。",
    },
    {
        "audio_text": "W: Could you brief the committee on the liquidity constraints? M: Certainly—I'll highlight our exposure to short-term funding markets.",
        "question": "What will the man focus on in his briefing?",
        "options": [
            "Short-term financing risks",
            "Long-term capital expenditure",
            "Employee training programs",
            "Product development timelines",
        ],
        "answer": "Short-term financing risks",
        "explanation_zh": "exposure to short-term funding markets。",
    },
    {
        "audio_text": "M: The likelihood of a rate cut has diminished after the jobs report. W: That explains the rally in banking stocks.",
        "question": "What does the woman imply?",
        "options": [
            "Bank stocks rose for a logical reason",
            "The jobs report was unexpectedly weak",
            "Rate cuts are guaranteed next month",
            "Investors are avoiding bank shares",
        ],
        "answer": "Bank stocks rose for a logical reason",
        "explanation_zh": "That explains the rally。",
    },
    {
        "audio_text": "W: We need regulatory approval in three jurisdictions before closing. M: Legal is already coordinating with local counsel.",
        "question": "What is being done about the requirement?",
        "options": [
            "Legal teams are working on compliance",
            "The deal has been abandoned",
            "Approval was granted last week",
            "The closing date was moved up",
        ],
        "answer": "Legal teams are working on compliance",
        "explanation_zh": "coordinating with local counsel。",
    },
    {
        "audio_text": "M: The prospectus provides a comprehensive overview of the risks. W: Investors will scrutinize the section on geopolitical exposure.",
        "question": "What do the speakers expect investors to examine closely?",
        "options": [
            "Political and international risk factors",
            "The company's cafeteria services",
            "Office relocation plans",
            "Annual holiday schedules",
        ],
        "answer": "Political and international risk factors",
        "explanation_zh": "geopolitical exposure。",
    },
    {
        "audio_text": "W: Proceeds from the bond issuance will refinance existing high-yield debt. M: That should alleviate some pressure on our balance sheet.",
        "question": "What benefit does the man anticipate?",
        "options": [
            "Reduced financial strain",
            "Higher dividend payouts",
            "Increased headcount",
            "Expansion of retail stores",
        ],
        "answer": "Reduced financial strain",
        "explanation_zh": "alleviate pressure on balance sheet。",
    },
    {
        "audio_text": "M: Escalating tensions have disrupted semiconductor supply chains. W: We may need to increase inventory buffers.",
        "question": "What does the woman suggest?",
        "options": [
            "Stockpiling additional supplies",
            "Exiting the semiconductor business",
            "Reducing product quality standards",
            "Lowering employee salaries",
        ],
        "answer": "Stockpiling additional supplies",
        "explanation_zh": "increase inventory buffers。",
    },
    {
        "audio_text": "W: The committee found the proposal commercially viable. M: Then I'll recommend approval at tomorrow's board meeting.",
        "question": "What will the man do?",
        "options": [
            "Endorse the proposal to the board",
            "Reject the business plan",
            "Request additional funding",
            "Delay the vote indefinitely",
        ],
        "answer": "Endorse the proposal to the board",
        "explanation_zh": "recommend approval at board meeting。",
    },
    {
        "audio_text": "M: Persistent inflation has eroded purchasing power. W: Which is why discretionary spending has been curbed.",
        "question": "According to the woman, what has happened to consumer behavior?",
        "options": [
            "Nonessential spending has decreased",
            "Luxury purchases have surged",
            "Savings rates have disappeared",
            "Credit card usage is unrestricted",
        ],
        "answer": "Nonessential spending has decreased",
        "explanation_zh": "discretionary spending has been curbed。",
    },
]

# Part 7 閱讀 — 單篇 / 雙篇 / 三篇
READING_BANK: list[dict[str, Any]] = [
    {
        "format": "single",
        "passages": [
            {
                "label": "Article",
                "text": (
                    "Global equity markets experienced heightened volatility last week as investors "
                    "weighed mounting inflation data against signals that major central banks may "
                    "maintain restrictive monetary policy longer than anticipated. Analysts noted that "
                    "while corporate earnings remained broadly resilient, sectors with high leverage "
                    "faced renewed scrutiny. Fund managers increasingly favored defensive positions "
                    "in utilities and consumer staples, citing concerns that further rate increases "
                    "could jeopardize refinancing activity among mid-cap borrowers."
                ),
            }
        ],
        "question": "According to the passage, why did fund managers shift toward defensive sectors?",
        "options": [
            "Concerns about refinancing difficulties for heavily indebted firms",
            "A sudden collapse in corporate earnings across all industries",
            "Mandatory regulations requiring utility investments",
            "A decline in inflation that reduced interest rates",
        ],
        "answer": "Concerns about refinancing difficulties for heavily indebted firms",
        "explanation_zh": "high leverage / jeopardize refinancing activity。",
    },
    {
        "format": "single",
        "passages": [
            {
                "label": "Report excerpt",
                "text": (
                    "The proposed merger between the two pharmaceutical giants is subject to antitrust "
                    "review in multiple jurisdictions. Although the companies argue that the deal "
                    "will consolidate research capabilities and accelerate drug development, consumer "
                    "advocates warn it could diminish competition in specialty markets. The board has "
                    "instructed management to prepare a comprehensive divestiture plan should regulators "
                    "require asset sales as a condition of approval."
                ),
            }
        ],
        "question": "What has the board asked management to prepare?",
        "options": [
            "A plan to sell assets if required by regulators",
            "An immediate withdrawal of the merger bid",
            "A marketing campaign for new pharmaceutical products",
            "A reduction in the company's research budget",
        ],
        "answer": "A plan to sell assets if required by regulators",
        "explanation_zh": "divestiture plan / asset sales as condition。",
    },
    {
        "format": "single",
        "passages": [
            {
                "label": "Memo",
                "text": (
                    "Effective next quarter, all regional offices must comply with the updated "
                    "financial reporting standards outlined in Appendix C. The compliance team will "
                    "conduct audits to identify deficiencies in internal controls. Employees who "
                    "fail to complete the mandatory training by March 15 will not be authorized to "
                    "process transactions exceeding ten thousand dollars."
                ),
            }
        ],
        "question": "What consequence is stated for employees who miss the training deadline?",
        "options": [
            "They cannot handle large transactions",
            "They will be transferred to another department",
            "They must work overtime without compensation",
            "They will lose access to email accounts",
        ],
        "answer": "They cannot handle large transactions",
        "explanation_zh": "not authorized to process transactions exceeding...",
    },
    {
        "format": "single",
        "passages": [
            {
                "label": "News brief",
                "text": (
                    "Oil prices surged after several exporting nations signaled willingness to extend "
                    "production cuts through the end of the year. Energy analysts cautioned that "
                    "persistent supply constraints, combined with robust demand in emerging markets, "
                    "could exacerbate inflationary pressures in import-dependent economies. Governments "
                    "in those regions are contemplating subsidy programs to alleviate the burden on "
                    "households, albeit at substantial fiscal cost."
                ),
            }
        ],
        "question": "What are import-dependent governments considering?",
        "options": [
            "Financial assistance programs for citizens",
            "Complete bans on oil consumption",
            "Withdrawal from international trade agreements",
            "Nationalization of all energy companies",
        ],
        "answer": "Financial assistance programs for citizens",
        "explanation_zh": "subsidy programs to alleviate burden on households。",
    },
    {
        "format": "single",
        "passages": [
            {
                "label": "Press release",
                "text": (
                    "The technology firm announced that proceeds from its bond issuance will be used "
                    "to refinance existing high-yield debt and fund expansion into cloud infrastructure "
                    "in Asia-Pacific markets. The CFO emphasized that the offering was oversubscribed, "
                    "reflecting strong institutional appetite despite recent market turbulence. The "
                    "company expects the transaction to bolster its liquidity profile and reduce "
                    "near-term borrowing costs."
                ),
            }
        ],
        "question": "What does the company plan to do with the bond proceeds?",
        "options": [
            "Refinance debt and expand regional infrastructure",
            "Acquire a competitor in the retail sector",
            "Pay special dividends to all shareholders",
            "Close underperforming manufacturing plants",
        ],
        "answer": "Refinance debt and expand regional infrastructure",
        "explanation_zh": "refinance high-yield debt / cloud infrastructure in Asia-Pacific。",
    },
    {
        "format": "single",
        "passages": [
            {
                "label": "Email",
                "text": (
                    "Dear Shareholders, At yesterday's extraordinary general meeting, the board "
                    "approved a share repurchase program of up to five hundred million dollars. "
                    "Management believes the current market price does not reflect the company's "
                    "long-term value proposition. Repurchases will be executed subject to regulatory "
                    "limits and prevailing market conditions. A detailed schedule will be disclosed "
                    "in next month's investor relations bulletin."
                ),
            }
        ],
        "question": "Why does management support the repurchase program?",
        "options": [
            "They believe the stock is undervalued",
            "They need to reduce the number of employees",
            "Regulators require immediate buybacks",
            "The company is preparing for bankruptcy",
        ],
        "answer": "They believe the stock is undervalued",
        "explanation_zh": "price does not reflect long-term value proposition。",
    },
    {
        "format": "single",
        "passages": [
            {
                "label": "Analysis",
                "text": (
                    "Notwithstanding recent gains in the benchmark index, portfolio managers remain "
                    "cautious amid escalating geopolitical tensions that have disrupted semiconductor "
                    "supply chains. Several firms have increased inventory buffers and diversified "
                    "suppliers across multiple regions. While such measures may bolster resilience, "
                    "they also elevate overhead costs and could offset efficiency gains achieved "
                    "through prior consolidation efforts."
                ),
            }
        ],
        "question": "What potential drawback of the firms' strategy is mentioned?",
        "options": [
            "Higher operating expenses",
            "Complete loss of market share",
            "Mandatory government ownership",
            "Elimination of all overseas suppliers",
        ],
        "answer": "Higher operating expenses",
        "explanation_zh": "elevate overhead costs / offset efficiency gains。",
    },
    {
        "format": "single",
        "passages": [
            {
                "label": "Notice",
                "text": (
                    "The audit committee has engaged an external firm to scrutinize revenue "
                    "recognition practices following anonymous allegations. Preliminary findings "
                    "suggest several deficiencies in documentation, though no material misstatement "
                    "has been confirmed. The CEO insisted on being briefed personally before any "
                    "findings are communicated to regulators or the public."
                ),
            }
        ],
        "question": "What is true about the audit so far?",
        "options": [
            "Documentation weaknesses were found but no major error is confirmed",
            "The CEO refused to receive any information",
            "Regulators have already imposed fines",
            "Revenue figures were proven fraudulent",
        ],
        "answer": "Documentation weaknesses were found but no major error is confirmed",
        "explanation_zh": "deficiencies in documentation / no material misstatement confirmed。",
    },
    {
        "format": "double",
        "passages": [
            {
                "label": "Email — CFO to Board",
                "text": (
                    "Subject: Q3 Liquidity Update. Our short-term funding exposure remains elevated "
                    "due to maturing commercial paper. Treasury is negotiating a revolving credit "
                    "facility, but terms may be less favorable given recent rating agency commentary."
                ),
            },
            {
                "label": "Email — Board Chair reply",
                "text": (
                    "Thank you for the update. Please coordinate with legal to ensure covenant "
                    "compliance under our existing indentures. We should also prepare contingency "
                    "scenarios should the facility not close before month-end."
                ),
            },
        ],
        "question": "What does the board chair want the CFO to do?",
        "options": [
            "Work with legal and plan backup options",
            "Immediately cancel all commercial paper",
            "Announce a public stock offering today",
            "Ignore rating agency opinions",
        ],
        "answer": "Work with legal and plan backup options",
        "explanation_zh": "coordinate with legal / contingency scenarios。",
    },
    {
        "format": "double",
        "passages": [
            {
                "label": "Internal memo",
                "text": (
                    "The logistics partner notified us of a two-week delay at the primary port. "
                    "Holiday inventory targets may be at risk unless alternate routing is approved."
                ),
            },
            {
                "label": "Reply memo",
                "text": (
                    "Operations has identified two secondary ports. Although freight costs will "
                    "increase by approximately eight percent, leadership authorized the change to "
                    "protect customer commitments."
                ),
            },
        ],
        "question": "Why did leadership approve alternate ports?",
        "options": [
            "To fulfill promises to customers despite higher cost",
            "To reduce freight expenses significantly",
            "To permanently close the primary port",
            "To delay all holiday shipments",
        ],
        "answer": "To fulfill promises to customers despite higher cost",
        "explanation_zh": "protect customer commitments / costs will increase。",
    },
    {
        "format": "double",
        "passages": [
            {
                "label": "Market commentary",
                "text": (
                    "Inflationary pressures are mounting, yet consumer spending has remained "
                    "surprisingly resilient in the services sector."
                ),
            },
            {
                "label": "Policy brief",
                "text": (
                    "This divergence complicates monetary policy: tightening too aggressively "
                    "could curb growth, while easing prematurely may exacerbate price instability."
                ),
            },
        ],
        "question": "What challenge do policymakers face according to both texts?",
        "options": [
            "Balancing inflation control with economic growth",
            "Eliminating all consumer spending",
            "Increasing tariffs on services only",
            "Closing foreign exchange markets",
        ],
        "answer": "Balancing inflation control with economic growth",
        "explanation_zh": "tightening vs easing / inflation vs growth。",
    },
    {
        "format": "double",
        "passages": [
            {
                "label": "Vendor proposal",
                "text": (
                    "Our cloud migration package includes 24/7 monitoring and quarterly compliance "
                    "audits aligned with your industry's regulatory framework."
                ),
            },
            {
                "label": "IT director response",
                "text": (
                    "We appreciate the comprehensive scope. Before signing, we need clarification "
                    "on data residency requirements for our European subsidiaries."
                ),
            },
        ],
        "question": "What issue must be resolved before the IT director will sign?",
        "options": [
            "Where data will be stored for EU operations",
            "Whether the vendor offers free hardware",
            "The color scheme of the user interface",
            "Employee vacation policies",
        ],
        "answer": "Where data will be stored for EU operations",
        "explanation_zh": "data residency requirements for European subsidiaries。",
    },
    {
        "format": "double",
        "passages": [
            {
                "label": "HR announcement",
                "text": (
                    "All staff must complete updated compliance training by March 15 to retain "
                    "authorization for high-value transactions."
                ),
            },
            {
                "label": "Department head note",
                "text": (
                    "Team leads should schedule make-up sessions for anyone traveling on assignment. "
                    "No exceptions will be granted after the deadline."
                ),
            },
        ],
        "question": "What arrangement is provided for traveling employees?",
        "options": [
            "Supplementary training sessions",
            "Permanent exemption from training",
            "Automatic promotion upon return",
            "Unlimited transaction authority",
        ],
        "answer": "Supplementary training sessions",
        "explanation_zh": "make-up sessions for anyone traveling。",
    },
    {
        "format": "double",
        "passages": [
            {
                "label": "Investment summary",
                "text": (
                    "The hedge fund's strategy relies heavily on quantitative models and algorithmic "
                    "trading across multiple asset classes."
                ),
            },
            {
                "label": "Risk disclosure",
                "text": (
                    "Sudden volatility spikes can undermine model assumptions, potentially leading "
                    "to substantial drawdowns within short intervals."
                ),
            },
        ],
        "question": "What risk is highlighted when combining both documents?",
        "options": [
            "Rapid losses if market volatility surges",
            "Guaranteed profits in all conditions",
            "Complete immunity from regulation",
            "Dependence on manual trading only",
        ],
        "answer": "Rapid losses if market volatility surges",
        "explanation_zh": "volatility spikes / substantial drawdowns。",
    },
    {
        "format": "double",
        "passages": [
            {
                "label": "Supplier letter",
                "text": (
                    "Tariff escalation could undermine margins on components shipped to your European "
                    "assembly plants."
                ),
            },
            {
                "label": "Procurement reply",
                "text": (
                    "We are diversifying our supplier base across Southeast Asia and Eastern Europe "
                    "to mitigate exposure."
                ),
            },
        ],
        "question": "How is the company responding to the supplier's warning?",
        "options": [
            "By spreading sourcing across more regions",
            "By ending all European operations",
            "By raising tariffs on customers",
            "By reducing product quality standards",
        ],
        "answer": "By spreading sourcing across more regions",
        "explanation_zh": "diversifying supplier base across multiple regions。",
    },
    {
        "format": "triple",
        "passages": [
            {
                "label": "Press release",
                "text": (
                    "Lexon Corp announced a proposed acquisition of MedAxis for $4.2 billion, subject "
                    "to shareholder and regulatory approval."
                ),
            },
            {
                "label": "Analyst note",
                "text": (
                    "The deal would consolidate research pipelines but may trigger divestiture "
                    "requirements in oncology and diagnostics."
                ),
            },
            {
                "label": "Regulator statement",
                "text": (
                    "We will assess whether the transaction substantially lessens competition and "
                    "may impose conditions to preserve market access."
                ),
            },
        ],
        "question": "What outcome is possible according to all three sources?",
        "options": [
            "The deal could proceed only with regulatory conditions",
            "Shareholders already rejected the offer",
            "MedAxis will acquire Lexon instead",
            "No approvals of any kind are necessary",
        ],
        "answer": "The deal could proceed only with regulatory conditions",
        "explanation_zh": "subject to approval / divestiture / impose conditions。",
    },
    {
        "format": "triple",
        "passages": [
            {
                "label": "CEO message",
                "text": (
                    "Our Asia-Pacific expansion will bolster long-term revenue diversification."
                ),
            },
            {
                "label": "CFO appendix",
                "text": (
                    "Near-term capital expenditure will peak in Q2, temporarily constraining free "
                    "cash flow."
                ),
            },
            {
                "label": "Investor FAQ",
                "text": (
                    "Management expects return on invested capital to improve beginning fiscal 2027 "
                    "once infrastructure reaches scale."
                ),
            },
        ],
        "question": "What timeline for financial improvement is suggested overall?",
        "options": [
            "After initial spending, benefits emerge around 2027",
            "Immediate profit increase this quarter",
            "Permanent reduction in all revenue",
            "Cancellation of the expansion plan",
        ],
        "answer": "After initial spending, benefits emerge around 2027",
        "explanation_zh": "Q2 capex peak / ROIC improve beginning 2027。",
    },
    {
        "format": "triple",
        "passages": [
            {
                "label": "Operations report",
                "text": (
                    "Semiconductor supply disruptions have delayed production schedules by up to "
                    "six weeks."
                ),
            },
            {
                "label": "Sales update",
                "text": (
                    "Key accounts have been notified; penalty clauses may apply if deliveries slip "
                    "beyond contracted dates."
                ),
            },
            {
                "label": "Executive decision log",
                "text": (
                    "Approved increased inventory buffers and dual sourcing despite an estimated "
                    "eight-percent rise in overhead."
                ),
            },
        ],
        "question": "What trade-off did executives accept?",
        "options": [
            "Higher costs to reduce delivery risk",
            "Lower quality to speed production",
            "Canceling all customer contracts",
            "Eliminating inventory entirely",
        ],
        "answer": "Higher costs to reduce delivery risk",
        "explanation_zh": "inventory buffers / eight-percent rise in overhead / penalty clauses。",
    },
    {
        "format": "triple",
        "passages": [
            {
                "label": "Job posting",
                "text": (
                    "Seeking a compliance officer to oversee reporting standards across three "
                    "jurisdictions."
                ),
            },
            {
                "label": "Audit finding",
                "text": (
                    "Documentation gaps were identified in two regional offices last quarter."
                ),
            },
            {
                "label": "Board minutes",
                "text": (
                    "Directors mandated completion of mandatory training for all transaction "
                    "processors by mid-March."
                ),
            },
        ],
        "question": "What organizational priority emerges from all three documents?",
        "options": [
            "Strengthening compliance and reporting controls",
            "Expanding into unrelated retail markets",
            "Eliminating all international operations",
            "Reducing training requirements",
        ],
        "answer": "Strengthening compliance and reporting controls",
        "explanation_zh": "compliance officer / documentation gaps / mandatory training。",
    },
    {
        "format": "triple",
        "passages": [
            {
                "label": "Energy bulletin",
                "text": "Exporting nations may extend production cuts, tightening global supply.",
            },
            {
                "label": "Economic survey",
                "text": (
                    "Import-dependent economies report mounting household cost pressures."
                ),
            },
            {
                "label": "Policy draft",
                "text": (
                    "Temporary subsidy programs are under consideration, though fiscal deficits "
                    "could widen substantially."
                ),
            },
        ],
        "question": "What concern connects all three texts?",
        "options": [
            "Rising energy costs burden consumers and government budgets",
            "Oil supply exceeds demand worldwide",
            "All subsidies have already been enacted",
            "Household costs are declining rapidly",
        ],
        "answer": "Rising energy costs burden consumers and government budgets",
        "explanation_zh": "production cuts / cost pressures / subsidies vs fiscal deficits。",
    },
]
