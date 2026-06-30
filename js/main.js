/* js/main.js — Lotus & Fairways site-wide JavaScript */

(function() {

  // ── FAQ ACCORDION ──────────────────────────────────────
  document.addEventListener('click', e => {
    const btn = e.target.closest('.faq-q');
    if (!btn) return;
    const answer = btn.nextElementSibling;
    const icon   = btn.querySelector('.faq-icon');
    const isOpen = answer.classList.contains('open');
    // Close all
    document.querySelectorAll('.faq-a').forEach(a => a.classList.remove('open'));
    document.querySelectorAll('.faq-icon').forEach(i => i.classList.remove('open'));
    // Open clicked if it was closed
    if (!isOpen) {
      answer.classList.add('open');
      if (icon) icon.classList.add('open');
    }
  });

  // ── HERO SLIDESHOW ─────────────────────────────────────
  const slides   = document.querySelectorAll('.hero-slide');
  const dots     = document.querySelectorAll('.hero-dot');
  const caption  = document.getElementById('slide-caption');
  const captions = ['Thailand', 'Vietnam', 'Golf in Asia'];

  if (slides.length > 1) {
    let current = 0;
    let timer;

    function goToSlide(n) {
      slides[current].classList.remove('active');
      if (dots[current]) dots[current].classList.remove('active');
      current = (n + slides.length) % slides.length;
      slides[current].classList.add('active');
      if (dots[current]) dots[current].classList.add('active');
      if (caption && captions[current]) caption.textContent = captions[current];
      clearInterval(timer);
      timer = setInterval(nextSlide, 5000);
    }

    function nextSlide() { goToSlide(current + 1); }

    // Attach dot clicks
    dots.forEach((dot, i) => dot.addEventListener('click', () => goToSlide(i)));

    // Start
    timer = setInterval(nextSlide, 5000);

    // Expose for external use
    window.LF = window.LF || {};
    window.LF.goToSlide = goToSlide;
  }

  // ── NETLIFY FORM HANDLING ──────────────────────────────
  const enquiryForm = document.getElementById('enquiry-form');
  if (enquiryForm) {
    enquiryForm.addEventListener('submit', e => {
      e.preventDefault();
      const btn = enquiryForm.querySelector('.btn-submit');
      const note = enquiryForm.querySelector('.form-note');
      btn.textContent = 'Sending…';
      btn.disabled = true;

      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(new FormData(enquiryForm)).toString()
      })
      .then(() => {
        enquiryForm.innerHTML = `
          <div style="text-align:center; padding:40px 0;">
            <svg width="48" height="48" viewBox="0 0 100 100" style="margin:0 auto 20px;">
              <path d="M50,5 A45,45 0 0,0 50,95 A22.5,22.5 0 0,1 50,50 A22.5,22.5 0 0,0 50,5Z" fill="#c4607a"/>
              <path d="M50,5 A45,45 0 0,1 50,95 A22.5,22.5 0 0,0 50,50 A22.5,22.5 0 0,1 50,5Z" fill="#3a6040"/>
              <circle cx="50" cy="27.5" r="11.25" fill="#3a6040"/>
              <circle cx="50" cy="72.5" r="11.25" fill="#c4607a"/>
              <circle cx="50" cy="27.5" r="4.5" fill="#c4607a"/>
              <circle cx="50" cy="72.5" r="4.5" fill="#3a6040"/>
            </svg>
            <p style="font-family:'Cormorant Garamond',serif; font-size:1.4rem; color:#f7f3ec; margin-bottom:10px;">Thank you — we'll be in touch shortly.</p>
            <p style="font-size:0.82rem; color:rgba(247,243,236,0.5); line-height:1.8;">We aim to respond within one business day. In the meantime, feel free to call us on 01603 340142 (Norfolk) or 01625 802142 (Cheshire).</p>
          </div>`;
      })
      .catch(() => {
        btn.textContent = 'Send Enquiry →';
        btn.disabled = false;
        if (note) note.textContent = 'Something went wrong — please try again or call us directly.';
      });
    });
  }

  // ── SCOTLAND GUIDE DOWNLOAD FORM ──────────────────────
  const guideForm = document.getElementById('guide-form');
  if (guideForm) {
    guideForm.addEventListener('submit', e => {
      e.preventDefault();
      const btn = guideForm.querySelector('.btn-submit');
      btn.textContent = 'Preparing your guide…';
      btn.disabled = true;

      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(new FormData(guideForm)).toString()
      })
      .then(() => {
        // Trigger PDF download
        const link = document.createElement('a');
        link.href = '/downloads/LotusAndFairways_ScotlandGolfGuide.pdf';
        link.download = 'LotusAndFairways_ScotlandGolfGuide.pdf';
        link.click();
        // Show confirmation
        guideForm.innerHTML = `
          <div style="text-align:center; padding:32px 0;">
            <p style="font-family:'Cormorant Garamond',serif; font-size:1.3rem; color:#f7f3ec; margin-bottom:10px;">Your guide is downloading.</p>
            <p style="font-size:0.8rem; color:rgba(247,243,236,0.5); line-height:1.8;">We'll also send a copy to your email. Andy will be in touch personally within 24 hours.</p>
          </div>`;
      })
      .catch(() => {
        btn.textContent = 'Download Guide →';
        btn.disabled = false;
      });
    });
  }

  // ── SMOOTH SCROLL ──────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── LAZY IMAGE LOADING ────────────────────────────────
  if ('IntersectionObserver' in window) {
    const imgs = document.querySelectorAll('img[data-src]');
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          obs.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });
    imgs.forEach(img => observer.observe(img));
  }

})();
