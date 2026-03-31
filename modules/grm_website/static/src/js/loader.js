(function () {
  var loader = document.getElementById('page-loader');
  if (!loader) return;
  $('[href*="sortby=users"]').remove();

  function hideLoader() {
    loader.setAttribute('aria-hidden', 'true');

    loader.classList.add('hidden');

    setTimeout(function () {
      if (loader && loader.parentNode) {
        loader.parentNode.removeChild(loader);
      }
    }, 500);
  }

  if (document.readyState === 'complete') {
    hideLoader();
    return;
  }

  window.addEventListener('load', hideLoader);

  setTimeout(function () {
    if (document.readyState !== 'complete') {
      hideLoader();
    }
  }, 8000);
})();