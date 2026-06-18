from datetime import datetime
import pytz

def format_telegram_message(analysis: dict, macro: dict) -> str:
    """Format the Claude analysis into a crisp Telegram message."""

    now_et = datetime.now(pytz.timezone("America/New_York"))
    date_str = now_et.strftime("%B %d, %Y")

    # Sentiment emoji
    sentiment = analysis.get("overall_sentiment", "Neutral")
    confidence = analysis.get("sentiment_confidence", "Medium")
    sentiment_emoji = {"Bullish": "🟢", "Neutral": "🟡", "Bearish": "🔴"}.get(sentiment, "🟡")

    # Yield curve
    yc_signal = analysis.get("yield_curve_signal", "Unknown")
    yc_emoji  = {"Normal": "✅", "Flattening": "⚠️", "Inverted": "🚨"}.get(yc_signal, "❓")

    # Build macro signals section
    macro_signals = analysis.get("macro_signals", [])
    macro_lines = []
    for sig in macro_signals[:4]:   # cap at 4 to keep message short
        sig_emoji = {"Bullish": "🟢", "Neutral": "🟡", "Bearish": "🔴"}.get(sig.get("signal"), "🟡")
        macro_lines.append(f"  {sig_emoji} {sig.get('indicator')}: {sig.get('value')} — {sig.get('reason')}")
    macro_section = "\n".join(macro_lines)

    # Build swing opportunities section
    opportunities = analysis.get("swing_opportunities", [])
    opp_lines = []
    for opp in opportunities[:5]:   # cap at 5 stocks
        action = opp.get("action", "WATCH")
        conviction = opp.get("conviction", "Medium")
        action_emoji = {"BUY": "🟢", "AVOID": "🔴", "WATCH": "👀"}.get(action, "👀")
        opp_lines.append(
            f"  {action_emoji} *{opp.get('ticker')}* [{conviction}]\n"
            f"     {opp.get('reason')}\n"
            f"     Entry: {opp.get('entry_zone', 'N/A')} | Risk: {opp.get('risk', 'N/A')}"
        )
    opp_section = "\n\n".join(opp_lines)

    # Build sectors section
    sectors = analysis.get("sectors_to_watch", [])
    sector_lines = []
    for sec in sectors[:4]:
        bias_emoji = {"Positive": "🟢", "Neutral": "🟡", "Negative": "🔴"}.get(sec.get("bias"), "🟡")
        sector_lines.append(f"  {bias_emoji} {sec.get('sector')}: {sec.get('reason')}")
    sector_section = "\n".join(sector_lines)

    # Sentiment drivers
    drivers = analysis.get("market_sentiment_drivers", [])
    driver_lines = "\n".join([f"  • {d}" for d in drivers[:3]])

    # Bottom line
    bottom_line = analysis.get("bottom_line", "")

    # Yield curve spread from macro
    yc_spread = macro.get("yield_curve_spread")
    yc_spread_str = f"{yc_spread:+.2f}%" if yc_spread is not None else "N/A"

    message = f"""🇺🇸 *Market Pulse — {date_str}*
━━━━━━━━━━━━━━━━━━━━

{sentiment_emoji} *OVERALL: {sentiment}* (Confidence: {confidence})

📊 *MACRO SIGNALS*
{macro_section}

{yc_emoji} *Yield Curve ({yc_signal}):* {yc_spread_str} spread
_{analysis.get('yield_curve_implication', '')}_

🧠 *SENTIMENT DRIVERS*
{driver_lines}

📈 *SWING OPPORTUNITIES* _(2–4 week horizon)_
{opp_section}

🏭 *SECTORS*
{sector_section}

⚡ *BOTTOM LINE*
_{bottom_line}_

━━━━━━━━━━━━━━━━━━━━
_Signals only. Not financial advice. Always do your own research._"""

    return message


def format_audit_message(analysis: dict) -> str:
    """Separate shorter audit message showing Claude's reasoning — for transparency."""
    audit = analysis.get("audit_trail", {})
    analysed_at = analysis.get("analysed_at", "Unknown")

    macro_factors  = "\n".join([f"  • {f}" for f in audit.get("key_macro_factors_used", [])])
    news_factors   = "\n".join([f"  • {f}" for f in audit.get("key_news_factors_used", [])])
    tech_factors   = "\n".join([f"  • {f}" for f in audit.get("key_technical_factors_used", [])])
    caveats        = audit.get("analyst_confidence_notes", "None")

    return f"""🔍 *Market Pulse — Audit Trail*
_Analysed at {analysed_at} UTC_

*Macro factors used:*
{macro_factors}

*News factors used:*
{news_factors}

*Technical factors used:*
{tech_factors}

*Caveats:*
_{caveats}_"""