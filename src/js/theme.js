// Runs before the first paint so a saved theme never flashes.
(function () {
  var d = document.documentElement, t = null;
  try { t = localStorage.getItem("theme"); } catch (e) {}
  d.setAttribute("data-theme", t === "dark" ? "dark" : "light");
  d.classList.add("js");
  // if the main script never runs, nothing stays hidden
  setTimeout(function () { if (!d.classList.contains("ready")) d.classList.remove("js"); }, 2500);
})();
