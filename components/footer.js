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
              <li><a href="tel:+441625802142">01625 802142 · Cheshire</a></li>
              <li><a href="mailto:hello@lotusfairways.com">hello@lotusfairways.com</a></li>
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
