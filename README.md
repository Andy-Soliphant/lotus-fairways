# Lotus & Fairways — Website

Luxury Southeast Asia travel & golf specialists.

## Tech Stack
- Pure HTML / CSS / Vanilla JS
- Deployed via Netlify (GitHub auto-deploy)
- Forms handled by Netlify Forms

## Structure
```
lotus-fairways/
├── index.html                    # Homepage
├── css/
│   └── style.css                 # Complete design system
├── js/
│   └── main.js                   # FAQ, slideshow, forms
├── components/
│   ├── nav.js                    # Shared navigation (injected on every page)
│   └── footer.js                 # Shared footer (injected on every page)
├── images/
│   └── favicon.svg               # Brand mark favicon
├── destinations/
│   ├── index.html                # Destinations hub
│   ├── thailand/index.html       # Thailand page
│   ├── vietnam/index.html        # Vietnam page
│   ├── cambodia/index.html       # Cambodia page
│   └── philippines/index.html   # Philippines page
├── golf-in-asia/
│   ├── index.html                # Golf hub
│   ├── thailand/index.html       # Golf Thailand
│   └── vietnam/index.html        # Golf Vietnam
├── beyond/
│   ├── index.html                # Beyond Asia hub
│   ├── scotland/index.html       # Scotland Golf (Pascal's guide)
│   └── south-america/index.html  # South America
├── about/index.html              # About Us
├── contact/index.html            # Contact & Enquiry
├── journal/index.html            # Blog index
└── netlify.toml                  # Netlify config
```

## How to Edit
1. Open GitHub Desktop
2. Make changes to any file
3. Commit with a brief note ("Update Thailand page")
4. Push to main — Netlify deploys automatically

## Shared Components
Nav and footer are injected by JavaScript — edit once, updates everywhere:
- `components/nav.js` — navigation
- `components/footer.js` — footer

## Forms
Enquiry form uses Netlify Forms. Submissions appear in the Netlify dashboard
and are emailed to hello@lotusfairways.com.

## Colours (CSS variables)
```
--rose:        #9b3a5a   (Lotus Rose)
--rose-light:  #c4607a
--green:       #2a4a2e   (Fairway Green)
--green-light: #3a6040
--bronze:      #8b6a3a
--bronze-light:#c49a5e   (Gold)
--deep:        #1a1208   (Deep Ink)
--parchment:   #f7f3ec
```

## Brand Notes
- Mark: Yin yang in rose/green with bronze ring
- L (green) in rose half · F (rose) in green half
- Typography: Cormorant Garamond (headings) · DM Sans (body)
- Gradient stripe: Rose → Gold → Green (signature brand element)
