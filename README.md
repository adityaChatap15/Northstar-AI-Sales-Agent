# Northstar AI Sales Agent

An AI conversational sales agent for **Northstar Homes** (fictional real-estate
company), built for the Huvo AI Forward Deployed Engineer assignment.

The agent handles natural conversation, lead qualification, objections,
Hindi/Hinglish/English, site-visit booking (with simulated success/failure),
human escalation, and conversation-ending, using a single system prompt
designed to work for both chat and voice/calling use cases.

Backend: **FastAPI (Python)**. Frontend: a small static HTML/CSS/JS chat page
served by the same FastAPI app (no build tooling, no framework).

## Project structure

```
app/
  main.py                  FastAPI app entrypoint, serves the frontend + API
  models/schemas.py        Pydantic request/response models
  prompts/system_prompt.py The final system prompt (chat + voice)
  routes/chat.py           /api/chat, /api/analytics, /api/session endpoints
  services/llm.py          Gemini (OpenAI-compatible) client wrapper
  services/agent.py        Conversation orchestration + booking-action handling
  services/analytics.py    Post-conversation analytics extraction
  tools/site_visit.py      Simulated site-visit booking tool
frontend/
  index.html               Chat UI page
  style.css                 Styling (light/dark aware)
  script.js                  Vanilla JS: sends messages, shows analytics
tests/test_cases.py        Scenario walkthroughs (input / expected / actual)
```

## How it works

- Each turn, the full conversation history plus the system prompt is sent to
  the model, so the agent naturally remembers everything shared earlier in
  the session (no separate memory store needed).
- When the agent has collected enough details for a site visit (name, phone,
  date, time), the prompt instructs it to emit a line like
  `ACTION_BOOK_VISIT: {"name": ..., "date": ..., "time": ...}`. The backend
  (`app/services/agent.py`) detects this, calls the simulated booking tool
  in `app/tools/site_visit.py`, and feeds the real result back to the model
  as a `TOOL_RESULT` message so it can confirm or explain a failure in the
  customer's own words. The agent never announces success/failure on its own.
- The booking tool is a plain deterministic simulation: it rejects missing
  fields, past dates, Sundays (closed), and a couple of hardcoded
  already-booked slots, so booking failures are reproducible for testing.
- After a conversation ends, `GET /api/analytics/{session_id}` sends the full
  transcript back through the model with a separate extraction prompt and
  returns structured JSON: budget, configuration interest, purpose, timeline,
  interest level, site-visit status, follow-up requirement, opt-out flag,
  escalation flag, and a short summary.

## API endpoints

| Method | Path                        | Purpose                                   |
|--------|-----------------------------|--------------------------------------------|
| POST   | `/api/chat`                 | Send a customer message, get the agent's reply |
| GET    | `/api/analytics/{session_id}` | Generate analytics for a finished conversation |
| DELETE | `/api/session/{session_id}` | Clear a session's history                 |

`POST /api/chat` body:
```json
{ "session_id": "abc123", "message": "Hi, tell me about Northstar One" }
```

## How to run

```bash
# from the project root
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

copy .env.example .env       # then fill in your own GEMINI_API_KEY
# cp .env.example .env

uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in a browser for the chat UI. Interactive API
docs are at `http://127.0.0.1:8000/docs`.

### Running the test scenarios

```bash
python -m tests.test_cases
```

This drives the agent in-process through several scenarios (English inquiry,
Hinglish objection, busy customer, "contact me later", opt-out, unknown
question, human escalation, and both a successful and a failed site-visit
booking), printing the input, the expected behaviour, and the agent's actual
reply for each, followed by a sample analytics extraction.

## Key assumptions

- Session state (conversation history) is kept in memory (a plain dict) for
  simplicity, since this is a demo assignment, not a production deployment.
  It resets if the server restarts.
- The site-visit "calendar" is fully simulated in `app/tools/site_visit.py`
  (no real scheduling system) with a small hardcoded set of already-booked
  slots and Sundays closed, purely to make success/failure paths testable.
- Analytics are generated on-demand per session (via the `/api/analytics`
  endpoint) rather than after every single turn, since the assignment asks
  for analytics "after the conversation ends."
- The model used is Gemini, called through Google's OpenAI-compatible
  endpoint, configurable via `GEMINI_MODEL` in `.env` (default
  `gemini-3.6-flash`).

## Known limitations

- No persistent database; all conversation state is lost on restart.
- The booking tool is a simulation, not a real calendar integration.
- Voice input/output (speech-to-text / text-to-speech) is not implemented;
  the prompt is written to be voice-compatible (plain sentences, no
  markdown), but this project only exercises it over text.
- Analytics extraction relies on the model returning valid JSON; if it
  doesn't, the endpoint returns a raw-output fallback instead of throwing.
- The frontend is intentionally minimal (plain HTML/CSS/JS, no framework,
  no build step) — a chat window, a "New Conversation" button, and an
  "End Chat & View Analytics" button. It talks to the same FastAPI backend
  over `fetch()`.
- The Gemini free tier is limited to 5 requests/minute; `app/services/llm.py`
  retries once on a 429 with a short backoff, but sustained rapid testing
  (e.g. running the full test script back-to-back) can still hit the limit.

## AI tools used

Claude (Anthropic) was used as a coding assistant to help implement the
backend (agent orchestration, booking tool, analytics extraction, and test
scenarios) on top of an existing project skeleton, and to refine the system
prompt.
