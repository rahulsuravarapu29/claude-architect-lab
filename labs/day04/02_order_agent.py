import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your environment

# The shop's shelf: (product, size) -> pairs in stock
INVENTORY = {("nike pegasus", 10): 3, ("nike pegasus", 11): 0, ("adidas ultraboost", 10): 5}


# ---------- Tool 1: look at the shelf ----------
def check_stock(product, size):
    return INVENTORY.get((product.lower(), size), 0)


# ---------- Tool 2: actually sell shoes (SAFE version) ----------
def place_order(product, size, quantity):
    key = (product.lower(), size)
    in_stock = INVENTORY.get(key, 0)

    # Guard 0: silly numbers
    if quantity <= 0:
        return "Error: quantity must be at least 1"

    # Guard 1: the CODE checks stock (we never trust Claude to do it)
    if quantity > in_stock:
        return f"Error: only {in_stock} pairs in stock"

    # Guard 2: a human must say yes
    approval = input(f"Approve order: {quantity} x {product} size {size}? (y/n) ")
    if approval.strip().lower() != "y":
        return "Order cancelled by staff"

    # Approved: take the shoes off the shelf
    INVENTORY[key] = in_stock - quantity
    return "Order placed!"


# Name -> function, so the loop can call the right one
TOOL_FUNCTIONS = {
    "check_stock": check_stock,
    "place_order": place_order,
}

TOOLS = [
    {
        "name": "check_stock",
        "description": "Check how many pairs of ONE product in ONE size are in stock. "
        "Returns a number (0 = out of stock).",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "Brand and model, e.g. 'Nike Pegasus'"},
                "size": {"type": "number", "description": "US shoe size, e.g. 10"},
            },
            "required": ["product", "size"],
        },
    },
    {
        "name": "place_order",
        "description": "Place an order for a customer. A staff member must approve it. "
        "Returns 'Order placed!', 'Order cancelled by staff', or an error message.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "Brand and model, e.g. 'Nike Pegasus'"},
                "size": {"type": "number", "description": "US shoe size, e.g. 10"},
                "quantity": {"type": "integer", "description": "Number of pairs, at least 1"},
            },
            "required": ["product", "size", "quantity"],
        },
    },
]

SYSTEM_PROMPT = """You are a shoe shop assistant. Use the tools to check stock and place orders.
Never guess stock. If an order fails, tell the customer exactly why and offer what IS possible."""

history = [{"role": "user", "content": "I want 5 pairs of Nike Pegasus size 10."}]

for step in range(10):  # safety cap: never loop more than 10 times
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=history,
    )

    if response.stop_reason == "end_turn":
        answer = "".join(b.text for b in response.content if b.type == "text")
        print(f"Claude: {answer}")
        break

    if response.stop_reason == "tool_use":
        history.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                func = TOOL_FUNCTIONS[block.name]   # pick the right function by name
                result = func(**block.input)        # run it with Claude's inputs
                print(f"🔧 {block.name} {block.input} -> {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                        "is_error": str(result).startswith("Error"),  # tell Claude it failed
                    }
                )

        history.append({"role": "user", "content": tool_results})
        continue

    print(f"Stopped unexpectedly: stop_reason={response.stop_reason}")
    break
