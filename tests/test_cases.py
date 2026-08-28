"""
Simple, runnable demonstration script for the Northstar AI Sales Agent.

This is not a pytest suite. It drives the agent in-process, turn by turn,
for a handful of realistic scenarios, and prints the input, what we expect
the agent to do, and what it actually replied -- plus a basic heuristic
check where one is easy to state (e.g. "must not claim booking succeeded").

Run from the project root with:

    python -m tests.test_cases

Requires a valid GEMINI_API_KEY in your .env file, since it makes real
calls to the model.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.agent import chat
from app.services.analytics import generate_analytics


def run_conversation(title, turns, expectation, check=None):

    print("=" * 70)
    print(f"TEST: {title}")
    print(f"EXPECTED BEHAVIOUR: {expectation}")
    print("-" * 70)

    conversation = []
    last_reply = None

    for user_message in turns:
        print(f"Customer: {user_message}")

        conversation.append({"role": "user", "content": user_message})
        reply = chat(conversation)
        conversation.append({"role": "assistant", "content": reply})

        print(f"Agent: {reply}")
        last_reply = reply

    if check is not None:
        result = "PASS" if check(last_reply, conversation) else "CHECK MANUALLY"
        print(f"HEURISTIC CHECK: {result}")

    print()

    return conversation


def main():

    conversations = {}

    conversations["english_inquiry"] = run_conversation(
        title="English inquiry and lead qualification",
        turns=[
            "Hi, I saw an ad for Northstar One. What's the price for a 3 BHK?",
            "That works for my budget. It's for my own family to live in.",
        ],
        expectation=(
            "Agent answers with the real 3 BHK starting price (Rs 1.75 crore "
            "onwards), and naturally gathers qualification info (purpose) "
            "without interrogating the customer."
        ),
        check=lambda reply, conv: "1.75" in "".join(
            m["content"] for m in conv if m["role"] == "assistant"
        ),
    )

    conversations["hinglish_objection"] = run_conversation(
        title="Hinglish objection handling",
        turns=[
            "2 BHK ka price kya hai Northstar One mein?",
            "Yeh to bahut zyada hai yaar, itna budget nahi hai mera.",
        ],
        expectation=(
            "Agent responds in Hinglish, acknowledges the price objection "
            "respectfully, does not invent a discount, and offers a useful "
            "next step."
        ),
    )

    conversations["busy_customer"] = run_conversation(
        title="Busy customer",
        turns=[
            "Hi",
            "Sorry, main abhi meeting mein hoon, busy hoon.",
        ],
        expectation=(
            "Agent respects that the customer is busy, stops asking sales "
            "questions, and offers to follow up later instead of pushing."
        ),
    )

    conversations["contact_later"] = run_conversation(
        title="Request to contact later",
        turns=[
            "I'm interested in the 2 BHK but call me next week instead, "
            "I can't talk right now.",
        ],
        expectation=(
            "Agent acknowledges the request, confirms/asks a suitable "
            "follow-up time, and does not continue qualification questions "
            "in this turn."
        ),
    )

    conversations["opt_out"] = run_conversation(
        title="Stop communication request",
        turns=[
            "Please stop messaging me, I don't want to be contacted about "
            "this again.",
        ],
        expectation=(
            "Agent immediately respects the request, does not continue "
            "sales messaging, and ends the conversation politely."
        ),
    )

    conversations["unknown_question"] = run_conversation(
        title="Unknown question",
        turns=[
            "Does Northstar One have a rooftop swimming pool and when is "
            "possession?",
        ],
        expectation=(
            "Agent does not invent amenity or possession details that were "
            "never provided; it clearly says it doesn't have that specific "
            "information and offers to follow up."
        ),
    )

    conversations["human_escalation"] = run_conversation(
        title="Human escalation",
        turns=[
            "I want to speak to an actual human sales manager, not a bot.",
        ],
        expectation=(
            "Agent acknowledges the request and notes it for human "
            "follow-up, without inventing a name or response time."
        ),
    )

    conversations["booking_success"] = run_conversation(
        title="Site-visit booking (success path)",
        turns=[
            "I'd like to book a site visit for the 3 BHK.",
            "My name is Rahul Sharma, phone is 9876543210.",
            "Let's do 2026-09-05 at 11:00 AM.",
        ],
        expectation=(
            "Agent collects name, phone, date and time, then confirms a "
            "real booking (since this slot is not in the simulated "
            "already-booked list and is not a Sunday)."
        ),
        check=lambda reply, conv: "confirm" in reply.lower()
        or "book" in reply.lower(),
    )

    conversations["booking_failure"] = run_conversation(
        title="Site-visit booking (failure path - already booked slot)",
        turns=[
            "I want to visit the property.",
            "Name: Priya Verma, phone: 9123456780.",
            "Can we do 2026-08-30 at 11:00 AM?",
        ],
        expectation=(
            "This exact slot is pre-marked as already booked in the "
            "simulated calendar. Agent must NOT claim success; it should "
            "explain the slot is unavailable and offer an alternative."
        ),
        check=lambda reply, conv: "confirmed" not in reply.lower(),
    )

    print("#" * 70)
    print("ANALYTICS GENERATION (example: booking_success conversation)")
    print("#" * 70)

    analytics = generate_analytics(conversations["booking_success"])

    print(analytics)


if __name__ == "__main__":
    main()
