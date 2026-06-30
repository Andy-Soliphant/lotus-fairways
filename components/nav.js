/* components/nav.js — Lotus & Fairways shared navigation */

(function() {
  // The mark SVG — used in nav and footer
  const MARK_SVG = (size = 38) => `
    <svg width="${size}" height="${size}" viewBox="0 0 100 100" aria-hidden="true">
      <circle cx="50" cy="50" r="48" fill="none" stroke="#c49a5e" stroke-width="2"/>
      <path d="M50,5 A45,45 0 0,0 50,95 A22.5,22.5 0 0,1 50,50 A22.5,22.5 0 0,0 50,5Z" fill="currentRose"/>
      <path d="M50,5 A45,45 0 0,1 50,95 A22.5,22.5 0 0,0 50,50 A22.5,22.5 0 0,1 50,5Z" fill="currentGreen"/>
      <circle cx="50" cy="27.5" r="11.25" fill="currentGreen"/>
      <circle cx="50" cy="72.5" r="11.25" fill="currentRose"/>
      <circle cx="50" cy="27.5" r="4.5" fill="currentRose"/>
      <circle cx="50" cy="72.5" r="4.5" fill="currentGreen"/>
      <text x="20" y="70" font-family="Cormorant Garamond, serif" font-size="24" font-style="italic" font-weight="400" fill="currentGreenText" opacity="0.75">L</text>
      <text x="55" y="42" font-family="Cormorant Garamond, serif" font-size="24" font-weight="300" fill="currentRoseText" opacity="0.75">F</text>
    </svg>`;

  // SVG with actual colour values
  const markLight = (size = 38) => `
    <svg width="${size}" height="${size}" viewBox="0 0 100 100" aria-hidden="true">
      <circle cx="50" cy="50" r="48" fill="none" stroke="#c49a5e" stroke-width="2"/>
      <path d="M50,5 A45,45 0 0,0 50,95 A22.5,22.5 0 0,1 50,50 A22.5,22.5 0 0,0 50,5Z" fill="#9b3a5a"/>
      <path d="M50,5 A45,45 0 0,1 50,95 A22.5,22.5 0 0,0 50,50 A22.5,22.5 0 0,1 50,5Z" fill="#2a4a2e"/>
      <circle cx="50" cy="27.5" r="11.25" fill="#2a4a2e"/>
      <circle cx="50" cy="72.5" r="11.25" fill="#9b3a5a"/>
      <circle cx="50" cy="27.5" r="4.5" fill="#9b3a5a"/>
      <circle cx="50" cy="72.5" r="4.5" fill="#2a4a2e"/>
      <text x="20" y="70" font-family="Cormorant Garamond, serif" font-size="24" font-style="italic" font-weight="400" fill="#2a4a2e" opacity="0.75">L</text>
      <text x="55" y="42" font-family="Cormorant Garamond, serif" font-size="24" font-weight="300" fill="#9b3a5a" opacity="0.75">F</text>
    </svg>`;

  const markDark = (size = 38) => `
    <svg width="${size}" height="${size}" viewBox="0 0 100 100" aria-hidden="true">
      <circle cx="50" cy="50" r="48" fill="none" stroke="#c49a5e" stroke-width="2"/>
      <path d="M50,5 A45,45 0 0,0 50,95 A22.5,22.5 0 0,1 50,50 A22.5,22.5 0 0,0 50,5Z" fill="#c4607a"/>
      <path d="M50,5 A45,45 0 0,1 50,95 A22.5,22.5 0 0,0 50,50 A22.5,22.5 0 0,1 50,5Z" fill="#3a6040"/>
      <circle cx="50" cy="27.5" r="11.25" fill="#3a6040"/>
      <circle cx="50" cy="72.5" r="11.25" fill="#c4607a"/>
      <circle cx="50" cy="27.5" r="4.5" fill="#c4607a"/>
      <circle cx="50" cy="72.5" r="4.5" fill="#3a6040"/>
      <text x="20" y="70" font-family="Cormorant Garamond, serif" font-size="24" font-style="italic" font-weight="400" fill="#3a6040" opacity="0.82">L</text>
      <text x="55" y="42" font-family="Cormorant Garamond, serif" font-size="24" font-weight="300" fill="#c4607a" opacity="0.82">F</text>
    </svg>`;

  // Detect active page for nav highlighting
  const path = window.location.pathname;
  const isGolf    = path.includes('/golf-in-asia');
  const isBeyond  = path.includes('/beyond');
  const isDest    = path.includes('/destinations');

  // Build nav HTML
  const navHTML = `
    <nav class="nav" id="main-nav" role="navigation" aria-label="Main navigation">
      <div class="nav-left">
        <a href="/" class="nav-brand" aria-label="Lotus & Fairways home">
          ${markLight(38)}
          <div class="nav-divider"></div>
          <div>
            <div class="nav-brand-text">
              <span class="lotus">Lotus</span>
              <span class="amp">&</span>
              <span class="fair">Fairways</span>
            </div>
            <div class="nav-tagline">Southeast Asia · Luxury Travel & Golf</div>
          </div>
        </a>
      </div>
      <ul class="nav-links" id="nav-links" role="list">
        <li class="${isDest ? 'active' : ''}"><a href="/destinations/">Destinations</a></li>
        <li class="golf-link ${isGolf ? 'active' : ''}"><a href="/golf-in-asia/">Golf in Asia</a></li>
        <li class="beyond-link ${isBeyond ? 'active' : ''}"><a href="/beyond/">Beyond Asia</a></li>
        <li><a href="/journal/">Journal</a></li>
        <li class="enquire-link"><a href="/contact/">Enquire</a></li>
      </ul>
      <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="nav-links" aria-label="Toggle navigation">
        <span></span><span></span><span></span>
      </button>
    </nav>`;

  // Insert nav
  document.body.insertAdjacentHTML('afterbegin', navHTML);

  // Scroll behaviour — transparent on hero pages, solid otherwise
  const nav = document.getElementById('main-nav');
  const hasHero = document.querySelector('.hero, .dest-hero');

  function updateNav() {
    if (hasHero) {
      if (window.scrollY > 60) {
        nav.classList.remove('transparent');
        nav.classList.add('scrolled');
        // Switch to light mark
        const markEl = nav.querySelector('svg');
        if (markEl) markEl.outerHTML = markLight(38);
      } else {
        nav.classList.add('transparent');
        nav.classList.remove('scrolled');
        // Switch to dark mark for transparent bg
        const markEl = nav.querySelector('svg');
        if (markEl) markEl.outerHTML = markDark(38);
      }
    } else {
      nav.classList.remove('transparent');
      nav.classList.add('scrolled');
    }
  }

  if (hasHero) {
    nav.classList.add('transparent');
    // Set dark mark initially
    const markEl = nav.querySelector('svg');
    if (markEl) markEl.outerHTML = markDark(38);
  }

  window.addEventListener('scroll', updateNav, { passive: true });

  // Mobile toggle
  const toggle = document.getElementById('nav-toggle');
  const links  = document.getElementById('nav-links');
  toggle.addEventListener('click', () => {
    const isOpen = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  // Smooth scroll for enquiry CTA
  document.addEventListener('click', e => {
    if (e.target.closest('a[href="#enquiry"]')) {
      e.preventDefault();
      const el = document.getElementById('enquiry');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  });

  // Export mark functions for use in other scripts
  window.LF = window.LF || {};
  window.LF.markLight = markLight;
  window.LF.markDark  = markDark;

})();
