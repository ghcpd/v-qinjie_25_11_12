// Vulnerable client-side behaviors for Project A
(function(){
  try {
    const keyEl = document.getElementById('apiKey');
    if (keyEl) {
      // Leaking API key to localStorage and console
      const apiKey = keyEl.innerText || keyEl.textContent;
      console.log('DEBUG: Exposing API Key in console:', apiKey);
      localStorage.setItem('API_KEY', apiKey);
    }

    // Expose unsafe DOM APIs for demo: read from querystring to allow DOM XSS
    function getQueryParam(name) {
      const params = new URLSearchParams(window.location.search);
      return params.get(name);
    }

    const dangerous = getQueryParam('dangerous');
    if (dangerous) {
      // Unsafe innerHTML injection
      const zone = document.getElementById('commentZone');
      if (zone) zone.innerHTML = dangerous;
    }
  } catch (e) {
    console.error('VulnJS error', e);
  }
})();
