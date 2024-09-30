import requests

url = "https://api.jdoodle.com/v1/execute"
data = {
    "script": "print(input())",
    "language": "python3",
    "versionIndex": "3",
    "input": "Hello, World!"
}

response = requests.post(url, json=data)
print(response.json())
