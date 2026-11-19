// Runs in <head> before the page paints, so the saved theme never flashes.
(function () {
  var d = document.documentElement, t = null;
  try { t = localStorage.getItem("theme"); } catch (e) {}
  d.setAttribute("data-theme", t === "light" || t === "dark" ? t : "dark");
  d.classList.add("js");
})();
