// Freehold — nav status bar: a live clock (with seconds) and a real health dot.
(function () {
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function tick() {
    var c = document.getElementById('clock');
    if (!c) return;
    var d = new Date();
    c.textContent = pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
  }

  function health() {
    var dot = document.getElementById('health-dot');
    if (!dot) return;
    fetch('/healthz', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (j) { dot.className = 'pulse ' + (j.status === 'ok' ? 'ok' : 'error'); })
      .catch(function () { dot.className = 'pulse error'; });
  }

  tick();
  setInterval(tick, 1000);      // clock ticks every second
  health();
  setInterval(health, 20000);   // re-probe health every 20s
})();
