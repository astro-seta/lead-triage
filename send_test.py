import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
URL = "http://127.0.0.1:5000/webhook/lead"
SECRET = os.getenv("WEBHOOK_SECRET")

samples = [
    {"name": "Ana Torres", "email": "ana@example.com",
     "message": "I was served court papers yesterday and must respond by Friday. Please call me today."},
    {"name": "Mark Lee", "email": "mark@seo-deals.example",
     "message": "We can get your firm to #1 on Google for only $99. Reply for details!"},
    {"name": "Priya Shah", "email": "priya@example.com",
     "message": "Hi, I'm already a client. Could you send me a copy of my signed agreement?"},
    {"name": "John Smith", "email": "john@example.com",
     "message": "I'm thinking about writing a will sometime next year. What are your rates?"},
]

print("--- Sending 4 test messages ---")
for s in samples:
    r = requests.post(URL, json=s, headers={"X-Webhook-Secret": SECRET})
    print(s["name"], r.status_code, r.json())
    time.sleep(2)

print("--- Failure test 1: wrong password (expect 401) ---")
r = requests.post(URL, json=samples[0], headers={"X-Webhook-Secret": "wrong"})
print(r.status_code, r.json())

print("--- Failure test 2: no message (expect 400) ---")
r = requests.post(URL, json={"name": "Bob"}, headers={"X-Webhook-Secret": SECRET})
print(r.status_code, r.json())
