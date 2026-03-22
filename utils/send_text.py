import requests
import json
import re
from dotenv import load_dotenv
import os
def query_text(script: str) -> list[str]:
    load_dotenv()
    print("Sending script to AI...")
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Give the parts that could be cut off this video so that it can be used as a clip and be published. Give the entertaining parts that users would like to watch. Give it in a format like this 5:30-6:00 only give the output and nothing else, here's the script: {script}"
                    }
                ],
                "reasoning": {"enabled": False}
            }),
            timeout=60  # <-- prevent hanging forever
        )
    except requests.Timeout:
        print("AI request timed out.")
        return []
    except requests.RequestException as e:
        print(f"AI request failed: {e}")
        return []

    print(f"AI response status: {response.status_code}")
    data = response.json()
    print(f"Raw AI response: {data}")  # temporary debug line

    try:
        content = data['choices'][0]['message']['content']
        print(f"AI content: {content}")
        timestamps = re.findall(r'\d+:\d{2}-\d+:\d{2}', content)
        print(f"Parsed timestamps: {timestamps}")
        return timestamps
    except Exception as e:
        print(f"Failed to parse AI response: {e}")
        return []