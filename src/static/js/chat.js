let ws = new WebSocket('ws://0.0.0.0:8888/ws/chat');
ws.onmessage = (data) => {console.log(data)};