"""Build a Journal article on the exact shell of journal/reading-a-bensley-hotel.html.
Head (fonts, style.css, GA, Crisp, nav/footer includes) is copied from the live page so
every article stays identical in structure. Only title/meta/OG, extra CSS and body change."""
import html, re

SHELL = "journal/reading-a-bensley-hotel.html"
EXTRA_CSS_BASE = """
    /* ---- shared article extras (versus / history pieces) ---- */
    .short-answer { background:var(--parchment); border-top:2px solid var(--bronze); padding:var(--space-xl); margin:var(--space-2xl) 0; }
    .short-answer .eyebrow { color:var(--bronze); margin-bottom:var(--space-sm); }
    .short-answer p { margin-bottom:var(--space-sm) !important; font-size:1rem !important; color:var(--deep) !important; }
    .compare-wrap { overflow-x:auto; margin:var(--space-xl) 0 var(--space-2xl); }
    .compare { width:100%; border-collapse:collapse; min-width:520px; font-family:var(--font-sans); font-size:0.9rem; }
    .compare th, .compare td { text-align:left; vertical-align:top; padding:12px 14px; border-bottom:1px solid var(--rule); line-height:1.55; color:var(--slate); }
    .compare thead th { font-family:var(--font-serif); font-size:1.1rem; font-weight:400; color:var(--deep); border-bottom:2px solid var(--bronze); }
    .compare tbody th { font-weight:500; color:var(--deep); width:22%; font-size:0.78rem; letter-spacing:0.06em; text-transform:uppercase; }
    @media(max-width:560px){
      .compare { min-width:0; }
      .compare thead { display:none; }
      .compare, .compare tbody, .compare tr, .compare th, .compare td { display:block; width:auto; }
      .compare tr { border-bottom:1px solid var(--rule); padding:var(--space-md) 0; }
      .compare tbody th, .compare td { border:0; padding:4px 0; width:auto; }
      .compare td[data-h]::before { content:attr(data-h); display:block; font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--bronze); margin-top:6px; }
    }
    .verdict-card { border-left:2px solid var(--bronze); padding:var(--space-sm) 0 var(--space-sm) var(--space-lg); margin:var(--space-lg) 0 var(--space-xl); }
    .verdict-card .who { font-family:var(--font-sans); font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--bronze); margin-bottom:6px; }
    .verdict-card blockquote { font-family:var(--font-serif); font-style:italic; font-size:1.2rem; line-height:1.6; color:var(--deep); margin:0; }
    .facts { background:var(--parchment); padding:var(--space-xl); margin:var(--space-2xl) 0; }
    .facts h3 { font-size:1.2rem; margin-bottom:var(--space-md); }
    .facts dl { display:grid; grid-template-columns:max-content 1fr; gap:8px 20px; font-size:0.92rem; }
    .facts dt { font-weight:500; color:var(--deep); }
    .facts dd { margin:0; color:var(--slate); line-height:1.6; }
    @media(max-width:560px){ .facts dl { grid-template-columns:1fr; } .facts dd { margin-bottom:8px; } }
    .journal-body a:not(.btn) { color:inherit; border-bottom:1px solid var(--bronze-light); }
    .journal-body a:not(.btn):hover { color:var(--rose); border-bottom-color:var(--rose); }
"""


def build(out_path, *, title, description, slug, og_title, og_desc, og_image,
          hero_img, hero_alt, eyebrow, h1, meta_line, body, footer_note,
          footer_href, footer_label, schema_json=""):
    src = open(SHELL, encoding="utf-8").read()
    head, _, _ = src.partition("<body>")
    url = "https://lotusfairways.com/journal/%s" % slug
    head = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*', r"\g<1>" + description.replace("\\", ""), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', r"\g<1>" + url, head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>" + og_title, head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\g<1>" + og_desc, head)
    head = re.sub(r'(<meta property="og:image" content=")[^"]*', r"\g<1>https://lotusfairways.com" + og_image, head)
    if 'og:url' not in head:
        head = head.replace('<meta property="og:type" content="article">',
                            '<meta property="og:type" content="article">\n  <meta property="og:url" content="%s">' % url)
    head = head.replace("  </style>", EXTRA_CSS_BASE + "  </style>", 1)
    if schema_json:
        head = head.replace("</head>", '  <script type="application/ld+json">%s</script>\n</head>' % schema_json)

    page = head + """<body>
<script src="/components/nav.js?v=2"></script>

<section class="journal-hero">
  <img src="%s" alt="%s">
  <div class="journal-hero-content">
    <div class="eyebrow">%s</div>
    <h1>%s</h1>
    <p class="meta">%s</p>
  </div>
</section>

<article class="journal-body">
%s

  <div class="journal-footer">
    <p>%s</p>
    <a href="%s" class="btn btn-rose">%s</a>
  </div>
</article>

<section class="more-stories">
  <h2>More from the Journal</h2>
  <p>Thirty years of travel across Southeast Asia. There are more stories to tell.</p>
  <a href="/journal/" class="btn btn-outline-green">Browse the Journal →</a>
</section>

<script src="/components/footer.js?v=2"></script>
<script src="/js/main.js"></script>
</body>
</html>
""" % (hero_img, hero_alt, eyebrow, h1, meta_line, body, footer_note, footer_href, footer_label)
    open(out_path, "w", encoding="utf-8").write(page)
    return page
