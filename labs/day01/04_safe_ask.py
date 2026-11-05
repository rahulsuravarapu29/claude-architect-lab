import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your environment


def ask(question, system_prompt):
    # 1 + 2. Call Claude with adaptive thinking, the system prompt, and the question
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )

    # 3. Keep only text blocks (skips thinking blocks); never rely on content[0]
    answer = "".join(block.text for block in response.content if block.type == "text")

    # 4. Flag answers that hit the token limit
    if response.stop_reason == "max_tokens":
        answer += " [WARNING: cut off]"

    # 5. Return the answer so the caller decides what to do with it
    return answer


PIRATE = "You are a pirate captain. Answer everything in pirate speak, in 3 sentences max."
INTERVIEWER = "You are a strict Google interviewer. Answer precisely, then ask one follow-up question."

pirate_answer = ask("What is Python?", PIRATE)
interviewer_answer = ask("What is Python?", INTERVIEWER)

print("=== PIRATE ===")
print(pirate_answer)
print()
print("=== GOOGLE INTERVIEWER ===")
print(interviewer_answer)
