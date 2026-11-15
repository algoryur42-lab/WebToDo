import re
import requests

BASE = "http://127.0.0.1:5000"
s = requests.Session()  

r = s.get(BASE + "/")
token = re.search(r'name="csrf_token" value="([^"]*)"', r.text).group(1)

r = s.post(BASE + "/add", data={"csrf_token": token, "title": "тест"})
print("С токеном:", r.status_code)

r = s.post(BASE + "/add", data={"title": "hack"})
print("Без токена:", r.status_code)

r = s.post(BASE + "/add", data={"csrf_token": "подделка", "title": "hack"})
print("С поддельным токеном:", r.status_code)