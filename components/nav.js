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

  // ── CURRENCY SYSTEM ──────────────────────────────────────────
  // Exchange rates — update these periodically (approx. guidance only)
  const RATES = { GBP: 1, EUR: 1.19, USD: 1.27, SGD: 1.71 };
  const SYMBOLS = { GBP: '£', EUR: '€', USD: '$', SGD: 'S$' };
  let activeCurrency = sessionStorage.getItem('lf_currency') || 'GBP';

  function convertPrice(gbpAmount) {
    return Math.round(gbpAmount * RATES[activeCurrency]);
  }

  function formatPrice(amount, currency) {
    return SYMBOLS[currency] + amount.toLocaleString();
  }

  // Find and update all price elements on page
  function updatePrices() {
    const symbol = SYMBOLS[activeCurrency];
    const rate   = RATES[activeCurrency];
    document.querySelectorAll('.lf-price[data-price-gbp]').forEach(el => {
      const gbp = parseInt(el.getAttribute('data-price-gbp'), 10);
      el.textContent = symbol + Math.round(gbp * rate).toLocaleString();
      let note = el.nextElementSibling;
      if (activeCurrency !== 'GBP') {
        if (!note || !note.classList.contains('lf-approx')) {
          note = document.createElement('span');
          note.className = 'lf-approx';
          note.style.cssText = 'font-size:0.65em;opacity:0.6;margin-left:3px;';
          note.textContent = 'approx.';
          el.insertAdjacentElement('afterend', note);
        }
      } else {
        if (note && note.classList.contains('lf-approx')) note.remove();
      }
    });
  }

  function setCurrency(c) {
    activeCurrency = c;
    sessionStorage.setItem('lf_currency', c);
    updatePrices();
    // Update toggle UI
    document.querySelectorAll('.lf-currency-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.currency === c);
    });
  }

  // Expose globally so pages can call LF.setCurrency()
  window.LF = window.LF || {};
  window.LF.setCurrency  = setCurrency;
  window.LF.activeCurrency = () => activeCurrency;
  window.LF.markLight    = markLight;
  window.LF.markDark     = markDark;

  // ── NAV HTML ─────────────────────────────────────────────────
  const path     = window.location.pathname;
  const isGolf   = path.includes('/golf-in-asia');
  const isHotels = path.startsWith('/hotels');
  const isFairwayTours = path.includes('/fairway-tours');
  const isFW     = path.includes('/fairway-weekends');
  const isBeyond = path.includes('/beyond');
  const isDest   = path.includes('/destinations');

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
        <li class="${isFairwayTours ? 'active' : ''}"><a href="/fairway-tours/">Fairway Tours</a></li>
        <li class="${isFW ? 'active' : ''}"><a href="/fairway-weekends/">Fairway Weekends</a></li>
        <li class="beyond-link ${isBeyond ? 'active' : ''}"><a href="/beyond/">Beyond Asia</a></li>
        <li class="${isHotels ? 'active' : ''}"><a href="/hotels/">The Houses</a></li>
        <li><a href="/journal/">Journal</a></li>
        <li class="nav-currency" aria-label="Select currency">
          <button class="lf-currency-btn ${activeCurrency==='GBP'?'active':''}" data-currency="GBP">£</button>
          <span class="nav-currency-sep">·</span>
          <button class="lf-currency-btn ${activeCurrency==='EUR'?'active':''}" data-currency="EUR">€</button>
          <span class="nav-currency-sep">·</span>
          <button class="lf-currency-btn ${activeCurrency==='USD'?'active':''}" data-currency="USD">$</button>
          <span class="nav-currency-sep">·</span>
          <button class="lf-currency-btn ${activeCurrency==='SGD'?'active':''}" data-currency="SGD">S$</button>
        </li>
        <li class="enquire-link"><a href="/contact/">Enquire</a></li>
      </ul>
      <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="nav-links" aria-label="Toggle navigation">
        <span></span><span></span><span></span>
      </button>
    </nav>`;

  document.body.insertAdjacentHTML('afterbegin', navHTML);

  // Currency button click handlers
  document.querySelectorAll('.lf-currency-btn').forEach(btn => {
    btn.addEventListener('click', () => setCurrency(btn.dataset.currency));
  });

  // ── SCROLL BEHAVIOUR ─────────────────────────────────────────
  const nav    = document.getElementById('main-nav');
  const hasHero = document.querySelector('.hero, .dest-hero, .signature-hero');

  function updateNav() {
    if (hasHero) {
      if (window.scrollY > 60) {
        nav.classList.remove('transparent');
        nav.classList.add('scrolled');
        const markEl = nav.querySelector('svg');
        if (markEl) markEl.outerHTML = markLight(38);
      } else {
        nav.classList.add('transparent');
        nav.classList.remove('scrolled');
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
    const markEl = nav.querySelector('svg');
    if (markEl) markEl.outerHTML = markDark(38);
  }

  window.addEventListener('scroll', updateNav, { passive: true });

  // ── MOBILE TOGGLE ────────────────────────────────────────────
  const toggle = document.getElementById('nav-toggle');
  const links  = document.getElementById('nav-links');
  toggle.addEventListener('click', () => {
    const isOpen = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  // ── SMOOTH SCROLL ────────────────────────────────────────────
  document.addEventListener('click', e => {
    if (e.target.closest('a[href="#enquiry"]')) {
      e.preventDefault();
      const el = document.getElementById('enquiry');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  });

  // Run price update after DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updatePrices);
  } else {
    updatePrices();
  }

})();
