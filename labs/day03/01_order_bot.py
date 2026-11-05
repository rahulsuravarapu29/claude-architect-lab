from typing import Optional
import anthropic
from pydantic import BaseModel, Field

client = anthropic.Anthropic()

# 1. Pydantic class: any field can be missing (required fields force Claude to guess)
class ShoeOrder(BaseModel):
    product: Optional[str] = Field(default=None, description="Brand and model, e.g. 'Nike Pegasus', or null if not said")
    size: Optional[float] = Field(default=None, description="US shoe size, e.g. 10.0, or null if not said")
    color: Optional[str] = Field(default=None, description="Color, or null if the customer has not said")
    quantity: Optional[int] = Field(default=None, description="Number of pairs, or null if the customer has not said")

SYSTEM_PROMPT = """Extract a shoe order from everything the customer has said.
Only use information the customer actually stated. If any field
was not stated, return null for it. Never guess."""

customer_texts = []                                   # 2

while True:                                           # 3
    customer_texts.append(input("You: "))

    response = client.messages.parse(                 # 4
        model="claude-opus-5-5",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "\n".join(customer_texts)}],
        output_format=ShoeOrder,
    )
    order = response.parsed_output

    missing = False                                   # 5
    if order.product is None:
        print("Bot: Which shoe would you like?")
        missing = True
    if order.size is None:
        print("Bot: What size do you wear?")
        missing = True
    if order.color is None:
        print("Bot: Which color would you like?")
        missing = True
    if order.quantity is None:
        print("Bot: How many pairs would you like?")
        missing = True

    if not missing:                                   # 6
        print(f"Bot: Order confirmed! {order.quantity} x {order.product}, size {order.size}, {order.color}")
        break
