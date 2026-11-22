/* Kiran & Anju — small enhancements. The page is fully readable without this file. */
(function () {
  'use strict';

  /* ---------- countdown ---------- */
  var box = document.querySelector('.countdown[data-to]');
  if (box) {
    var target = new Date(box.getAttribute('data-to')).getTime();
    var cells = {};
    box.querySelectorAll('[data-unit]').forEach(function (el) { cells[el.getAttribute('data-unit')] = el; });
    var pad = function (n) { return n < 10 ? '0' + n : String(n); };

    var tick = function () {
      var left = target - Date.now();
      if (isNaN(target) || left <= 0) {
        box.classList.add('is-past');
        return false;
      }
      var s = Math.floor(left / 1000);
      cells.d.textContent = Math.floor(s / 86400);
      cells.h.textContent = pad(Math.floor(s % 86400 / 3600));
      cells.m.textContent = pad(Math.floor(s % 3600 / 60));
      cells.s.textContent = pad(s % 60);
      return true;
    };
    if (tick()) {
      var timer = setInterval(function () { if (!tick()) clearInterval(timer); }, 1000);
    }
  }

  /* ---------- reveal on scroll ---------- */
  var items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('is-in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
  items.forEach(function (el) { io.observe(el); });

  /* make sure print / save-as-PDF shows everything */
  window.addEventListener('beforeprint', function () {
    items.forEach(function (el) { el.classList.add('is-in'); });
  });
})();
