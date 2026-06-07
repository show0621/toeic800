"""多益800+ 級單字釋義（優先於通用字典的第一義）。"""

from __future__ import annotations



from typing import Any



# 考場常見語意：英文解釋 + 繁中

TOEIC_GLOSSARY: dict[str, dict[str, str]] = {

    "slump": {"meaning_en": "a sudden sharp decline (in prices, sales, or activity)", "meaning_zh": "驟跌；衰退；低迷"},

    "inflation": {"meaning_en": "a sustained increase in the general price level", "meaning_zh": "通貨膨脹"},

    "volatility": {"meaning_en": "the degree of variation in market prices over time", "meaning_zh": "波動性；劇烈起伏"},

    "merger": {"meaning_en": "the combination of two companies into one entity", "meaning_zh": "合併；併購"},

    "acquisition": {"meaning_en": "the purchase of one company by another", "meaning_zh": "收購"},

    "dividend": {"meaning_en": "a portion of corporate profits paid to shareholders", "meaning_zh": "股利；股息"},

    "recession": {"meaning_en": "a prolonged period of economic decline", "meaning_zh": "經濟衰退"},

    "tariff": {"meaning_en": "a tax imposed on imported or exported goods", "meaning_zh": "關稅"},

    "sanction": {"meaning_en": "a penalty restricting trade or financial activity", "meaning_zh": "制裁"},

    "forecast": {"meaning_en": "a prediction of future financial or economic results", "meaning_zh": "預測；展望"},

    "surge": {"meaning_en": "a sudden large increase", "meaning_zh": "激增；飆升"},

    "plunge": {"meaning_en": "to fall suddenly and sharply", "meaning_zh": "暴跌；驟降"},

    "rally": {"meaning_en": "a recovery or upward movement in prices", "meaning_zh": "反彈；回升"},

    "portfolio": {"meaning_en": "a collection of financial investments held by an investor", "meaning_zh": "投資組合"},

    "liquidity": {"meaning_en": "the availability of cash or easily converted assets", "meaning_zh": "流動性"},

    "leverage": {"meaning_en": "using borrowed capital to increase potential returns", "meaning_zh": "槓桿；舉債經營"},

    "compliance": {"meaning_en": "adherence to laws, regulations, and internal policies", "meaning_zh": "合規；遵循法規"},

    "procurement": {"meaning_en": "the process of obtaining goods or services for a business", "meaning_zh": "採購"},

    "infrastructure": {"meaning_en": "basic physical and organizational systems (transport, utilities)", "meaning_zh": "基礎建設"},

    "consolidate": {"meaning_en": "to combine or strengthen into a more effective whole", "meaning_zh": "整合；合併"},

    "mitigate": {"meaning_en": "to make a risk or negative effect less severe", "meaning_zh": "減輕；緩和"},

    "exacerbate": {"meaning_en": "to make a problem or situation worse", "meaning_zh": "加劇；惡化"},

    "substantial": {"meaning_en": "large in amount, value, or importance", "meaning_zh": "大量的；重大的"},

    "unprecedented": {"meaning_en": "never done or known before", "meaning_zh": "前所未有的"},

    "regulatory": {"meaning_en": "relating to rules set by government authorities", "meaning_zh": "監管的；法規的"},

    "shareholder": {"meaning_en": "an owner of shares in a company", "meaning_zh": "股東"},

    "default": {"meaning_en": "failure to fulfill a financial obligation", "meaning_zh": "違約；不履行"},

    "stimulus": {"meaning_en": "government spending or policy to boost economic activity", "meaning_zh": "刺激（方案）"},

    "sentiment": {"meaning_en": "the overall attitude or mood of investors or consumers", "meaning_zh": "市場情緒；觀感"},

    "benchmark": {"meaning_en": "a standard used to measure performance", "meaning_zh": "基準；標竿"},

    "commodity": {"meaning_en": "a basic good traded on markets (oil, metals, crops)", "meaning_zh": "大宗商品"},

    "earnings": {"meaning_en": "a company's profit for a given period", "meaning_zh": "盈餘；收益"},

    "revenue": {"meaning_en": "income generated from business operations", "meaning_zh": "營收"},

    "equity": {"meaning_en": "ownership interest in a company; or stocks as an asset class", "meaning_zh": "股權；股票"},

    "yield": {"meaning_en": "the return on an investment, often expressed as a percentage", "meaning_zh": "收益率；殖利率"},

    "hedge": {"meaning_en": "to protect against financial loss using offsetting investments", "meaning_zh": "避險"},

    "derivative": {"meaning_en": "a financial contract whose value depends on an underlying asset", "meaning_zh": "衍生性商品"},

    "capital": {"meaning_en": "financial assets available for investment or operations", "meaning_zh": "資本；資金"},

    "speculation": {"meaning_en": "high-risk investment based on expected price changes", "meaning_zh": "投機"},

    "depreciation": {"meaning_en": "a decrease in the value of an asset over time", "meaning_zh": "折舊；貶值"},

    "appreciation": {"meaning_en": "an increase in the value of an asset or currency", "meaning_zh": "升值；增值"},

    "collateral": {"meaning_en": "property pledged as security for a loan", "meaning_zh": "抵押品；擔保"},

    "bankruptcy": {"meaning_en": "legal status when a debtor cannot repay obligations", "meaning_zh": "破產"},

    "austerity": {"meaning_en": "strict economic measures to reduce government debt", "meaning_zh": "緊縮（政策）"},

    "embargo": {"meaning_en": "an official ban on trade with a particular country", "meaning_zh": "禁運；貿易禁令"},

    "geopolitical": {"meaning_en": "relating to politics influenced by geography and national interests", "meaning_zh": "地緣政治的"},

    "fluctuation": {"meaning_en": "irregular rises and falls in level or value", "meaning_zh": "波動；起伏"},

    "intervention": {"meaning_en": "action by authorities to influence markets or policy", "meaning_zh": "干預"},

    "transparency": {"meaning_en": "openness in business or government operations", "meaning_zh": "透明度"},

    "accountability": {"meaning_en": "responsibility to report and justify decisions", "meaning_zh": "問責；可究責性"},

    "overhaul": {"meaning_en": "a thorough revision or restructuring", "meaning_zh": "全面改革；大修"},

    "restructure": {"meaning_en": "to reorganize a company to improve efficiency or finances", "meaning_zh": "重組"},

    "bailout": {"meaning_en": "financial rescue of a failing company or economy", "meaning_zh": "紓困；救助"},

    "downgrade": {"meaning_en": "to lower a credit rating or classification", "meaning_zh": "降評；下調"},

    "headwind": {"meaning_en": "a factor that slows progress or growth", "meaning_zh": "逆風；不利因素"},

    "tailwind": {"meaning_en": "a factor that helps progress or growth", "meaning_zh": "順風；有利因素"},

    "macroeconomic": {"meaning_en": "relating to the economy as a whole", "meaning_zh": "總體經濟的"},

    "legislation": {"meaning_en": "laws enacted by a legislative body", "meaning_zh": "立法；法規"},

    "diplomatic": {"meaning_en": "relating to international relations and negotiations", "meaning_zh": "外交的"},

    "consensus": {"meaning_en": "general agreement among a group", "meaning_zh": "共識"},

    "skeptic": {"meaning_en": "a person who doubts or questions claims", "meaning_zh": "懷疑論者；持疑者"},

    "robust": {"meaning_en": "strong and healthy; showing vigor", "meaning_zh": "強勁的；穩健的"},

    "sluggish": {"meaning_en": "slow-moving; lacking energy or growth", "meaning_zh": "遲緩的；疲弱的"},

    "escalate": {"meaning_en": "to increase in intensity or scope", "meaning_zh": "升級；加劇"},

    "alleviate": {"meaning_en": "to make suffering or a problem less severe", "meaning_zh": "緩解；減輕"},

    "jeopardize": {"meaning_en": "to put at risk of harm or loss", "meaning_zh": "危及；損及"},

    "undermine": {"meaning_en": "to weaken gradually or indirectly", "meaning_zh": "削弱；破壞"},

    "bolster": {"meaning_en": "to support or strengthen", "meaning_zh": "支撐；加強"},

    "scrutinize": {"meaning_en": "to examine closely and critically", "meaning_zh": "審查；詳查"},

    "formidable": {"meaning_en": "inspiring respect through size, ability, or difficulty", "meaning_zh": "強大的；難對付的"},

    "plausible": {"meaning_en": "seeming reasonable or believable", "meaning_zh": "貌似合理的；可信的"},

    "likelihood": {"meaning_en": "the probability that something will happen", "meaning_zh": "可能性"},

    "overvalued": {"meaning_en": "priced higher than fundamental value suggests", "meaning_zh": "估值過高"},

    "vulnerable": {"meaning_en": "exposed to harm, risk, or attack", "meaning_zh": "脆弱的；易受影響的"},

    "sustainable": {"meaning_en": "able to be maintained over the long term", "meaning_zh": "可持續的"},

    "mounting": {"meaning_en": "gradually increasing", "meaning_zh": "日益增加的"},

    "stake": {"meaning_en": "a share or interest in a business venture", "meaning_zh": "股權；利害關係"},

    "executive": {"meaning_en": "a senior manager in an organization", "meaning_zh": "高階主管"},

    "debut": {"meaning_en": "a first public appearance or launch", "meaning_zh": "首次亮相；上市"},

    "sell-off": {"meaning_en": "rapid selling of assets, often causing prices to fall", "meaning_zh": "拋售"},

    "investor": {"meaning_en": "a person or institution that puts money into assets for profit", "meaning_zh": "投資人"},

    "borrowing": {"meaning_en": "the act of taking loans; debt financing", "meaning_zh": "借款；舉債"},

    "utilities": {"meaning_en": "companies providing essential services (power, water)", "meaning_zh": "公用事業"},

    "staples": {"meaning_en": "basic necessary goods (food, household items)", "meaning_zh": "民生必需品"},

    "emphasis": {"meaning_en": "special importance placed on something", "meaning_zh": "強調；重點"},

    "acquiring": {"meaning_en": "obtaining or purchasing (often another company)", "meaning_zh": "收購；取得"},

}





def apply_glossary(word: str, info: dict[str, Any]) -> dict[str, Any]:

    """若詞彙在考場詞庫中，覆蓋過於簡單的字典釋義。"""

    g = TOEIC_GLOSSARY.get(word.lower().strip())

    if not g:

        return info

    out = dict(info)

    out["meaning_en"] = g["meaning_en"]

    out["meaning_zh"] = g["meaning_zh"]

    return out


