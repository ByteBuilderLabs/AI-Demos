import base64
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def encode_image(image_path):
    """Convert a local image to a base64 string for API transmission."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class VisionAgent:
    def __init__(self, model="gpt-4o"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def analyze_ui(self, image_path, task):
        base64_image = encode_image(image_path)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Task: {task}. Return a JSON object with 'element', 'x_percent', and 'y_percent'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

if __name__ == "__main__":
    agent = VisionAgent()

    # Ensure you have a 'screenshot.png' in your directory
    print("--- Analyzing UI ---")
    result = agent.analyze_ui("screenshot.png", "Find the 'Export to CSV' button.")
    print(result)