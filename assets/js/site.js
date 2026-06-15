// Scroll-reveal: the single motion pattern from the editorial style guide.
// Above-the-fold elements reveal instantly (no wait); below-the-fold fade up on scroll.
(function () {
  var els = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if (!els.length) return;

  function show(el) { el.classList.add('is-visible'); }

  if (!('IntersectionObserver' in window)) {
    els.forEach(show);
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { show(entry.target); io.unobserve(entry.target); }
    });
  }, { threshold: 0.1 });

  // Reveal anything already in view synchronously so nothing is ever stuck hidden;
  // observe the rest for the scroll animation.
  function init() {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    els.forEach(function (el) {
      if (el.getBoundingClientRect().top < vh * 0.95) { show(el); }
      else { io.observe(el); }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

// Member directory: live faceted filter (search + topic + country). DOM-based,
// no fetch, so it works when the file is opened directly. Degrades to the full
// list if JS is off.
(function () {
  var form = document.getElementById('member-filters');
  var grid = document.getElementById('member-grid');
  if (!form || !grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.member-card'));
  var search = document.getElementById('f-search');
  var topic = document.getElementById('f-topic');
  var country = document.getElementById('f-country');
  var count = document.getElementById('member-count');
  var empty = document.getElementById('member-empty');
  var total = cards.length;

  // never let the scroll-reveal hide a directory card
  cards.forEach(function (c) { c.classList.add('is-visible'); });

  function listHas(attr, value) {
    return ('|' + attr).indexOf('|' + value + '|') !== -1;
  }

  function apply() {
    var q = (search.value || '').trim().toLowerCase();
    var t = topic.value;
    var c = country.value;
    var shown = 0;
    cards.forEach(function (card) {
      var ok = (!q || card.getAttribute('data-search').indexOf(q) !== -1)
        && (!t || listHas(card.getAttribute('data-topics'), t))
        && (!c || listHas(card.getAttribute('data-countries'), c));
      card.hidden = !ok;
      if (ok) shown++;
    });
    var filtered = q || t || c;
    count.textContent = filtered
      ? shown + ' of ' + total + ' members'
      : total + ' members';
    empty.hidden = shown !== 0;
  }

  function clear() {
    search.value = ''; topic.value = ''; country.value = ''; apply();
  }

  search.addEventListener('input', apply);
  topic.addEventListener('change', apply);
  country.addEventListener('change', apply);
  document.getElementById('f-clear').addEventListener('click', clear);
  var c2 = document.getElementById('f-clear2');
  if (c2) c2.addEventListener('click', clear);
  apply();
})();
