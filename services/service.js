(function () {
  var topButton = document.querySelector('.top-button');
  if (!topButton) return;

  function toggleTopButton() {
    if (window.scrollY > 420) {
      topButton.classList.add('visible');
    } else {
      topButton.classList.remove('visible');
    }
  }

  topButton.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  window.addEventListener('scroll', toggleTopButton, { passive: true });
  toggleTopButton();
})();
