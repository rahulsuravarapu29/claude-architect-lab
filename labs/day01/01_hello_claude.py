"""
Day 01 - Lesson 1: Your first Claude API call.

Run:  .venv/bin/python labs/day01/01_hello_claude.py
Needs: ANTHROPIC_API_KEY set in your environment.
"""

import anthropic

# 1. Create a client. It reads ANTHROPIC_API_KEY from your environment
#    automatically, so you never write the key in code.
client = anthropic.Anthropic()

# 2. Send a message. Every Claude request goes to one endpoint: Messages.
response = client.beta.messages.create(
    model="claude-opus-5-5",   # which model answers
    max_tokens=16000,          # upper limit on the reply length (in tokens)
    system="You are a friendly tutor. Answer in 3 short sentences.",  # sets behavior
    messages=[                 # the conversation so far
        {"role": "user", "content": "What is an LLM, explained for a web developer?"}
    ],
    # Safety net: if the model declines a request, the API retries it on a
    # fallback model for you. ("beta" features need the betas=[...] flag.)
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
)

# 3. Check WHY the model stopped before trusting the output.
#    "end_turn" = finished normally, "max_tokens" = got cut off, "refusal" = declined.
print("stop_reason:", response.stop_reason)

# 4. The reply is a LIST of content blocks (text, thinking, tool calls...).
#    We only print the text blocks.
for block in response.content:
    if block.type == "text":
        print("\nClaude says:\n" + block.text)

# 5. Usage = what you're billed for. Tokens are roughly 3/4 of a word.
print("\n--- usage ---")
print("input tokens: ", response.usage.input_tokens)
print("output tokens:", response.usage.output_tokens)
