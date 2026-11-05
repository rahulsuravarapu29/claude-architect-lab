import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your environment

# 1. Start with an empty history
history = []

# 2. Loop forever
while True:
    # 3. Get the user's message
    user_message = input("You: ")

    # 4. Stop when the user types quit
    if user_message.strip().lower() == "quit":
        break

    # 5. Add the user message to history
    history.append({"role": "user", "content": user_message})

    # 6. Send the WHOLE history (the API is stateless)
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        messages=history,
    )

    # 7. Keep only the text blocks
    answer = "".join(block.text for block in response.content if block.type == "text")

    # 8. Print Claude's answer
    print(f"Claude: {answer}\n")

    # 9. Add Claude's answer to history so the next turn remembers it
    history.append({"role": "assistant", "content": answer})
