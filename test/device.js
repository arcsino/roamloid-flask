let socket = null;
let currentDevice = null;
let userId = null;

function showMessage(msg, isError = false) {
  const m = document.getElementById("device-message");
  m.textContent = msg;
  m.className = "message" + (isError ? " error" : "");
}

async function fetchUserId() {
  const res = await fetch(
    "https://roamloid-flask.onrender.com/api/auth/detail",
    {
      credentials: "include",
    }
  );
  if (!res.ok) throw new Error("ユーザー情報取得失敗");
  const data = await res.json();
  return data.id;
}

async function fetchDevices() {
  const res = await fetch(
    "https://roamloid-flask.onrender.com/api/room/devices",
    {
      credentials: "include",
    }
  );
  if (!res.ok) throw new Error("デバイス一覧取得失敗");
  const data = await res.json();
  return data.devices || [];
}

async function createDevice(name) {
  const res = await fetch(
    "https://roamloid-flask.onrender.com/api/room/devices",
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    }
  );
  return await res.json();
}

document.addEventListener("DOMContentLoaded", async () => {
  const deviceSelect = document.getElementById("device_select");
  const refreshBtn = document.getElementById("refreshBtn");
  const selectBtn = document.getElementById("selectBtn");
  const createDeviceBtn = document.getElementById("createDeviceBtn");
  const newDeviceNameInput = document.getElementById("new_device_name");
  const deviceMessage = document.getElementById("device-message");
  const deviceSelectSection = document.getElementById("device-select-section");
  const chatSection = document.getElementById("chat-section");
  const msgInput = document.getElementById("msg");
  const sendBtn = document.getElementById("sendBtn");
  const backBtn = document.getElementById("backBtn");
  const log = document.getElementById("log");

  async function updateDeviceList() {
    deviceSelect.innerHTML = "";
    try {
      const devices = await fetchDevices();
      devices.forEach((d) => {
        const opt = document.createElement("option");
        opt.value = d.name;
        opt.textContent = d.name + (d.in_3d ? "（3D）" : "");
        deviceSelect.appendChild(opt);
      });
      showMessage("デバイス一覧を更新しました");
    } catch (e) {
      showMessage(e.message, true);
    }
  }

  refreshBtn.onclick = updateDeviceList;

  createDeviceBtn.onclick = async () => {
    const name = newDeviceNameInput.value.trim();
    if (!name) {
      showMessage("新規デバイス名を入力してください", true);
      return;
    }
    const res = await createDevice(name);
    if (res.error_message) {
      showMessage(res.error_message, true);
    } else {
      showMessage("デバイス作成成功: " + res.name);
      newDeviceNameInput.value = "";
      await updateDeviceList();
    }
  };

  selectBtn.onclick = async () => {
    const deviceName = deviceSelect.value;
    if (!deviceName) {
      showMessage("デバイスを選択してください", true);
      return;
    }
    try {
      if (!userId) {
        userId = await fetchUserId();
      }
      currentDevice = deviceName;
      deviceSelectSection.style.display = "none";
      chatSection.style.display = "";
      startSocket();
    } catch (e) {
      showMessage("ユーザー情報取得失敗: " + e.message, true);
    }
  };

  backBtn.onclick = () => {
    chatSection.style.display = "none";
    deviceSelectSection.style.display = "";
    if (socket) {
      socket.disconnect();
      socket = null;
    }
    log.innerHTML = "";
  };

  function appendLog(message) {
    const div = document.createElement("div");
    div.textContent = message;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  function startSocket() {
    socket = io();
    socket.on("connect", () => {
      socket.emit("join_room", { device_name: currentDevice });
      appendLog("接続しました。デバイス: " + currentDevice);
    });
    socket.on("joined", (data) => {
      appendLog(`joined: ${JSON.stringify(data)}`);
    });
    socket.on("receive_data", (data) => {
      appendLog(`受信: ${data.text}`);
    });
    socket.on("moved_3d", (data) => {
      appendLog(`3D移動: ${JSON.stringify(data)}`);
    });
    socket.on("error", (data) => {
      appendLog(`error: ${JSON.stringify(data)}`);
    });
  }

  sendBtn.onclick = () => {
    if (!socket || !currentDevice) return;
    const msg = msgInput.value.trim();
    if (!msg) {
      appendLog("メッセージを入力してください");
      return;
    }
    const data = { device_name: currentDevice, msg };
    socket.emit("send_data", data);
    appendLog(`送信: ${msg}`);
    msgInput.value = "";
  };

  // 初期化
  await updateDeviceList();
});
