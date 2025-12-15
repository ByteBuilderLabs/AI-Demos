import requests
import json

class LocalLLM:
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.api_endpoint = f"{self.host}/api/generate"
        
        try:
            # Quick health check
            requests.get(self.host)
            print(f"Connected to {self.model} at {self.host}")
        except requests.exceptions.ConnectionError:
            print(f"Error: Is Ollama running on {self.host}?")
            exit(1)
    
    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0}
        }
        
        try:
            response = requests.post(self.api_endpoint, json=payload)
            response.raise_for_status()
            
            # Extract the actual text from the JSON object
            return response.json().get("response", "")
            
        except requests.exceptions.RequestException as e:
            return f"Inference Error: {e}"
    
    def chat_stream(self, prompt: str):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True, # Enable streaming logic
            "options": {"temperature": 0.0}
        }
        
        # Use context manager for stream handling
        with requests.post(self.api_endpoint, json=payload, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    # Decode binary -> String -> JSON
                    decoded_line = json.loads(line.decode('utf-8'))
                    
                    # Yield text only if the stream isn't finished
                    if decoded_line.get("done") is False:
                        yield decoded_line.get("response", "")

if __name__ == "__main__":
    # Initialize the builder
    bot = LocalLLM(model="llama3")
    
    user_prompt = "Explain the difference between TCP and UDP protocols concisely."
    
    print(f"\nPrompt: {user_prompt}\n" + "-"*40)
    
    # Consume the generator
    for token in bot.chat_stream(user_prompt):
        # flush=True is critical for the visual effect
        print(token, end='', flush=True)
        
    print("\n" + "-"*40 + "\nGeneration Complete.")