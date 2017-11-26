let chat_id = $('#passed-data').attr('data-room-id');
let user_id = $('#passed-data').attr('data-user-id');
let input = $('#text-input-id');
let file_field = $('#file-field-id');
let submit_button = $('#submit-button-id');
let submit_file_button = $('#submit-file-button-id');
let message_container = $('#message-container-id');

function getBase64(file) {
    return new Promise((resolve, reject) => {
        let reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function () {
            resolve(reader.result.split(',')[1]);
        };
        reader.onerror = function (error) {
            reject(error);
        };
    });
}

submit_button.click(() => {
    let text = input.val();
    let data = {
        'action': 'add_message',
        'room_id': chat_id,
        'text': text
    };
    ws.send(JSON.stringify(data));
    input.val('');
});
submit_file_button.click(() => {
    let file = file_field[0].files[0];
    getBase64(file).then((base64_data) => {
        let data = {
            'action': 'add_file',
            'room_id': chat_id,
            'file_data': {
                'content': base64_data,
                'file_name': file.name,
            }
        };
        ws.send(JSON.stringify(data));
        input.val('');
        file_field.val('');
    });

});
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

    for (let i in data.data) {
        _insert_message(data.data[i]._id,
            data.data[i].room_name,
            data.data[i].last_message.text,
            data.data[i].last_message.created,
            data.data[i].read_count,
        );
    }
};
