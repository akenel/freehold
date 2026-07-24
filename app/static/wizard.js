/* Freehold — turn a long form into a wizard you can walk, and tell people when
   something is happening.
 *
 * Two complaints, both fair, both from watching someone actually use the thing:
 *   "you press a button and don't see any progression — you don't know it happened"
 *   "I got to the end and couldn't really go back, it's a little bit clunky"
 *
 * So: one <form>, several panes, one visible at a time. Switching panes is
 * client-side, which is why it feels instant — there is no round trip and no
 * state to carry, because it is all still one form that submits once at the end.
 *
 * Progressive enhancement on purpose. With JS off, every pane is visible and the
 * page behaves exactly as it did before: one long form with one submit. Nothing
 * here is load-bearing for correctness — the gate, the ticks and the approval all
 * live on the server. This file only decides what you are looking at.
 */
(function () {
  "use strict";

  // ---- 1. the wizard --------------------------------------------------
  var root = document.querySelector("[data-wizard]");
  if (root) buildWizard(root);

  function buildWizard(root) {
    var panes = Array.prototype.slice.call(root.querySelectorAll("[data-step]"));
    if (panes.length < 2) return;
    root.classList.add("wiz-on");

    var bar = document.createElement("nav");
    bar.className = "wizbar";
    bar.setAttribute("aria-label", "Steps");

    var dots = panes.map(function (pane, i) {
      var b = document.createElement("button");
      b.type = "button";                    // never submit the form
      b.className = "wizdot";
      b.innerHTML = '<span class="n">' + (i + 1) + "</span><span class=\"l\">" +
        (pane.getAttribute("data-title") || "Step " + (i + 1)) + "</span>";
      // Every step is reachable at any time, forwards or back. This is a review
      // screen, not a payment funnel — locking someone out of step 2 because
      // they are "on" step 4 is the clunkiness being complained about.
      b.addEventListener("click", function () { go(i, true); });
      bar.appendChild(b);
      return b;
    });
    root.insertBefore(bar, root.firstChild);

    // Back / Next under each pane. The last pane keeps its own real submit
    // buttons and gets no Next — the end of the walk IS the decision.
    panes.forEach(function (pane, i) {
      var row = document.createElement("div");
      row.className = "wiznav";
      if (i > 0) row.appendChild(mk("← Back", function () { go(i - 1, true); }));
      if (i < panes.length - 1) {
        var next = mk("Next: " + (panes[i + 1].getAttribute("data-title") || "") + " →",
                      function () { go(i + 1, true); });
        next.className = "btn primary";
        row.appendChild(next);
      }
      pane.appendChild(row);
    });

    function mk(label, fn) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "btn ghost";
      b.textContent = label;
      b.addEventListener("click", fn);
      return b;
    }

    var at = -1;
    function go(i, push) {
      if (i < 0 || i >= panes.length || i === at) return;
      at = i;
      panes.forEach(function (p, n) { p.hidden = n !== i; });
      dots.forEach(function (d, n) {
        d.classList.toggle("on", n === i);
        d.classList.toggle("done", n < i);
        d.setAttribute("aria-current", n === i ? "step" : "false");
      });
      if (push) {
        // Real history entries, so the browser Back button walks the steps too —
        // which is what a person reaches for before they find our own Back.
        history.pushState({ wizStep: i }, "", "#step-" + (i + 1));
        root.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    window.addEventListener("popstate", function (e) {
      var i = e.state && typeof e.state.wizStep === "number" ? e.state.wizStep
            : stepFromHash();
      go(i, false);
    });

    function stepFromHash() {
      var m = /^#step-(\d+)$/.exec(location.hash || "");
      return m ? Math.min(panes.length, Math.max(1, parseInt(m[1], 10))) - 1 : 0;
    }

    go(stepFromHash(), false);
    history.replaceState({ wizStep: at }, "", "#step-" + (at + 1));
  }

  // ---- 2. "something is happening" ------------------------------------
  // Any form carrying data-busy shows an overlay and disables its submits, so a
  // click that takes 90 seconds looks different from a click that did nothing.
  Array.prototype.forEach.call(document.querySelectorAll("form[data-busy]"), function (form) {
    form.addEventListener("submit", function (ev) {
      if (form.dataset.busyDone) return;         // a resubmit we already handled
      // Let the browser's own validation win first.
      if (typeof form.checkValidity === "function" && !form.checkValidity()) return;
      form.dataset.busyDone = "1";

      var msg = form.getAttribute("data-busy") || "Working…";
      // The button actually pressed can override the message: reading a list and
      // running one take very different amounts of time and deserve to say so.
      var pressed = ev.submitter;
      if (pressed && pressed.getAttribute("data-busy")) msg = pressed.getAttribute("data-busy");

      Array.prototype.forEach.call(form.querySelectorAll("button[type=submit],button:not([type])"),
        function (b) { b.disabled = true; });

      var o = document.createElement("div");
      o.className = "busy";
      o.setAttribute("role", "status");
      o.setAttribute("aria-live", "polite");
      o.innerHTML = '<div class="busybox"><div class="spin" aria-hidden="true"></div>' +
                    '<div class="busymsg"></div>' +
                    '<div class="busysub">This page will move on by itself when it is done.</div></div>';
      o.querySelector(".busymsg").textContent = msg;   // never innerHTML: it can carry a filename
      document.body.appendChild(o);
      requestAnimationFrame(function () { o.classList.add("in"); });
    });
  });
})();
