/* TW Results: small, no dependencies. */
(function () {
  "use strict";
  // ---- Settings to fill in before launch ----
  var GA4_ID = "[GA4 ID]";            // e.g. G-XXXXXXXXXX. Analytics and the cookie bar stay off until this is real.
  // -------------------------------------------

  // Mobile menu
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Close" : "Menu";
    });
  }

  // Hero: cycle the trade in the mock search (skipped if the visitor prefers reduced motion)
  var t = document.getElementById("trade");
  if (t && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var trades = ["barber", "plumber", "hairdresser", "electrician", "beauty salon", "roofer", "builder"], i = 0;
    setInterval(function () { i = (i + 1) % trades.length; t.textContent = trades[i]; }, 2600);
  }

  // Enquiry form (Formspree): send in the background, show a thank-you on the page
  var form = document.getElementById("enquiry");
  if (form) {
    form.setAttribute("novalidate", "");
    var msg = document.getElementById("form-msg");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var show = function (text) { msg.textContent = text; msg.classList.add("show"); msg.focus(); };
      var hp = form.querySelector("[name=_gotcha]"); if (hp && hp.value) { return; } // spam trap filled: quietly ignore
      var missing = [].filter.call(form.querySelectorAll("[required]"), function (el) { return !el.value.trim(); });
      if (missing.length) { show("Please fill in your name, your trade or business, and a phone number or email."); missing[0].focus(); return; }
      var action = form.getAttribute("action") || "";
      if (action.indexOf("[") !== -1) {
        show("Preview only: the form isn't connected yet. Please email dan@twresults.com for now.");
        return;
      }
      var b = form.querySelector("button[type=submit]"); b.disabled = true; b.textContent = "Sending…";
      fetch(action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          form.reset();
          show("Thanks, that's come through. I'll run your free Google check and call you back within one working day. Dan");
        })
        .catch(function () { show("Sorry, that didn't send. Please email dan@twresults.com instead."); })
        .then(function () { b.disabled = false; b.textContent = "Send to Dan"; });
    });
  }

  // Privacy page: let the visitor change their cookie choice (clears it and shows the bar again)
  [].forEach.call(document.querySelectorAll("[data-cookie-reset]"), function (b) {
    b.addEventListener("click", function () {
      try { localStorage.removeItem("twr-consent"); } catch (e) {}
      location.reload();
    });
  });

  // Analytics: GA4 only loads after the visitor says yes
  if (GA4_ID.indexOf("[") === -1) {
    var KEY = "twr-consent", choice = null;
    try { choice = localStorage.getItem(KEY); } catch (e) {}
    var loadGA = function () {
      var s = document.createElement("script");
      s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_ID;
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag("js", new Date()); window.gtag("config", GA4_ID, { anonymize_ip: true });
    };
    if (choice === "yes") { loadGA(); }
    else if (choice !== "no") {
      var bar = document.getElementById("cookie");
      if (bar) {
        bar.hidden = false;
        // Keep the bar from covering the final CTA or the form: pad the page by the bar's height while it shows.
        var pad = function () {
          var base = window.matchMedia("(max-width:760px)").matches ? 74 : 0;
          document.body.style.paddingBottom = bar.hidden ? "" : (bar.getBoundingClientRect().height + base) + "px";
        };
        pad(); window.addEventListener("resize", pad);
        bar.addEventListener("click", function (e) {
          var v = e.target.getAttribute("data-consent"); if (!v) return;
          try { localStorage.setItem(KEY, v); } catch (err) {}
          bar.hidden = true; pad(); if (v === "yes") loadGA();
        });
      }
    }
  }
})();
