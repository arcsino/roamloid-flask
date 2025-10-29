document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const messageDiv = document.getElementById("login-message");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    messageDiv.textContent = "";
    const username = form.username.value.trim();
    const password = form.password.value;
    if (!username || !password) {
      messageDiv.textContent = "ユーザー名とパスワードを入力してください。";
      messageDiv.className = "login-message error";
      return;
    }
    try {
      const res = await fetch(
        "https://roamloid-flask.onrender.com/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Origin: "http://localhost:5173",
          },
          credentials: "include",
          body: JSON.stringify({ username, password }),
        }
      );
      const data = await res.json();
      if (res.ok) {
        messageDiv.textContent = "ログイン成功: " + (data.message || "");
        messageDiv.className = "login-message success";
        location.href = "device.html";
      } else {
        messageDiv.textContent =
          data.error_message || "ログインに失敗しました。";
        messageDiv.className = "login-message error";
      }
    } catch (err) {
      messageDiv.textContent = "通信エラーが発生しました。";
      messageDiv.className = "login-message error";
    }
  });
});
