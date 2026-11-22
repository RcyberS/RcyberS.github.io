(function () {
  var doc = document.documentElement;
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
})();
