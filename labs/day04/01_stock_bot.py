import anthropic

client = anthropic.Anthropic()

INVENTORY = {("nike pegasus", 10): 3, ("nike pegasus", 11): 0, ("adidas ultraboost", 10): 5}

def check_stock(product, size):
    return INVENTORY.get((product.lower(), size), 0)

TOOLS = [{
    "name": "check_stock",
    "description": "Check how many pairs of a shoe are in stock for ONE product and ONE size. "
                   "Call it once per size. Returns the number of pairs (0 means out of stock).",
    "input_schema": {
        "type": "object",
        "properties": {
            "product": {"type": "string", "description": "Brand and model, e.g. 'Nike Pegasus'"},
            "size": {"type": "number", "description": "US shoe size, e.g. 10"},
        },
        "required": ["product", "size"],
    },
}]

SYSTEM_PROMPT = "You are a shoe shop assistant. Use check_stock to answer stock questions. Never guess stock."

history = [{"role": "user", "content": "Do you have the Nike Pegasus in size 10 and 11?"}]

while True:
    response = client.messages.create(
        model="claude-opus-5-5", max_tokens=16000,
        system=SYSTEM_PROMPT, tools=TOOLS, messages=history,
    )

    if response.stop_reason == "end_turn":                      # done ✅
        answer = "".join(b.text for b in response.content if b.type == "text")
        print(f"Claude: {answer}")
        break

    if response.stop_reason == "tool_use":
        history.append({"role": "assistant", "content": response.content})  # save whole message

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":                         # run EVERY tool call
                result = check_stock(block.input["product"], block.input["size"])
                print(f"🔧 {block.name} {block.input} -> {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,                     # 🔑 match result to call
                    "content": str(result),
                })

        history.append({"role": "user", "content": tool_results})  # ALL results, ONE message
        continue

    print(f"Stopped unexpectedly: stop_reason={response.stop_reason}")  # safety exit
    break
