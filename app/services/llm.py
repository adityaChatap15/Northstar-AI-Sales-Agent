from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os
import time


load_dotenv()


client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 20


def generate_response(messages):

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.4
            )

            return response.choices[0].message.content

        except RateLimitError:
            if attempt == MAX_RETRIES:
                raise

            time.sleep(RETRY_WAIT_SECONDS)
