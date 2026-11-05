import anthropic

client = anthropic.Anthropic()

# 1. System prompt: role + the allergy fact
SYSTEM_PROMPT = """You are a polite shoe shop assistant. Only talk about shoes:
styles, sizing, materials, care, and recommendations. Politely steer any other topic back to shoes.

Important customer fact: This customer is allergic to leather.
Never recommend leather shoes or leather parts (uppers, linings, insoles, trims)."""

history = []                                   # 2. memory

while True:
    user_message = input("You: ")
    if user_message.strip().lower() == "quit": # 6. exit
        break

    history.append({"role": "user", "content": user_message})

    # 3. last 6 messages, but the window must start with "user"
    recent = history[-6:]
    if recent[0]["role"] == "assistant":
        recent = recent[1:]

    # 4. stream word by word
    print("Claude: ", end="", flush=True)
    answer = ""
    with client.messages.stream(
        model="claude-opus-5-5",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=recent,
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
            answer += chunk                    # Option 1: collect chunks

        if stream.get_final_message().stop_reason == "max_tokens":
            answer += " [WARNING: cut off]"
            print(" [WARNING: cut off]", end="")

    print("\n")
    history.append({"role": "assistant", "content": answer})   # 5. save
