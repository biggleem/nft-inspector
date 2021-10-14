import requests

r = requests.get("https://api.opensea.io/api/v1/assets")

print(r.json())
