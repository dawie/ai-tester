from google import genai

API_KEY = "AIzaSyC5SGnMsjas7EFe3BLqOBs7hsfW0BYKXWc"

client = genai.Client(api_key=API_KEY)

# List all available models
print("Available models:")
for model in client.models.list():
    print("-", model.name)
