function startCountdowns() {
  const countdowns = document.querySelectorAll(".countdown");

  countdowns.forEach(el => {
    const endTimeStr = el.dataset.end;

    if (!endTimeStr) {
      el.textContent = "Unknown";
      return;
    }

    const [hours, minutes] = endTimeStr.split(":").map(Number);
    const now = new Date();
    const expiresAt = new Date(now);
    expiresAt.setHours(hours, minutes, 0, 0);

    // If pickup_end is earlier than current time (e.g., posted yesterday), assume it's tomorrow
    if (expiresAt < now) {
      expiresAt.setDate(now.getDate() + 1);
    }

    function update() {
      const now = new Date();
      const remaining = expiresAt - now;

      if (remaining <= 0) {
        el.textContent = "Expired";
        el.classList.add("text-danger");
        return;
      }

      const mins = Math.floor(remaining / 60000);
      const secs = Math.floor((remaining % 60000) / 1000);
      el.textContent = `${mins}m ${secs < 10 ? "0" : ""}${secs}s`;
      el.classList.remove("text-danger");
    }

    update();
    setInterval(update, 1000);
  });
}

document.addEventListener("DOMContentLoaded", startCountdowns);
