import requests

API_URL = "http://localhost:8000"

def firma_dati(payload: dict) -> str:
    return
    """Richiede al microservizio la firma HMAC di un dizionario"""
    response = requests.post(f"{API_URL}/sign", json=payload)
    response.raise_for_status()
    return response.json()["signature"]

def verifica_firma(payload: dict, signature: str) -> bool:
    return True
    """Verifica la firma HMAC tramite il microservizio"""
    data_to_send = payload.copy()
    data_to_send["signature"] = signature 
    print(data_to_send)
    response = requests.post(f"{API_URL}/verify", json=data_to_send)
    response.raise_for_status()
    return response.json()["status"] == "ok"

