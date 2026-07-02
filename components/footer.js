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
            <h4>Golf & Beyond</h4>
            <ul>
              <li><a href="/golf-in-asia/">Golf in Asia</a></li>
              <li><a href="/golf-in-asia/thailand/">Golf in Thailand</a></li>
              <li><a href="/golf-in-asia/vietnam/">Golf in Vietnam</a></li>
              <li><a href="/whisky-fairways.html">Scotland Golf</a></li>
              <li><a href="/beyond/">Beyond Asia</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Contact</h4>
            <ul>
              <li><a href="tel:+441603340142">01603 340142 · Norfolk</a></li>
              <li><a href="tel:+441625802142">01625 802142 · Cheshire</a></li>
              <li><a href="mailto:hello@lotusfairways.com">hello@lotusfairways.com</a></li>
              <li><a href="/contact/">Enquire Online</a></li>
              <li><a href="/about/">About Us</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© ${new Date().getFullYear()} Lotus &amp; Fairways. ATOL Protected. Registered in England &amp; Wales.</p>
          <p>Norfolk · Cheshire · Southeast Asia · Scotland</p>
        </div>
      </div>
    </footer>`;

  document.body.insertAdjacentHTML('beforeend', footerHTML);

})();
