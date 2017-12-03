let ws = null;
let connect = () => {
  ws = new WebSocket(`ws://${window.location.hostname}:${window.location.port}/ws/chat`);

  ws.onmessage = (data) => {
        data = JSON.parse(data.data);
        handle_message(data);
  };

  ws.onclose = () => {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    setTimeout(() => {
      connect();
    }, 1000);
  };

  ws.onerror = () => {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
  };
};

connect();

let counter = $('#message-counter-id');

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
