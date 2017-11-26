let ws = new WebSocket('ws://0.0.0.0:8888/ws/chat');
let counter = $('#message-counter-id');
ws.onmessage = (data) => {
    data = JSON.parse(data.data);
    handle_message(data);
};
ws.onclose = (data) => {
    console.log(data)
};
let handle_message = (data) => {
    if (data.event == 'get_messages') {
        insert_messages(data);
    }
    if (data.event == 'new_message') {
        console.log(data);
        _insert_message(data.data.from_user_id, data.data.from_user_first_name, data.data.text, data.data.created, data.data.file);
    }
    if (data.event == 'get_rooms'){
        console.log(data);
        insert_messages(data);
    }
};
