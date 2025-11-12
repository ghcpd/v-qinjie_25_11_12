// safe DOM updates: sanitize content and use textContent
(function(){
  function reflectHash() {
    var area = document.getElementById('hashArea');
    var h = location.hash.substring(1);
    if (!h) h = 'no-hash';
    // set textContent to avoid any HTML injection
    area.textContent = 'user hash: ' + h;
  }
  window.addEventListener('hashchange', reflectHash);
  window.addEventListener('load', reflectHash);
})();
