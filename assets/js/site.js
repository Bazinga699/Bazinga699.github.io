/* Progressive navigation: links stay available when JavaScript is disabled. */
(function () {
  'use strict';
  var nav = document.getElementById('site-nav');
  if (!nav) return;
  var toggle = nav.querySelector('button');
  var links = nav.querySelectorAll('.site-nav__links a');
  var desktop = window.matchMedia('(min-width: 64rem)');

  function closeMenu(returnFocus) {
    nav.dataset.open = 'false';
    toggle.setAttribute('aria-expanded', 'false');
    if (returnFocus) toggle.focus();
  }
  nav.dataset.enhanced = 'true';
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') !== 'true';
    nav.dataset.open = String(open);
    toggle.setAttribute('aria-expanded', String(open));
  });
  nav.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      closeMenu(true);
    }
  });
  document.addEventListener('click', function (event) {
    if (!nav.contains(event.target)) closeMenu(false);
  });
  nav.addEventListener('focusout', function (event) {
    if (event.relatedTarget && !nav.contains(event.relatedTarget)) closeMenu(false);
  });
  nav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      closeMenu(false);
      var target = document.getElementById(link.hash.slice(1));
      if (target) {
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      }
    });
  });
  desktop.addEventListener('change', function () {
    var focusedLink = nav.querySelector('.site-nav__links').contains(document.activeElement);
    closeMenu(!desktop.matches && focusedLink);
  });

  // Match the highlighted link to the section immediately below the sticky bar.
  var sections = Array.from(links).map(function (link) {
    return { link: link, target: document.getElementById(link.hash.slice(1)) };
  }).filter(function (section) { return section.target; });
  var scheduled = false;
  function updateCurrentSection() {
    var current = sections[0];
    var offset = nav.offsetHeight + 40;
    // Source order may differ from navigation order, so choose the nearest heading above the bar.
    var passed = sections.filter(function (section) { return section.target.getBoundingClientRect().top <= offset; });
    if (passed.length) current = passed.sort(function (a, b) {
      return b.target.getBoundingClientRect().top - a.target.getBoundingClientRect().top;
    })[0];
    sections.forEach(function (section) {
      if (section === current) section.link.setAttribute('aria-current', 'location');
      else section.link.removeAttribute('aria-current');
    });
    scheduled = false;
  }
  function scheduleUpdate() {
    if (!scheduled) { scheduled = true; window.requestAnimationFrame(updateCurrentSection); }
  }
  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate, { passive: true });
  window.addEventListener('load', scheduleUpdate);
  updateCurrentSection();
})();
