// DOM-based XSS: unsafe innerHTML insertion 

document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('insert-dom');
  const commentInput = document.getElementById('comment');
  const domArea = document.getElementById('dom-area');
  const apiKey = document.getElementById('api-key').innerText;

  // Persist api key in localStorage (vulnerable for secrets exposure)
  localStorage.setItem('api_key', apiKey);

  btn.addEventListener('click', function () {
    const value = commentInput.value || '';
    // Unsafe: innerHTML will evaluate and insert scripts
    domArea.innerHTML = '<div class="comment">' + value + '</div>';
  });

  document.getElementById('log-secret').addEventListener('click', function () {
    console.log('API Key (leaked):', apiKey);
  });
});
