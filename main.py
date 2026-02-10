import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_functions import available_functions, call_function
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

# Set AI client
client = genai.Client(api_key=api_key)

got_final_answer = False


def main():
    for _ in range(20):
        function_call_results_list = []

        # Set AI messages and response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
                temperature=0,
            ),
        )

        usage_metadata = response.usage_metadata

        if usage_metadata == None:
            raise RuntimeError("API request failed")

        # Set metadata variables using response's metadata
        prompt_tokens = usage_metadata.prompt_token_count
        candidate_tokens = usage_metadata.candidates_token_count

        if response.candidates is not None:
            for candidate in response.candidates:
                messages.append(candidate.content)

        if response.function_calls:
            for function_call in response.function_calls:
                result = call_function(function_call, args.verbose)
                if (
                    result.parts is None
                    or result.parts[0].function_response is None
                    or result.parts[0].function_response.response is None
                ):
                    raise Exception(f"Empty function response for {function_call.name}")
                else:
                    function_call_results_list.append(result.parts[0])

            messages.append(
                types.Content(role="user", parts=function_call_results_list)
            )

            if args.verbose:
                print(
                    f"-> {result.parts[0].function_response.response}\n"
                    f"User prompt: {args.user_prompt}\n"
                    f"Prompt tokens: {prompt_tokens}\n"
                    f"Response tokens: {candidate_tokens}\n"
                )

        else:
            print(response.text)
            got_final_answer = True
            break

    if not got_final_answer:
        print("Agent hit max iterations without a final answer")
        sys.exit(1)


if __name__ == "__main__":
    main()
