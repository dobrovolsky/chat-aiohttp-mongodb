let input = $('#text-input-id');

ws.onopen = () => {
    ws.send(JSON.stringify({
        'action': 'get_rooms',
        'limit': 100,
        'offset': 0,
    }))
};

let _insert_message = (room_id, room_name, text, time, read_count) => {
    let message_container = $('#message-container-id');
    let date = new Date(time * 1000);
    let hours = date.getHours();
    let minutes = "0" + date.getMinutes();
    let seconds = "0" + date.getSeconds();
    let formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
    let insert_string = `<li class="list-group-item">
                            <a href="/chat/${room_id}">${ room_name }: TEXT: ${text}</a>
                            <span>${read_count}</span>
                            <span>${formattedTime}</span>
                         </li>`;
    message_container.append(insert_string);
};
let insert_messages = (data) => {
    data.data.sort((first, second) => {
        return first.created > second.created;
    });

    if (!data.data.length){
        let message_container = $('#message-container-id');
        let insert_string = `<li class="list-group-item">
                                <p>There is no chats yet</p>
                             </li>`;
        message_container.append(insert_string);
    }
    for (let i in data.data) {
        _insert_message(data.data[i]._id,
            data.data[i].room_name,
            data.data[i].last_message.text,
            data.data[i].last_message.created,
            data.data[i].read_count,
        );
    }
};
