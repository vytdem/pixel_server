class WebsocketHandler {
    constructor() {
        this.token = document.querySelector('meta[name="user-token"]').getAttribute('content');

        this.ws = new WebSocket('ws://127.0.0.1:8765/');
        this.ws.onopen = this.onOpen.bind(this);
        this.ws.onmessage = this.onMessage;
        this.ws.onerror = this.onError;
        this.ws.onclose = this.onClose;
    }

    sendMessage()
    {
        console.log('message sent');
        let data = {
            "content_type_id": 1,
            "channel": "events",
            "data": "test"
        };
        this.ws.send(JSON.stringify(data));
    }

    onOpen(e)
    {
        console.log("websocket connected");
        this.ws.send(this.token);
    }

    onMessage(e)
    {
        console.log("Received: ", e);
    }

    onError(e)
    {
        console.error(e);
    }

    onClose(e)
    {
        console.log("connection closed");
    }
}