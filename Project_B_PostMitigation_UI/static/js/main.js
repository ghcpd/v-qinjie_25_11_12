document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('insert-dom');
  const commentInput = document.getElementById('comment');
  const domArea = document.getElementById('dom-area');

  btn.addEventListener('click', function () {
    const value = commentInput.value || '';
    // Safe insertion using textContent — prevents script execution
    const div = document.createElement('div');
    div.className = 'comment';
    div.textContent = value; // never innerHTML
    domArea.appendChild(div);
  });
});
