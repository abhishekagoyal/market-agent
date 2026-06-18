import os
import json
import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """You are a senior market analyst specialising in US equities and macro economics. 
You analyse data objectively and provide crisp, actionable swing trade insights (2-4 week horizon).
You always show your reasoning transparently so the reader can verify your conclusions.
You never give financial advice — you present signals and let the reader decide.
Always respond in the exact JSON format requested."""

def build_analysis_prompt(macro: dict, stocks: dict, news_headlines: list) -> str:
    return f"""Analyse the following market data and produce a structured market pulse report.

## MACRO DATA
{json.dumps(macro, indent=2)}

## STOCK DATA  
{json.dumps(stocks, indent=2)}

## RECENT NEWS HEADLINES
{json.dumps(news_headlines, indent=2)}

## YOUR TASK
Produce a JSON response with exactly this structure:
{{
  "overall_sentiment": "Bullish | Neutral | Bearish",
  "sentiment_confidence": "High | Medium | Low",
  "macro_summary": "2-3 sentence summary of macro environment",
  "macro_signals": [
    {{"indicator": "Fed Funds Rate", "value": "X%", "signal": "Bullish | Neutral | Bearish", "reason": "one line"}}
  ],
  "yield_curve_signal": "Normal | Flattening | Inverted",
  "yield_curve_implication": "one line implication for equities",
  "market_sentiment_drivers": ["driver 1", "driver 2", "driver 3"],
  "swing_opportunities": [
    {{
      "ticker": "$NVDA",
      "action": "BUY | AVOID | WATCH",
      "conviction": "High | Medium | Low",
      "reason": "2-3 sentences covering technicals + macro + news catalyst",
      "entry_zone": "price range to consider entry",
      "risk": "key risk to this thesis"
    }}
  ],
  "sectors_to_watch": [
    {{"sector": "Technology", "bias": "Positive | Neutral | Negative", "reason": "one line"}}
  ],
  "bottom_line": "2-3 sentence crisp summary a trader can act on",
  "audit_trail": {{
    "key_macro_factors_used": ["factor 1", "factor 2"],
    "key_news_factors_used": ["headline 1", "headline 2"],
    "key_technical_factors_used": ["factor 1", "factor 2"],
    "analyst_confidence_notes": "any caveats or data quality notes"
  }}
}}

Return ONLY the JSON. No preamble, no markdown, no explanation."""


def analyse(macro: dict, stocks: dict, news_headlines: list = []) -> dict:
    """Run Claude analysis on macro + stock + news data."""
    prompt = build_analysis_prompt(macro, stocks, news_headlines)
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        result["analysed_at"] = datetime.utcnow().isoformat()
        return result
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw_response": raw}
    except Exception as e:
        return {"error": str(e)}