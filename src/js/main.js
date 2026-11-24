(function () {
  var doc = document.documentElement;
  doc.classList.add("ready");

  // theme switch
  var btn = document.querySelector(".theme");
  if (btn) {
    var sync = function () { btn.setAttribute("aria-pressed", doc.getAttribute("data-theme") === "dark" ? "true" : "false"); };
    sync();
    btn.addEventListener("click", function () {
      var next = doc.getAttribute("data-theme") === "dark" ? "light" : "dark";
      doc.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      sync();
    });
  }
  document.querySelectorAll(".lang a[hreflang]").forEach(function (a) {
    a.addEventListener("click", function () { try { localStorage.setItem("lang", a.getAttribute("hreflang")); } catch (e) {} });
  });

  // the log-flow diagram stands still for people who ask for less motion
  var map = document.querySelector(".flowmap");
  if (map && window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches && map.pauseAnimations) {
    map.pauseAnimations();
  }

  // the case list and the timeline come in once, when they reach the screen
  var targets = document.querySelectorAll(".cards, .xp");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -12% 0px" });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add("is-in"); });
  }

  // screenshots open full size with their notes
  var viewer = document.querySelector(".viewer");
  var links = Array.prototype.slice.call(document.querySelectorAll(".thumb__link"));
  if (viewer && links.length && typeof viewer.showModal === "function") {
    var img = viewer.querySelector(".viewer__img"), notes = viewer.querySelector(".viewer__notes"), count = viewer.querySelector(".viewer__count"), at = 0, opener = null;
    var show = function (i) {
      at = (i + links.length) % links.length;
      var a = links[at], src = a.querySelector("img");
      img.src = a.getAttribute("href"); img.alt = src.alt;
      img.width = +a.dataset.w; img.height = +a.dataset.h;
      notes.innerHTML = a.parentNode.querySelector(".notes").innerHTML;
      count.textContent = (at + 1) + " / " + links.length;
    };
    links.forEach(function (a, i) {
      a.addEventListener("click", function (ev) { ev.preventDefault(); opener = a; show(i); viewer.showModal(); });
    });
    viewer.querySelectorAll("[data-go]").forEach(function (b) {
      b.addEventListener("click", function () { show(at + (+b.dataset.go)); });
    });
    viewer.querySelector(".viewer__close").addEventListener("click", function () { viewer.close(); });
    viewer.addEventListener("click", function (ev) { if (ev.target === viewer) viewer.close(); });
    viewer.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowRight") show(at + 1);
      if (ev.key === "ArrowLeft") show(at - 1);
    });
    viewer.addEventListener("close", function () { if (opener) opener.focus(); });
  }
})();
