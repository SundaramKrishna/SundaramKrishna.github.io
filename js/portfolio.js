(() => {
  const illustration = document.querySelector('.profile-illustration');
  if (!illustration || !('IntersectionObserver' in window)) return;

  const motion = window.matchMedia('(prefers-reduced-motion: no-preference)');
  if (!motion.matches || !motion.addEventListener) return;

  const threshold = 0.3;
  const assemble = () => {
    illustration.classList.add('is-assembled');
    observer.disconnect();
    motion.removeEventListener('change', handleMotionChange);
  };
  const handleMotionChange = event => {
    if (!event.matches) assemble();
  };
  const observer = new IntersectionObserver(entries => {
    if (entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= threshold)) {
      assemble();
    }
  }, { threshold });

  motion.addEventListener('change', handleMotionChange);
  illustration.classList.add('motion-ready');
  observer.observe(illustration);
})();

(() => {
  const shell = document.querySelector('.nav-shell');
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  if (!shell || !menu || !nav) return;
  shell.classList.add('enhanced');
  menu.hidden = false;
  const closeMenu = () => {
    nav.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.textContent = 'Menu';
  };
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.textContent = open ? 'Close' : 'Menu';
    nav.classList.toggle('is-open', open);
  });
  nav.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || menu.getAttribute('aria-expanded') !== 'true') return;
    closeMenu();
    const target = link.hash && document.getElementById(link.hash.slice(1));
    if (target) target.focus({ preventScroll: true });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menu.focus();
    }
  });
  window.matchMedia('(min-width: 761px)').addEventListener('change', closeMenu);
})();
