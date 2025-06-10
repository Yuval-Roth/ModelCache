import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:5000"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"query": "What is AI?"}))
        response = await websocket.recv()
        print("Received:", response)

asyncio.run(test_client())