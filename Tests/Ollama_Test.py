from ollama import Client

client = Client()

response = client.chat(
    model="gemma3:4b",
    messages=[
        {"role": "user", "content": "Summarize this text: AI is changing the world..."}
    ],
)

print(response["message"]["content"])
