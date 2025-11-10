import requests

url = "http://localhost:8000/image_to_text"
files = {"file": open("cat.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())