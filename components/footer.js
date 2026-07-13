/* components/footer.js — Lotus & Fairways shared footer */

(function() {

  const footerHTML = `
    <footer role="contentinfo">
      <div class="footer-inner">
        <div class="footer-top">
          <div>
            <div class="footer-logo">
              <span class="lotus">Lotus</span>
              <span class="amp">&</span>
              <span class="fair">Fairways</span>
            </div>
            <p class="footer-desc">UK-based luxury travel specialists in Southeast Asia and Scotland. Bespoke holidays to Thailand, Vietnam and Cambodia. Championship golf — Asia and beyond. Norfolk and Cheshire offices.</p>
            <div class="footer-atol">ATOL Protected</div>
          </div>
          <div class="footer-col">
            <h4>Destinations</h4>
            <ul>
              <li><a href="/destinations/thailand/">Thailand</a></li>
              <li><a href="/destinations/vietnam/">Vietnam</a></li>
              <li><a href="/destinations/cambodia/">Cambodia</a></li>
              <li><a href="/destinations/philippines/">Philippines</a></li>
              <li><a href="/destinations/">All Destinations</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Signature Experiences</h4>
            <ul>
              <li><a href="/whisky-and-fairways.html">Whisky & Fairways — Scotland</a></li>
              <li><a href="/the-cham-tour.html">The Cham Tour — Vietnam</a></li>
              <li><a href="/golf-in-asia/">Golf in Asia</a></li>
              <li><a href="/beyond/">Beyond Asia</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Contact</h4>
            <ul>
              <li><a href="tel:+441603340142">01603 340142 · Norfolk</a></li>
              <li><a href="tel:+441625802142">01625 802142 · Cheshire</a></li>
              <li><a href="mailto:hello@lotusfairways.com">hello@lotusfairways.com</a></li>
              <li>
                <a href="https://wa.me/441603340142" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                  WhatsApp
                </a>
              </li>
              <li><a href="/contact/">Enquire Online</a></li>
              <li><a href="/about/">About Us</a></li>
            </ul>
            <p style="font-size:0.72rem;color:#7a6e65;margin-top:12px;line-height:1.5;">UK office hours (GMT/BST).<br>We respond within one working day.</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© ${new Date().getFullYear()} Lotus &amp; Fairways. ATOL Protected. Registered in England &amp; Wales.</p>
          <p>Norfolk · Cheshire · Southeast Asia · Scotland</p>
        </div>
      </div>
    </footer>`;

  document.body.insertAdjacentHTML('beforeend', footerHTML);


  // Ask a Specialist sidebar tab
  const sidebarHTML = `
    <a href="/contact.html" id="ask-specialist-tab" aria-label="Ask a Specialist" style="
      position:fixed;
      right:0;
      top:50%;
      transform:translateY(-50%);
      background:#9b3a5a;
      color:#fff;
      writing-mode:vertical-rl;
      text-orientation:mixed;
      transform:rotate(180deg) translateY(50%);
      padding:20px 12px;
      font-family:'DM Sans',sans-serif;
      font-size:0.68rem;
      font-weight:500;
      letter-spacing:0.1em;
      text-transform:uppercase;
      text-decoration:none;
      border-radius:6px 0 0 6px;
      box-shadow:-2px 0 12px rgba(0,0,0,0.15);
      z-index:999;
      transition:background 0.2s;
    ">Ask a Specialist</a>`;

  document.body.insertAdjacentHTML('beforeend', sidebarHTML);

  document.getElementById('ask-specialist-tab').addEventListener('mouseenter', function() {
    this.style.background = '#7a2a45';
  });
  document.getElementById('ask-specialist-tab').addEventListener('mouseleave', function() {
    this.style.background = '#9b3a5a';
  });

})();
