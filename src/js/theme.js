// Runs before the first paint so a saved theme never flashes.
(function () {
  var t = null;
  try { t = localStorage.getItem("theme"); } catch (e) {}
  document.documentElement.setAttribute("data-theme", t === "dark" ? "dark" : "light");
})();
