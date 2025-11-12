// vulnerable DOM logic
(function(){
  function reflectHash() {
    // intentionally uses innerHTML - DOM XSS
    var area = document.getElementById('hashArea');
    var h = location.hash.substring(1);
    if (!h) h = 'no-hash';
    area.innerHTML = 'user hash: ' + h;
  }
  window.addEventListener('hashchange', reflectHash);
  window.addEventListener('load', reflectHash);

  // also place debug information into console
  if (window.location.pathname === '/') {
    console.log('PUBLIC KEY AVAILABLE: ' + window.PUBLIC_API_KEY);
  }
})();
