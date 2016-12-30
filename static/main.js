$(document).ready(function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    window.socket = socket;
    var numbers_received = [];
    $("#backbutton").on('click', function () { socket.emit('go_back') });
    socket.on('check_vive_connected', function () {
        socket.emit('heartbeat');
    })
    socket.on('receive_views', function (msg) {
        try { $("#currentview").remove(); } catch (err) { }
        try {
            var animation = document.createElement("a-animation");
            animation.setAttribute("attribute", "position");
            animation.setAttribute("to", "0 -1 0");
            animation.setAttribute("dur", "2000");
            animation.setAttribute("repeat", "0");
            animation.setAttribute("animationend", $("#view_box").remove());
            $("#view_box").append(animation);
        } catch (err) { }
        total_html = ""
        for (var i = 0; i < msg.length; i++) {
            var view = msg[i]
            var button_asset_id = view.id + 'img_asset'
            $("#aframe-assets").append("<img id='" + button_asset_id + "' src='" + view.image + "' crossorigin='anonymous'>")
            var curved_image_html = "<a-curvedimage id='" + view.id + "img' src='#" + button_asset_id + "' position='" + view.image_pos + "' height='6' radius='10' theta-length='50' rotation='" + view.theta + "' crossorigin=anonymous>"
            var button_html = "<a-entity id='" + view.id + "button' geometry='primitive:box' position='4.1 -4.2 9' rotation='0 295 0' material='color:white' scale='1 2 7' move='target:#user;position:0 " + view.button_height + " 0;level:" + view.level + ";'>"
            var text_html = "<a-entity bmfont-text='text: " + view.name + "; fnt:/futura.fnt; fntImage:/futura.png; width:800; lineHeight:60; align:center; color:black;' scale='0.21 0.72 1.00' position='-0.51 " + view.text_pos_height + " -0.42' rotation='0 270 0'> </a-entity>"
            var closing_button_html = "</a-entity></a-curvedimage>"
            var on_click_js = "\<script id='" + view.id + "script'\>" +
                "document.querySelector('" + view.hash_id + "button').addEventListener('click', function(){" +
                "if (" + view.is_stack + ") {console.log('yep');" +
                "var user_animation = document.createElement('a-animation');" +
                "user_animation.setAttribute('attribute','position');" +
                "user_animation.setAttribute('to','0 0 0');" +
                "user_animation.setAttribute('repeat','0');" +
                "user_animation.setAttribute('dur','2000');" +
                "$('#user').append(user_animation);" +
                "console.log('i have been clicked!');" +
                "window.socket.emit\('send_view', \{data\: '" + view.id + "'\}\);" +
                "return;\}\}\);" +
                "\<\/script\>"
            var complete_html = curved_image_html + button_html + text_html + closing_button_html + on_click_js
            total_html = total_html + complete_html
        }
        $("#scene").append("<a-entity id='view_box' visible='true'><a-animation attribute='position' from='0 20 0' to='0 -0.4 0' dur='3000'></a-animation>" + total_html + "</a-entity>");
    });
});