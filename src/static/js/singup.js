let form = $('#sing-up-data-id');
form.submit((e) => {
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: window.location.href,
        data: form.serialize(),
    }).done(
        (data) => {
            window.location = '/'
        }
    ).fail(
        (data) => {
            console.log(data);
        }
    );
});
