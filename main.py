import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

import call_functions as call
from prompts import system_prompt

# Set API key from user environment
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key == None:
    raise RuntimeError("Missing API key")

# Set args variable to with argparser
parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

# Create a list of messages and responses from argparser
messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

# Set AI client and response
client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
    config=types.GenerateContentConfig(
        tools=[call.available_functions],
        system_instruction=system_prompt,
        temperature=0,
    ),
)

# Set metadata variables using response's metadata
usage_metadata = response.usage_metadata
prompt_tokens = response.usage_metadata.prompt_token_count
candidate_tokens = response.usage_metadata.candidates_token_count


def main():
    if usage_metadata == None:
        raise RuntimeError("API request failed")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {candidate_tokens}")

    if response.function_calls != None:
        for call in response.function_calls:
            print(f"Calling function: {call.name}({call.args})")
    else:
        print(response.text)


if __name__ == "__main__":
    main()
