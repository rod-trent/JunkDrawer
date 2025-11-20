# Save as agents/weather_reporter.py
def run(client):
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {"role": "system", "content": "You are a helpful agent that reports the weather in a fun way."},
            {"role": "user", "content": "What's the weather like in Paris right now? Be creative!"}
        ],
        temperature=0.9
    )
    print("🌤️ Weather Report:", response.choices[0].message.content)
    return response.choices[0].message.content