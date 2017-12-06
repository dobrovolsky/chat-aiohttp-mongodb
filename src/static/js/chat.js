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
        console.log(data);
        ws.send(JSON.stringify(data));
        input.val('');
        file_field.val('');
    });

});
ws.onopen = () => {
    ws.send(JSON.stringify({
        'action': 'get_messages',
        'limit': 100,
        'offset': 0,
        'room_id': chat_id
    }))
};
let _insert_message = (message_user_id, user_name, text, time, file) => {
    let file_url_string = '';
    let darker = "";
    let image_class = "left";
    let time_class = "right";
    if (message_user_id == user_id) {
        darker = "darker";
        image_class = "right";
        time_class = "left";
    }
    if (file){
       file_url_string = `<a href="${file}" target="_blank">file</a>`
    }
    let date = new Date(time * 1000);
    let hours = date.getHours();
    let minutes = "0" + date.getMinutes();
    let seconds = "0" + date.getSeconds();
    let formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);


    let insert_string = `<div class="message-container ${darker}">
                            <img src="https://tracker.moodle.org/secure/thumbnail/30912/_thumb_30912.png" alt="${user_name}" class="${image_class}">
                            <p>${user_name}: </p>
                            <p>${text}</p>
                            ${file_url_string}
                            <span class="time-${time_class}">${formattedTime}</span>
                         </div>`;
    message_container.append(insert_string);
};
let insert_messages = (data) => {
    data.data.sort((first, second) => {
        return first > second;
    });
    for (let i in data.data) {
        _insert_message(data.data[i].from_user_id,
            data.data[i].from_user_first_name,
            data.data[i].text,
            data.data[i].created,
            data.data[i].file
        );
    }
};
