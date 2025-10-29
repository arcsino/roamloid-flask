let socket = null;
let currentDevice = null;
let currentUserId = null;

function showMessage(msg, isError = false) {
  const m = document.getElementById("device-message");
  m.textContent = msg;
  m.className = "message" + (isError ? " error" : "");
}

const API_BASE = "https://roamloid-flask.onrender.com";

async function fetchUserId() {
  try {
    const res = await fetch(`${API_BASE}/api/auth/detail`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error("ユーザー情報取得失敗");
    const data = await res.json();
    return data.id;
  } catch {
    return null;
  }
}

async function fetchDevices(userId) {
  try {
    const res = await fetch(`${API_BASE}/api/room/devices`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error("デバイス一覧取得失敗");
    return await res.json();
  } catch {
    return [];
  }
}

async function createDevice(userId, name) {
  const res = await fetch(`${API_BASE}/api/room/devices`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
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
  const moveDeviceInput = document.getElementById("move_device");
  const sendBtn = document.getElementById("sendBtn");
  const backBtn = document.getElementById("backBtn");
  const log = document.getElementById("log");

  // ユーザーIDをAPIから取得
  currentUserId = await fetchUserId();
  if (!currentUserId) {
    showMessage("ユーザー情報が取得できません。ログインしてください。", true);
    deviceSelectSection.style.display = "none";
    return;
  }

  async function updateDeviceList() {
    deviceSelect.innerHTML = "";
    const devices = await fetchDevices(currentUserId);
    devices.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d.name;
      opt.textContent = d.name + (d.in_3d ? "（3D）" : "");
      deviceSelect.appendChild(opt);
    });
    showMessage("デバイス一覧を更新しました");
  }

  refreshBtn.onclick = updateDeviceList;

  createDeviceBtn.onclick = async () => {
    const name = newDeviceNameInput.value.trim();
    if (!name) {
      showMessage("新規デバイス名を入力してください", true);
      return;
    }
    const res = await createDevice(currentUserId, name);
    if (res.error_message) {
      showMessage(res.error_message, true);
    } else {
      showMessage("デバイス作成成功: " + res.name);
      await updateDeviceList();
    }
  };

  selectBtn.onclick = () => {
    const deviceName = deviceSelect.value;
    if (!deviceName) {
      showMessage("デバイスを選択してください", true);
      return;
    }
    currentDevice = deviceName;
    deviceSelectSection.style.display = "none";
    chatSection.style.display = "";
    startSocket();
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
      appendLog(`receive_data: ${JSON.stringify(data)}`);
    });
    socket.on("moved_3d", (data) => {
      appendLog(`moved_3d: ${JSON.stringify(data)}`);
    });
    socket.on("error", (data) => {
      appendLog(`error: ${JSON.stringify(data)}`);
    });
  }

  sendBtn.onclick = () => {
    if (!socket || !currentDevice) return;
    const msg = msgInput.value.trim();
    const move_device = moveDeviceInput.value.trim();
    if (!msg && !move_device) {
      appendLog("メッセージまたは3D移動先デバイス名を入力してください");
      return;
    }
    const data = { device_name: currentDevice };
    if (msg) data.msg = msg;
    if (move_device) data.move = { to_device_name: move_device };
    socket.emit("send_data", data);
    appendLog(`send_data送信: ${JSON.stringify(data)}`);
  };

  // 初期化
  updateDeviceList();
});
