// Safe client-side behavior: we avoid innerHTML and use textContent
(function(){
  try {
    const keyEl = document.getElementById('apiKey');
    if (keyEl) {
      // Masked display only; do not store secrets in localStorage or console
      // No console.debug of API key
    }

    // Safe rendering: if a 'dangerous' query param exists, render it as text
    function getQueryParam(name) {
      const params = new URLSearchParams(window.location.search);
      return params.get(name);
    }

    const dangerous = getQueryParam('dangerous');
    if (dangerous) {
      const zone = document.getElementById('commentZone');
      if (zone) zone.textContent = dangerous; // safe assignment
    }

  } catch (e) {
    // Log for diagnostics but no sensitive information
    console.error('SafeJS error', e && e.message);
  }
})();
