"""
LLM Formatter — converts raw backend data into a friendly sentence.

Tries to call the configured LLM API. On ANY failure (missing key,
timeout, rate limit, quota), falls back silently to a template string.
"""

import os


def format_status(rooms: list) -> str:
    """Format full office status for !status command.
    Always shows structured data first, then appends a conversational LLM summary.
    """
    structured = _template_status(rooms)
    try:
        conversational = _llm_format_status(rooms)
        return f"{structured}\n\n💬 *{conversational}*"
    except Exception as e:
        print(f"[LLM] Fallback triggered: {e}")
        return structured


def format_room(room: dict) -> str:
    """Format a single room summary for !room command.
    Always shows structured data first, then appends a conversational LLM summary.
    """
    structured = _template_room(room)
    try:
        conversational = _llm_format_room(room)
        return f"{structured}\n\n💬 *{conversational}*"
    except Exception as e:
        print(f"[LLM] Fallback triggered: {e}")
        return structured


def format_usage(current: dict, today: dict) -> str:
    """Format usage summary for !usage command.
    Always shows structured data first, then appends a conversational LLM summary.
    """
    structured = _template_usage(current, today)
    try:
        conversational = _llm_format_usage(current, today)
        return f"{structured}\n\n💬 *{conversational}*"
    except Exception as e:
        print(f"[LLM] Fallback triggered: {e}")
        return structured



# ── Template fallbacks (always work, zero dependencies) ──────────────────────

def _template_status(rooms: list) -> str:
    lines = ["📊 **Office Status**"]
    for room in rooms:
        devices = room.get("devices", [])
        fans_on = sum(1 for d in devices if d["type"] == "fan" and d["status"])
        lights_on = sum(1 for d in devices if d["type"] == "light" and d["status"])
        watts = room.get("total_watts", 0)
        lines.append(
            f"**{room['name']}**: {fans_on} fan(s) ON, {lights_on} light(s) ON — {watts}W"
        )
    return "\n".join(lines)


def _template_room(room: dict) -> str:
    devices = room.get("devices", [])
    fans_on = sum(1 for d in devices if d["type"] == "fan" and d["status"])
    fans_off = sum(1 for d in devices if d["type"] == "fan" and not d["status"])
    lights_on = sum(1 for d in devices if d["type"] == "light" and d["status"])
    lights_off = sum(1 for d in devices if d["type"] == "light" and not d["status"])
    watts = room.get("total_watts", 0)
    return (
        f"💡 **{room['name']}**\n"
        f"Fans: {fans_on} ON / {fans_off} OFF\n"
        f"Lights: {lights_on} ON / {lights_off} OFF\n"
        f"Current draw: **{watts}W**"
    )


def _template_usage(current: dict, today: dict) -> str:
    total_watts = current.get("total_watts", 0)
    kwh = today.get("estimated_kwh", 0.0)
    return (
        f"⚡ **Power Usage**\n"
        f"Right now: **{total_watts}W**\n"
        f"Today's estimate: **{kwh:.3f} kWh**"
    )


# ── LLM wrappers ─────────────────────────────────────────────────────────────

def _build_prompt(context: str) -> str:
    return (
        "You are a helpful assistant for an office IoT monitoring system. "
        "Reply in 1–3 natural, friendly sentences. No bullet points. No JSON. "
        "Always format any estimated energy consumption (kWh) with exactly three decimal places (e.g. 0.415 kWh). "
        f"Data: {context}"
    )


def _call_llm(prompt: str) -> str:
    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        raise ValueError("LLM_API_KEY not set")

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-latest")
    resp = model.generate_content(prompt)
    return resp.text.strip()


def _llm_format_status(rooms: list) -> str:
    return _call_llm(_build_prompt(f"Office rooms: {rooms}"))


def _llm_format_room(room: dict) -> str:
    return _call_llm(_build_prompt(f"Room details: {room}"))


def _llm_format_usage(current: dict, today: dict) -> str:
    return _call_llm(_build_prompt(f"Current usage: {current}, Today: {today}"))
