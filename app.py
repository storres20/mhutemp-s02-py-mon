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


# =========================================================
# APP
# =========================================================

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
# LOGIN MODEL
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

                "username": "doctor03",

                "hospital": {
                    "_id": "stack02-hospital",
                    "name": "MHUTEMP Stack 02 Test Site"
                },

                "area": {
                    "_id": "stack02-area",
                    "name": "Experimental Monitoring Area"
                }

            },

            "token": "stack02-demo-token"

        }


    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
    )


# =========================================================
# DEVICE - BLD-prueba
# =========================================================

@app.get("/api/devices/by-sensor/{username}")
def get_device_by_sensor(username: str):

    if username == "BLD-prueba":

        return {

            "_id": "stack02-device-001",

            "name": "MHUTEMP Test Node",

            "brand": "MHUTEMP",

            "model": "Stack 02 Experimental Node",

            "serie": "BLD-prueba",

            "assigned_sensor_username": "BLD-prueba",

            "hospital": {
                "_id": "stack02-hospital",
                "name": "MHUTEMP Stack 02 Test Site"
            },

            "area": {
                "_id": "stack02-area",
                "name": "Experimental Monitoring Area"
            }

        }


    raise HTTPException(
        status_code=404,
        detail="Device not found"
    )


# =========================================================
# REST - MEDICIONES
# =========================================================

@app.get("/api/measurements")
def get_measurements(limit: int = 20):

    limit = min(
        max(limit, 1),
        100
    )

    docs = list(

        measurements
        .find(
            {},
            {
                "_id": 0
            }
        )
        .sort(
            "receivedAt",
            -1
        )
        .limit(limit)

    )

    return docs


# =========================================================
# REST - MEDICIONES POR NODO
# =========================================================

@app.get("/api/measurements/{username}")
def get_measurements_by_username(
    username: str,
    limit: int = 20
):

    limit = min(
        max(limit, 1),
        100
    )

    docs = list(

        measurements
        .find(
            {
                "username": username
            },
            {
                "_id": 0
            }
        )
        .sort(
            "receivedAt",
            -1
        )
        .limit(limit)

    )

    return docs


# =========================================================
# WEBSOCKET
# =========================================================

@app.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    username = None

    print(
        "WebSocket conectado"
    )


    try:

        while True:

            data = await websocket.receive_json()


            # =================================================
            # PING / PONG
            # =================================================

            if data.get("type") == "ping":

                await websocket.send_json({

                    "type": "pong",

                    "timestamp": int(
                        time.time() * 1000
                    )

                })

                print(
                    "PING recibido → PONG enviado"
                )

                continue


            # =================================================
            # IDENTIFICACIÓN INICIAL DEL NODO
            # =================================================

            if (
                "username" in data
                and len(data) == 1
            ):

                username = data["username"]

                connected_clients[
                    username
                ] = websocket

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

                    "username":
                        data.get("username"),

                    "dsTemperature":
                        data.get("dsTemperature"),

                    "temperature":
                        data.get("temperature"),

                    "humidity":
                        data.get("humidity"),

                    "datetime":
                        data.get("datetime"),

                    "doorStatus":
                        data.get("doorStatus"),

                    "receivedAt":
                        datetime.now(
                            timezone.utc
                        )

                }


                # =============================================
                # GUARDAR EN MONGODB
                # =============================================

                measurements.insert_one(
                    document
                )


                print(

                    f"Medición guardada | "

                    f"{username} | "

                    f"DS: "
                    f"{data.get('dsTemperature')} | "

                    f"T: "
                    f"{data.get('temperature')} | "

                    f"H: "
                    f"{data.get('humidity')} | "

                    f"Door: "
                    f"{data.get('doorStatus')}"

                )


                # =============================================
                # DATOS PARA BROADCAST
                # =============================================

                broadcast_data = {

                    "username":
                        document["username"],

                    "dsTemperature":
                        document["dsTemperature"],

                    "temperature":
                        document["temperature"],

                    "humidity":
                        document["humidity"],

                    "datetime":
                        document["datetime"],

                    "doorStatus":
                        document["doorStatus"]

                }


                # =============================================
                # BROADCAST
                # =============================================

                disconnected = []


                for (
                    client_name,
                    client_ws
                ) in connected_clients.items():

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


    # =========================================================
    # DESCONEXIÓN NORMAL
    # =========================================================

    except WebSocketDisconnect:

        print(
            f"WebSocket desconectado: "
            f"{username}"
        )


    # =========================================================
    # OTROS ERRORES
    # =========================================================

    except Exception as e:

        print(
            f"Error WebSocket: {e}"
        )


    # =========================================================
    # LIMPIEZA
    # =========================================================

    finally:

        if username:

            connected_clients.pop(
                username,
                None
            )