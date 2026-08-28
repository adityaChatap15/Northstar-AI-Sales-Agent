import json

from app.services.llm import generate_response


ANALYTICS_PROMPT = """
You are a data-extraction assistant. You will be given a conversation
between an AI real-estate sales agent (Northstar Homes) and a customer.

Read the full conversation and return ONLY a valid JSON object (no markdown,
no code fences, no extra text) with exactly these fields:

{
  "budget_mentioned": string or null,
  "configuration_interest": "2 BHK" or "3 BHK" or "undecided" or null,
  "purpose": "self-use" or "investment" or null,
  "timeline": string or null,
  "interest_level": "high" or "medium" or "low" or "not interested",
  "site_visit_status": "booked" or "attempted_failed" or "not requested",
  "follow_up_required": true or false,
  "opted_out": true or false,
  "escalation_requested": true or false,
  "summary": "one or two sentence summary of the conversation"
}

Only use information present in the conversation. Use null or false when
information is not available. Do not invent details.
"""


def generate_analytics(conversation):

    transcript = _format_transcript(conversation)

    messages = [
        {"role": "system", "content": ANALYTICS_PROMPT},
        {"role": "user", "content": transcript}
    ]

    raw_output = generate_response(messages)

    return _parse_analytics(raw_output)


def _format_transcript(conversation):

    lines = []

    for turn in conversation:
        speaker = "Customer" if turn["role"] == "user" else "Agent"
        lines.append(f"{speaker}: {turn['content']}")

    return "\n".join(lines)


def _parse_analytics(raw_output):

    cleaned = raw_output.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "error": "Could not parse analytics output.",
            "raw_output": raw_output
        }
