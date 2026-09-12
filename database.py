import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI no está definido en .env")

client = MongoClient(MONGODB_URI)

db = client["mhutemp_stack02"]
measurements = db["measurements"]


def test_connection():
    client.admin.command("ping")
    print("✓ MongoDB conectado correctamente")