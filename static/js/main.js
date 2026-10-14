document.addEventListener('DOMContentLoaded', () => {
  // 1. Navbar shrinks and gets a blur after scrolling
  const navbar = document.getElementById('mainNavbar');
  const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 40);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // 2. Fade-in on scroll for any element with class "reveal"
  const items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    items.forEach((el) => observer.observe(el));
  } else {
    items.forEach((el) => el.classList.add('visible'));
  }

  // 3. Auto-hide Django messages after 4 seconds
  document.querySelectorAll('.alert').forEach((alert) => {
    setTimeout(() => {
      bootstrap.Alert.getOrCreateInstance(alert).close();
    }, 4000);
  });
});

// 4. Call this later when an item is added to the cart
function bumpCartBadge(newCount) {
  const badge = document.getElementById('cartCount');
  if (!badge) return;
  if (newCount !== undefined) badge.textContent = newCount;
  badge.classList.remove('bump');
  void badge.offsetWidth; // restarts the animation
  badge.classList.add('bump');
}