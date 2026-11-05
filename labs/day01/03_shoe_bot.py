import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your environment

# 1. System prompt: polite shoe shop bot that only talks about shoes
SYSTEM_PROMPT = """You are a polite customer service assistant for a shoe shop.
Only talk about shoes: styles, sizing, materials, care, and recommendations.
If the customer asks about anything else, politely decline and steer the
conversation back to shoes."""

# 2. Send the customer message
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": "Tell me a joke about cats."}],
)

# 3. Check whether the answer was cut off
if response.stop_reason == "max_tokens":
    print("Warning: answer was cut off!")

# 4. Print Claude's answer (keep only text blocks; Opus 5.5 may also return thinking blocks)
answer = "".join(block.text for block in response.content if block.type == "text")
print(answer)

# 5. Print token usage
print(f"Input tokens:  {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
