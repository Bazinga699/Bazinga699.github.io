/* Live counts rendered as native text. Shields supplies data, not badge images. */
(function () {
  'use strict';
  var cachePrefix = 'homepage-count-v1:';
  var cacheLifetime = 6 * 60 * 60 * 1000;
  var requests = new Map();

  // Upstream GitHub counts can be abbreviated (e.g. "1.2k"). Do not invent precision.
  function validCount(value) {
    return typeof value === 'string' && /^(?:\d+|\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?[kmb])$/i.test(value);
  }
  function displayCount(value) {
    return /^[\d,]+$/.test(value) ? Number(value.replace(/,/g, '')).toLocaleString('en-US') : value;
  }
  function readCache(url) {
    try {
      var saved = JSON.parse(localStorage.getItem(cachePrefix + url));
      if (saved && validCount(saved.value) && Number.isFinite(saved.savedAt)) return saved;
    } catch (error) { /* Storage can be disabled or full. Counts still load normally. */ }
    return null;
  }
  function loadCount(url) {
    if (!requests.has(url)) {
      var controller = new AbortController();
      var timer = setTimeout(function () { controller.abort(); }, 10000);
      var request = fetch(url, { signal: controller.signal, credentials: 'omit' })
        .then(function (response) {
          if (!response.ok) throw new Error('Count unavailable');
          return response.json();
        })
        .then(function (data) {
          var value = String(data.value == null ? data.message : data.value);
          if (data.isError || !validCount(value)) throw new Error('Invalid count');
          var saved = { value: value, savedAt: Date.now() };
          try { localStorage.setItem(cachePrefix + url, JSON.stringify(saved)); } catch (error) { /* Optional cache. */ }
          return saved;
        })
        .finally(function () { clearTimeout(timer); });
      requests.set(url, request);
    }
    return requests.get(url);
  }

  document.querySelectorAll('[data-count-url]').forEach(function (element) {
    var url = element.dataset.countUrl;
    var label = element.dataset.countLabel;
    var valueElement = element.querySelector('[data-count-value]');
    var labelElement = element.querySelector('[data-count-label-text]');
    var originalTitle = element.title;
    var saved = readCache(url);

    function render(count, stale) {
      valueElement.textContent = displayCount(count.value);
      labelElement.textContent = count.value === '1' ? label.slice(0, -1) : label;
      element.dataset.countState = stale ? 'cached' : 'ready';
      element.title = originalTitle + ' · ' + (stale ? 'Last available count, retrieved ' : 'Count retrieved ')
        + new Date(count.savedAt).toLocaleString('en-US');
    }
    if (saved) {
      render(saved, Date.now() - saved.savedAt >= cacheLifetime);
      if (Date.now() - saved.savedAt < cacheLifetime) return;
    }
    loadCount(url).then(function (count) {
      render(count, false);
    }).catch(function () {
      if (saved) render(saved, true);
      else {
        element.dataset.countState = 'unavailable';
        valueElement.textContent = '—';
        labelElement.textContent = label + ' unavailable';
        element.title = originalTitle + ' · Count temporarily unavailable';
      }
    });
  });
})();
