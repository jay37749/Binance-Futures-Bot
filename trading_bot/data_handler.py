import websocket
import json
import logging

def on_message(ws, message):
    data = json.loads(message)
    logging.info(f"Received data: {data}")

def on_error(ws, error):
    logging.error(f"Error: {error}")

def on_close(ws):
    logging.info("WebSocket closed")

def on_open(ws):
    logging.info("WebSocket opened")
    ws.send(json.dumps({"method": "SUBSCRIBE", "params": ["btcusdt@kline_1m"], "id": 1}))

def start_websocket():
    websocket_url = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(websocket_url, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
