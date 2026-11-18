// Small progressive enhancements. The site works without this file.
(function () {
  var root = document.documentElement;

  // Today's date in the top bar (set at view time so it never goes stale).
  var today = document.getElementById("today");
  if (today) {
    today.textContent = new Date().toLocaleDateString("en-US", {
      weekday: "long", year: "numeric", month: "long", day: "numeric"
    });
  }

  // Light/dark toggle. The choice is remembered; otherwise the system setting wins.
  var toggle = document.querySelector(".theme-toggle");
  function isDark() {
    var t = root.dataset.theme;
    if (t) return t === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function syncToggle() {
    if (toggle) toggle.setAttribute("aria-pressed", isDark() ? "true" : "false");
  }
  if (toggle) {
    syncToggle();
    toggle.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) {}
      syncToggle();
    });
  }

  // Category menu on phones: bring the current section into view and drop the
  // "more to scroll" fade once the end is reached.
  var list = document.querySelector(".catnav ul");
  if (list) {
    var active = list.querySelector("a.active");
    if (active && list.scrollWidth > list.clientWidth) {
      list.scrollLeft = active.offsetLeft - (list.clientWidth - active.offsetWidth) / 2;
    }
    var checkEnd = function () {
      list.classList.toggle("at-end", list.scrollLeft + list.clientWidth >= list.scrollWidth - 4);
    };
    list.addEventListener("scroll", checkEnd, { passive: true });
    window.addEventListener("resize", checkEnd);
    checkEnd();
  }

  // Compact logo in the sticky menu once the masthead is gone; back-to-top button
  // only after a screen or so of scrolling.
  var masthead = document.querySelector(".masthead");
  function onScroll() {
    var y = window.scrollY;
    var mastBottom = masthead ? masthead.offsetTop + masthead.offsetHeight : 0;
    root.classList.toggle("scrolled", y > mastBottom);
    root.classList.toggle("show-top", y > window.innerHeight * 1.2);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
