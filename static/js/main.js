// function parseDuration(text) {
//   const [num, unit] = text.toLowerCase().split(" ");
//   const n = parseInt(num);
//   if (unit.startsWith("hour")) return n * 3600;
//   if (unit.startsWith("min")) return n * 60;
//   return 1800; // default to 30 mins if unrecognized
// }

// function updateCountdowns() {
//   document.querySelectorAll(".countdown").forEach(el => {
//     const createdAt = new Date(el.dataset.created);
//     const durationSec = parseDuration(el.dataset.duration);
//     const expiresAt = new Date(createdAt.getTime() + durationSec * 1000);
//     const now = new Date();
//     const secondsLeft = Math.floor((expiresAt - now) / 1000);

//     if (secondsLeft <= 0) {
//       el.textContent = "Expired";
//     } else {
//       const mins = Math.floor(secondsLeft / 60);
//       const secs = secondsLeft % 60;
//       el.textContent = `${mins}m ${secs < 10 ? '0' : ''}${secs}s`;
//     }
//   });
// }

// setInterval(updateCountdowns, 1000);

// Countdown for student dashboard
function startCountdowns() {
  const countdowns = document.querySelectorAll(".countdown");

  countdowns.forEach(el => {
    const created = new Date(el.dataset.created);
    const durationText = el.dataset.duration.toLowerCase();

    let duration = 0;

    if (durationText.includes("hour")) {
      duration = parseFloat(durationText) * 60 * 60 * 1000;
    } else if (durationText.includes("min")) {
      duration = parseFloat(durationText) * 60 * 1000;
    } else if (!isNaN(parseFloat(durationText))) {
      // If it's just a number with no unit, assume minutes
      duration = parseFloat(durationText) * 60 * 1000;
    } else {
      duration = 30 * 60 * 1000; // fallback
    }
    

    const expiresAt = new Date(created.getTime() + duration);

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
      el.textContent = `${mins}m ${secs}s`;
      el.classList.remove("text-danger");
    }

    update();
    setInterval(update, 1000);
  });
}

document.addEventListener("DOMContentLoaded", startCountdowns);
