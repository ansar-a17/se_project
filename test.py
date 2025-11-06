import requests

url = "http://localhost:8000/image_to_text"
files = {"file": open("beagle-hound-dog.webp", "rb")}
response = requests.post(url, files=files)
print(response.json())