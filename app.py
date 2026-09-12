from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    HTTPException
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import measurements, test_connection
from datetime import datetime, timezone
import time


app = FastAPI(
    title="MHUTEMP Stack 02",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mhutemp-s02-nextjs.netlify.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CLIENTES WEBSOCKET CONECTADOS
# =========================================================

connected_clients = {}


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def startup_event():
    test_connection()


# =========================================================
# MODELO LOGIN
# =========================================================

class LoginRequest(BaseModel):
    username: str
    password: str


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "system": "MHUTEMP",
        "stack": "02",
        "backend": "Python / FastAPI",
        "database": "MongoDB",
        "status": "running"
    }


# =========================================================
# LOGIN DEMO
# =========================================================

@app.post("/api/auth/login")
def login(data: LoginRequest):

    if (
        data.username == "doctor03"
        and data.password == "123456"
    ):
        return {
            "user": {
                "username": "doctor03"
            },
            "token": "stack02-demo-token"
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
    )


# =========================================================
# REST - MEDICIONES
# =========================================================

@app.get("/api/measurements")
def get_measurements(limit: int = 20):

    limit = min(max(limit, 1), 100)

    docs = list(
        measurements
        .find({}, {"_id": 0})
        .sort("receivedAt", -1)
        .limit(limit)
    )

    return docs


# =========================================================
# WEBSOCKET
# =========================================================

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    username = None

    print("WebSocket conectado")

    try:

        while True:

            data = await websocket.receive_json()

            # =================================================
            # PING / PONG
            # =================================================

            if data.get("type") == "ping":

                await websocket.send_json({
                    "type": "pong",
                    "timestamp": int(time.time() * 1000)
                })

                print("PING recibido → PONG enviado")

                continue


            # =================================================
            # IDENTIFICACIÓN INICIAL DEL NODO
            # =================================================

            if (
                "username" in data
                and len(data) == 1
            ):

                username = data["username"]

                connected_clients[username] = websocket

                print(
                    f"Nodo identificado: {username}"
                )

                continue


            # =================================================
            # RECEPCIÓN DE MEDICIÓN
            # =================================================

            if "username" in data:

                username = data["username"]

                document = {
                    "username": data.get("username"),
                    "dsTemperature": data.get("dsTemperature"),
                    "temperature": data.get("temperature"),
                    "humidity": data.get("humidity"),
                    "datetime": data.get("datetime"),
                    "doorStatus": data.get("doorStatus"),
                    "receivedAt": datetime.now(timezone.utc)
                }

                measurements.insert_one(document)

                print(
                    f"Medición guardada | "
                    f"{username} | "
                    f"DS: {data.get('dsTemperature')} | "
                    f"T: {data.get('temperature')} | "
                    f"H: {data.get('humidity')} | "
                    f"Door: {data.get('doorStatus')}"
                )


                # =============================================
                # DATOS PARA BROADCAST
                # =============================================

                broadcast_data = {
                    "username": document["username"],
                    "dsTemperature": document["dsTemperature"],
                    "temperature": document["temperature"],
                    "humidity": document["humidity"],
                    "datetime": document["datetime"],
                    "doorStatus": document["doorStatus"]
                }


                # =============================================
                # BROADCAST
                # =============================================

                disconnected = []

                for client_name, client_ws in connected_clients.items():

                    try:

                        await client_ws.send_json(
                            broadcast_data
                        )

                    except Exception:

                        disconnected.append(
                            client_name
                        )


                for client_name in disconnected:

                    connected_clients.pop(
                        client_name,
                        None
                    )


    except WebSocketDisconnect:

        print(
            f"WebSocket desconectado: {username}"
        )


    except Exception as e:

        print(
            f"Error WebSocket: {e}"
        )


    finally:

        if username:

            connected_clients.pop(
                username,
                None
            )