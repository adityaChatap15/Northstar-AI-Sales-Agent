import json

from app.services.llm import generate_response
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.tools.site_visit import book_site_visit


ACTION_MARKER = "ACTION_BOOK_VISIT:"


def chat(conversation):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation)

    reply = generate_response(messages)

    if ACTION_MARKER in reply:
        reply = _handle_booking_action(messages, reply)

    return reply


def _handle_booking_action(messages, reply):

    _, action_json = reply.split(ACTION_MARKER, 1)

    booking_details = _parse_action_json(action_json)

    if booking_details is None:
        # Could not parse the model's action, drop it and show nothing broken.
        return reply.split(ACTION_MARKER, 1)[0].strip()

    tool_result = book_site_visit(
        name=booking_details.get("name"),
        phone=booking_details.get("phone"),
        date=booking_details.get("date"),
        time=booking_details.get("time"),
        configuration=booking_details.get("configuration")
    )

    follow_up_messages = messages + [
        {
            "role": "system",
            "content": (
                "TOOL_RESULT for the site-visit booking attempt: "
                + json.dumps(tool_result)
                + ". Inform the customer of this outcome naturally, in the same "
                  "language they have been using. If it failed, explain why in "
                  "plain terms and offer an alternative. Do not mention the "
                  "word 'tool' and do not show any JSON to the customer. Reply "
                  "in plain spoken sentences only: no markdown, no bullet "
                  "points, no bold/asterisks, no headings. If a booking ID is "
                  "present, just say it as part of a normal sentence."
            )
        }
    ]

    return generate_response(follow_up_messages)


def _parse_action_json(action_json):

    try:
        return json.loads(action_json.strip())
    except (json.JSONDecodeError, AttributeError):
        return None
