(function () {
  var doc = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Theme toggle
  var themeBtn = document.querySelector(".theme-toggle");
  if (themeBtn) {
    var sync = function () {
      var dark = doc.getAttribute("data-theme") !== "light";
      themeBtn.setAttribute("aria-pressed", dark ? "true" : "false");
    };
    sync();
    themeBtn.addEventListener("click", function () {
      var next = doc.getAttribute("data-theme") === "light" ? "dark" : "light";
      doc.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      sync();
    });
  }

  // Mobile menu
  var menuBtn = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (menuBtn && nav) {
    var close = function () { nav.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); };
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { close(); menuBtn.focus(); }
    });
  }

  // Remember the language the visitor picked
  document.querySelectorAll(".lang a[hreflang]").forEach(function (a) {
    a.addEventListener("click", function () {
      try { localStorage.setItem("lang", a.getAttribute("hreflang")); } catch (e) {}
    });
  });

  // Home: network background (decorative)
  var canvas = document.getElementById("net");
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext("2d"), hero = canvas.parentElement;
    var W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2), nodes = [], pulses = [], running = false, onScreen = true;
    var css = function (name) { return getComputedStyle(doc).getPropertyValue(name).trim(); };
    var size = function () {
      W = canvas.offsetWidth; H = canvas.offsetHeight;
      canvas.width = W * dpr; canvas.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    var init = function () {
      size(); nodes = []; pulses = [];
      var n = Math.max(24, Math.min(90, Math.round(W * H / 24000)));
      for (var i = 0; i < n; i++) nodes.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .22, vy: (Math.random() - .5) * .22, r: Math.random() * 1.6 + 1.1 });
    };
    var frame = function () {
      var blue = css("--blue"), red = css("--red"), light = doc.getAttribute("data-theme") === "light";
      ctx.clearRect(0, 0, W, H);
      ctx.globalAlpha = light ? .55 : 1;
      for (var i = 0; i < nodes.length; i++) {
        var a = nodes[i];
        if (!reduce) { a.x += a.vx; a.y += a.vy; if (a.x < 0 || a.x > W) a.vx *= -1; if (a.y < 0 || a.y > H) a.vy *= -1; }
        for (var j = i + 1; j < nodes.length; j++) {
          var b = nodes[j], dx = a.x - b.x, dy = a.y - b.y, dd = dx * dx + dy * dy;
          if (dd < 19600) { ctx.strokeStyle = blue; ctx.globalAlpha = (light ? .12 : .16) * (1 - Math.sqrt(dd) / 140); ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
        }
      }
      ctx.globalAlpha = light ? .45 : .7; ctx.fillStyle = blue;
      for (i = 0; i < nodes.length; i++) { ctx.beginPath(); ctx.arc(nodes[i].x, nodes[i].y, nodes[i].r, 0, 7); ctx.fill(); }
      for (i = pulses.length - 1; i >= 0; i--) {
        var p = pulses[i]; p.t++; var k = p.t / 60;
        ctx.strokeStyle = red; ctx.fillStyle = red; ctx.lineWidth = 2;
        ctx.globalAlpha = 1 - k; ctx.beginPath(); ctx.arc(p.n.x, p.n.y, 4 + k * 26, 0, 7); ctx.stroke();
        ctx.beginPath(); ctx.arc(p.n.x, p.n.y, 3, 0, 7); ctx.fill();
        if (p.t >= 60) pulses.splice(i, 1);
      }
      ctx.globalAlpha = 1; ctx.lineWidth = 1;
    };
    var loop = function () { if (!running) return; frame(); requestAnimationFrame(loop); };
    var run = function (on) {
      if (reduce) { frame(); return; }
      if (on && !running) { running = true; requestAnimationFrame(loop); } else if (!on) running = false;
    };
    init(); run(true);
    var lastW = window.innerWidth, t;
    window.addEventListener("resize", function () {
      clearTimeout(t);
      t = setTimeout(function () { if (window.innerWidth !== lastW) { lastW = window.innerWidth; init(); } else size(); if (reduce) frame(); }, 150);
    });
    if ("IntersectionObserver" in window) new IntersectionObserver(function (e) { onScreen = e[0].isIntersecting; run(onScreen && !document.hidden); }).observe(hero);
    document.addEventListener("visibilitychange", function () { run(onScreen && !document.hidden); });
    if (!reduce) setInterval(function () { if (running && nodes.length) pulses.push({ n: nodes[Math.floor(Math.random() * nodes.length)], t: 0 }); }, 1500);
    if (themeBtn && reduce) themeBtn.addEventListener("click", frame);
  }

  // Home: rotate the example alerts
  var feed = document.getElementById("feed"), tpl = document.getElementById("feed-items");
  if (feed && tpl && !reduce) {
    var items = tpl.content.querySelectorAll("li"), k = feed.children.length;
    setInterval(function () {
      if (document.hidden) return;
      feed.insertBefore(items[k++ % items.length].cloneNode(true), feed.firstChild);
      while (feed.children.length > 4) feed.removeChild(feed.lastChild);
    }, 3000);
  }

  // Contact form
  var form = document.querySelector("form.contact");
  if (form) {
    var status = form.querySelector(".form-status");
    var msg = function (key) { return form.getAttribute("data-" + key); };
    var check = function (field) {
      var input = form.querySelector("#" + field), err = form.querySelector("#" + field + "-error"), text = "";
      if (input.validity.valueMissing) text = msg("required");
      else if (input.validity.typeMismatch) text = msg("email");
      else if (input.validity.tooShort) text = msg("short");
      err.textContent = text;
      if (text) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
      return !text;
    };
    ["name", "email", "message"].forEach(function (f) {
      var el = form.querySelector("#" + f);
      el.addEventListener("blur", function () { if (el.value) check(f); });
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true, first = null;
      ["name", "email", "message"].forEach(function (f) { if (!check(f)) { ok = false; first = first || form.querySelector("#" + f); } });
      if (!ok) { first.focus(); return; }
      var btn = form.querySelector("button[type=submit]");
      btn.disabled = true; status.className = "form-status"; status.textContent = msg("sending");
      fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(Object.fromEntries(new FormData(form))) })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.success) { form.reset(); status.className = "form-status ok"; status.textContent = msg("sent"); }
          else throw new Error();
        })
        .catch(function () { status.className = "form-status fail"; status.textContent = msg("failed"); })
        .then(function () { btn.disabled = false; });
    });
  }

  // Cookie consent + Google Analytics (loads only after "Accept")
  var banner = document.getElementById("consent");
  if (banner) {
    var GA = banner.getAttribute("data-ga"), MAX = 395 * 864e5; // about 13 months
    var read = function () {
      try { var c = JSON.parse(localStorage.getItem("consent")); if (c && Date.now() - c.t < MAX) return c.v; } catch (e) {}
      return null;
    };
    var loadGA = function () {
      if (window.gaLoaded) return; window.gaLoaded = true;
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag("js", new Date());
      window.gtag("config", GA);
      var s = document.createElement("script"); s.async = true;
      s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA);
      document.head.appendChild(s);
    };
    var clearGA = function () {
      document.cookie.split(";").forEach(function (c) {
        var n = c.split("=")[0].trim();
        if (n.indexOf("_ga") === 0) {
          var host = location.hostname, parts = host.split(".");
          [host, "." + host, "." + parts.slice(-2).join(".")].forEach(function (d) {
            document.cookie = n + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=" + d;
          });
          document.cookie = n + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
        }
      });
    };
    var opener = null;
    var show = function () { banner.hidden = false; };
    var hide = function () { banner.hidden = true; if (opener) { opener.focus(); opener = null; } };
    var choice = read();
    if (choice === "granted") loadGA(); else if (choice !== "denied") show();
    banner.querySelectorAll("[data-consent]").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-consent"), before = read();
        try { localStorage.setItem("consent", JSON.stringify({ v: v, t: Date.now() })); } catch (e) {}
        hide();
        if (v === "granted") loadGA();
        else if (before === "granted" || window.gaLoaded) { clearGA(); location.reload(); }
      });
    });
    document.querySelectorAll("[data-consent-open]").forEach(function (b) {
      b.addEventListener("click", function () { opener = b; show(); banner.querySelector("[data-consent]").focus(); });
    });
  }
})();
