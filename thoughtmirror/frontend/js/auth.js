console.log("auth.js loaded ✅");

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  if (!form) {
    console.error("loginForm not found ❌");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    console.log("Login clicked", email);

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      console.log("Backend response:", data);

      if (data.user_id) {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("email", data.email);

        window.location.href = "dashboard.html";
      } else {
        alert("Login failed");
      }

    } catch (err) {
      console.error("Fetch error:", err);
      alert("Backend not running");
    }
  });
});
