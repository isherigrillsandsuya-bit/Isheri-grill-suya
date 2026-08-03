document.body.addEventListener('htmx:configRequest', (event) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  if (csrfToken) {
    event.detail.headers['X-CSRFToken'] = csrfToken;
  }
});

window.addEventListener('DOMContentLoaded', () => {
  const heroSlides = document.querySelectorAll('.landing-slide');
  if (!heroSlides.length) return;

  let activeIndex = 0;
  const rotateSlides = () => {
    heroSlides.forEach((slide, index) => {
      slide.classList.toggle('opacity-100', index === activeIndex);
      slide.classList.toggle('opacity-0', index !== activeIndex);
    });
    activeIndex = (activeIndex + 1) % heroSlides.length;
  };

  heroSlides.forEach((slide, index) => {
    slide.style.transition = 'opacity 1s ease';
    slide.style.opacity = index === 0 ? '1' : '0';
  });

  setInterval(rotateSlides, 5000);
});
