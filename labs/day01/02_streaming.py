"""
Day 01 - Lesson 2: Streaming (the "typing effect" you see in chat apps).

Without streaming you wait for the WHOLE reply. With streaming, text arrives
piece by piece as it's generated, so users see output immediately.

Run:  .venv/bin/python labs/day01/02_streaming.py
"""

import anthropic

client = anthropic.Anthropic()

# `with ... as stream` opens a live connection and closes it cleanly at the end.
with client.beta.messages.stream(
    model="claude-opus-5-5",
    max_tokens=64000,  # streaming can safely use a high limit (no request timeout)
    messages=[
        {"role": "user", "content": "Write a 5-step roadmap to go from full-stack dev to AI engineer."}
    ],
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
) as stream:
    # text_stream yields small chunks of text as they arrive.
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)  # flush = show it right away

    # After the stream ends, grab the complete message (same shape as lesson 1).
    final = stream.get_final_message()

print("\n\n--- usage ---")
print("stop_reason:  ", final.stop_reason)
print("input tokens: ", final.usage.input_tokens)
print("output tokens:", final.usage.output_tokens)
