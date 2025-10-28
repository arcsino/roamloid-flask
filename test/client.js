document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const log = document.getElementById('log');
    const userIdInput = document.getElementById('user_id');
    const deviceNameInput = document.getElementById('device_name');
    const joinBtn = document.getElementById('joinBtn');
    const msgInput = document.getElementById('msg');
    const moveDeviceInput = document.getElementById('move_device');
    const sendBtn = document.getElementById('sendBtn');

    function appendLog(message) {
        const div = document.createElement('div');
        div.textContent = message;
        log.appendChild(div);
        log.scrollTop = log.scrollHeight;
    }

    joinBtn.onclick = () => {
        const device_name = deviceNameInput.value.trim();
        if (!device_name) {
            appendLog('デバイス名を入力してください');
            return;
        }
        socket.emit('join_room', { device_name });
        appendLog(`join_room送信: device_name=${device_name}`);
    };

    sendBtn.onclick = () => {
        const device_name = deviceNameInput.value.trim();
        const msg = msgInput.value.trim();
        const move_device = moveDeviceInput.value.trim();
        if (!device_name) {
            appendLog('デバイス名を入力してください');
            return;
        }
        if (!msg && !move_device) {
            appendLog('メッセージまたは3D移動先デバイス名を入力してください');
            return;
        }
        const data = { device_name };
        if (msg) data.msg = msg;
        if (move_device) data.move = { to_device_name: move_device };
        socket.emit('send_data', data);
        appendLog(`send_data送信: ${JSON.stringify(data)}`);
    };

    socket.on('joined', data => {
        appendLog(`joined: ${JSON.stringify(data)}`);
    });
    socket.on('receive_data', data => {
        appendLog(`receive_data: ${JSON.stringify(data)}`);
    });
    socket.on('moved_3d', data => {
        appendLog(`moved_3d: ${JSON.stringify(data)}`);
    });
    socket.on('error', data => {
        appendLog(`error: ${JSON.stringify(data)}`);
    });
});
