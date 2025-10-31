document.addEventListener("DOMContentLoaded", () => {
  // const socket = io(); これだと、ログイン時にサーバーからもらったセッションクッキーをWebSocketの接続時に送ってくれない(らしい)

  const socket = io("http://localhost:5000", {
    // ローカルサーバーに接続（開発環境）
    // const socket = io('https://roamloid-flask.onrender.com', { //本番環境
    withCredentials: true, // これでCookieを送受信
  });

  const log = document.getElementById("log");
  const deviceNameInput = document.getElementById("device_name");
  const joinBtn = document.getElementById("joinBtn");
  const msgInput = document.getElementById("msg");
  const moveDeviceInput = document.getElementById("move_device");
  const sendBtn = document.getElementById("sendBtn");
  const deviceList = document.getElementById("device_list");
  const refreshDevicesBtn = document.getElementById("refreshDevices");
  const createDeviceBtn = document.getElementById("createDeviceBtn");
  const newDeviceNameInput = document.getElementById("new_device_name");
  const renameDeviceBtn = document.getElementById("renameDeviceBtn");
  const deleteDeviceBtn = document.getElementById("deleteDeviceBtn");

  function appendLog(message) {
    const div = document.createElement("div");
    div.textContent = message;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  joinBtn.onclick = () => {
    const device_name = deviceNameInput.value.trim();
    if (!device_name) {
      appendLog("デバイス名を入力してください");
      return;
    }
    socket.emit("join_room", { device_name });
    appendLog(`join_room送信: device_name=${device_name}`);
  };

  sendBtn.onclick = () => {
    const device_name = deviceNameInput.value.trim();
    const msg = msgInput.value.trim();
    const move_device = moveDeviceInput.value.trim();
    if (!device_name) {
      appendLog("デバイス名を入力してください");
      return;
    }
    if (!msg && !move_device) {
      appendLog("メッセージまたは3D移動先デバイス名を入力してください");
      return;
    }
    const data = { device_name };
    if (msg) data.msg = msg;
    if (move_device) data.move = { to_device_name: move_device };
    socket.emit("send_data", data);
    appendLog(`send_data送信: ${JSON.stringify(data)}`);
  };

  // デバイス一覧取得
  async function fetchDevices() {
    try {
      const res = await fetch("http://localhost:5000/api/room/devices", {
        method: "GET",
        headers: { Origin: "http://localhost:5173" },
        credentials: "include",
      });
      const data = await res.json();
      deviceList.innerHTML = "";
      if (data.devices && Array.isArray(data.devices)) {
        data.devices.forEach((dev) => {
          const opt = document.createElement("option");
          opt.value = dev.id;
          opt.textContent = dev.name;
          deviceList.appendChild(opt);
        });
        // 先頭を選択
        if (data.devices.length > 0) {
          deviceList.value = data.devices[0].id;
          deviceNameInput.value = data.devices[0].name;
        } else {
          deviceNameInput.value = "";
        }
      } else {
        appendLog("デバイス一覧取得失敗: 不正なレスポンス");
      }
    } catch (e) {
      appendLog("デバイス一覧取得失敗", e);
    }
  }

  // デバイス選択時
  deviceList.addEventListener("change", () => {
    const selected = deviceList.options[deviceList.selectedIndex];
    deviceNameInput.value = selected.textContent;
  });

  // デバイス再読込
  refreshDevicesBtn.onclick = fetchDevices;

  // デバイス新規作成
  createDeviceBtn.onclick = async () => {
    const name = newDeviceNameInput.value.trim();
    if (!name) {
      appendLog("新規デバイス名を入力してください");
      return;
    }
    try {
      const res = await fetch("http://localhost:5000/api/room/devices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Origin: "http://localhost:5173",
        },
        credentials: "include",
        body: JSON.stringify({ name }),
      });
      if (res.ok) {
        appendLog("デバイス作成成功");
        newDeviceNameInput.value = "";
        fetchDevices();
      } else {
        appendLog("デバイス作成失敗");
      }
    } catch {
      appendLog("通信エラー(作成)");
    }
  };

  // デバイス名変更
  renameDeviceBtn.onclick = async () => {
    const id = deviceList.value;
    const name = deviceNameInput.value.trim();
    if (!id || !name) {
      appendLog("変更対象デバイスと新しい名前を選択/入力してください");
      return;
    }
    try {
      const res = await fetch(`http://localhost:5000/api/room/devices/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Origin: "http://localhost:5173",
        },
        credentials: "include",
        body: JSON.stringify({ name }),
      });
      if (res.ok) {
        appendLog("デバイス名変更成功");
        fetchDevices();
      } else {
        appendLog("デバイス名変更失敗");
      }
    } catch {
      appendLog("通信エラー(名前変更)");
    }
  };

  // デバイス削除
  deleteDeviceBtn.onclick = async () => {
    const id = deviceList.value;
    if (!id) {
      appendLog("削除対象デバイスを選択してください");
      return;
    }
    if (!confirm("本当に削除しますか？")) return;
    try {
      const res = await fetch(`http://localhost:5000/api/room/devices/${id}`, {
        method: "DELETE",
        headers: { Origin: "http://localhost:5173" },
        credentials: "include",
      });
      if (res.ok) {
        appendLog("デバイス削除成功");
        fetchDevices();
      } else {
        appendLog("デバイス削除失敗");
      }
    } catch {
      appendLog("通信エラー(削除)");
    }
  };

  socket.on("joined", (data) => {
    appendLog(`joined: ${JSON.stringify(data)}`);
  });
  socket.on("receive_data", (data) => {
    appendLog(`receive_data: ${JSON.stringify(data)}`);
  });
  socket.on("error", (data) => {
    appendLog(`error: ${JSON.stringify(data)}`);
  });

  // 初回デバイス一覧取得
  fetchDevices();
});
