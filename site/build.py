#!/usr/bin/env python3
"""Static site generator for Nidhi Homes Furniture.

Reads src/data/*.json + assets/ and renders dist/:
  index.html, categories/<slug>/, products/<id>/, about/, contact/,
  sitemap.xml, robots.txt, llms.txt
Images live in ../../images/ (collected separately) and are copied into dist/images/.
"""
import json, os, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "data")
IMG_SRC = os.path.abspath(os.path.join(ROOT, "..", "images"))
DIST = os.path.join(ROOT, "dist")

def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return json.load(f)

SITE = load("site.json")
CATS = load("categories.json")
PRODUCTS = load("products.json")
DOMAIN = SITE["domain"].rstrip("/")
WA = SITE["whatsapp"]
PHONE = SITE["phone_display"]

CAT_BY_SLUG = {c["slug"]: c for c in CATS}
PRODS_BY_CAT = {}
for p in PRODUCTS:
    PRODS_BY_CAT.setdefault(p["category"], []).append(p)

def esc(s):
    return html.escape(str(s), quote=True)

def img_for(p, idx):
    return f"/images/{p['category']}/{p['category']}-{idx:02d}.webp"

def wa_link(text):
    import urllib.parse
    return f"https://wa.me/{WA}?text=" + urllib.parse.quote(text)

def head(title, desc, path, og_img="/images/hero/hero.webp", extra=""):
    canon = DOMAIN + path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}{og_img}">
<meta name="robots" content="index, follow">
<link rel="icon" href="/assets/brand/logo-official.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra}
</head>
<body>
"""

HEADER = f"""
<div class="topstrip"><div class="wrap">
<span>📍 {esc(SITE['address'])} &nbsp;•&nbsp; Mon–Sat 9 AM – 6 PM</span>
<span>Call / WhatsApp: <a href="tel:+91{PHONE}">+91 {PHONE}</a> &nbsp;•&nbsp; <b>★ {SITE['rating']} rated on Google</b></span>
</div></div>
<header class="site"><div class="wrap header-in">
<a class="logo" href="/"><img src="/assets/brand/logo-official.png" alt="Nidhi Homes Furniture logo"></a>
<nav class="main">
<a href="/">Home</a>
<a href="/categories/beds/">Beds</a>
<a href="/categories/sofas/">Sofas</a>
<a href="/categories/modular-kitchens/">Modular Kitchen</a>
<a href="/categories/almirahs-wardrobes/">Almirahs</a>
<a href="/categories/mandirs/">Mandirs</a>
<a href="/about/">About</a>
<a href="/contact/">Contact</a>
</nav>
<div class="header-cta">
<a class="btn btn-ghost btn-sm" href="tel:+91{PHONE}">📞 Call</a>
<a class="btn btn-peach btn-sm" href="{wa_link('Hello Nidhi Homes Furniture! I want to enquire about furniture.')}">WhatsApp</a>
</div>
</div></header>
"""

FOOTER = f"""
<footer><div class="wrap">
<div class="cols">
<div>
<h4>Nidhi Homes Furniture</h4>
<p>{esc(SITE['short_about'])}</p>
<p style="margin-top:12px">★ {SITE['rating']} on Google ({SITE['reviews_count']} reviews)</p>
</div>
<div>
<h4>Categories</h4>
{''.join(f'<a href="/categories/{c["slug"]}/">{esc(c["name"])}</a>' for c in CATS)}
</div>
<div>
<h4>Quick Links</h4>
<a href="/">Home</a>
<a href="/about/">About Us</a>
<a href="/contact/">Contact &amp; Enquiry</a>
<a href="{esc(SITE['maps_url'])}" target="_blank" rel="noopener">Find Us on Google Maps</a>
<a href="{esc(SITE['instagram'])}" target="_blank" rel="noopener">Instagram</a>
</div>
<div>
<h4>Visit Our Showroom</h4>
<p>{esc(SITE['address'])}</p>
<p>Phone / WhatsApp: <a href="tel:+91{PHONE}" style="display:inline">+91 {PHONE}</a></p>
<p>Hours: {esc(SITE['hours'])}</p>
</div>
</div>
<div class="bottom"><span>© 2026 Nidhi Homes Furniture, Arsena, Agra. All rights reserved.</span><span>Stylish Homes, Happy Lives</span></div>
</div></footer>
<a class="wa-float" href="{wa_link('Hello Nidhi Homes Furniture! I want to enquire about furniture.')}">💬 WhatsApp Us</a>
<script>
function sendEnquiry(e){{
  e.preventDefault();
  var f=e.target;
  var msg="Hello Nidhi Homes Furniture!%0A%0AName: "+encodeURIComponent(f.name.value)+"%0APhone: "+encodeURIComponent(f.phone.value)+"%0AInterested in: "+encodeURIComponent(f.category.value)+"%0AMessage: "+encodeURIComponent(f.message.value);
  window.open("https://wa.me/{WA}?text="+msg,"_blank");
  return false;
}}
</script>
</body>
</html>
"""

def enquiry_form(select_id="cat"):
    opts = "".join(f'<option value="{esc(c["name"])}">{esc(c["name"])}</option>' for c in CATS)
    return f"""
<form class="card" onsubmit="return sendEnquiry(event)">
<label for="fname">Your Name</label>
<input id="fname" name="name" type="text" placeholder="e.g. Rahul Sharma" required>
<label for="fphone">Phone Number</label>
<input id="fphone" name="phone" type="tel" placeholder="e.g. 98765 43210" required>
<label for="fcat">I am interested in</label>
<select id="fcat" name="category">{opts}<option value="Full Home Furniture">Full Home Furniture</option><option value="Other">Other</option></select>
<label for="fmsg">Your Message</label>
<textarea id="fmsg" name="message" rows="4" placeholder="e.g. I need a king-size bed with storage for my bedroom..."></textarea>
<button class="btn btn-peach" type="submit">Send Enquiry on WhatsApp →</button>
<p style="font-size:13px;color:#6E6258;margin-top:10px;text-align:center">Your enquiry opens in WhatsApp — no details are stored on this website.</p>
</form>
"""

def prod_card(p, idx):
    cat = CAT_BY_SLUG[p["category"]]
    return f"""
<article class="prod-card">
<a href="/products/{p['id'].lower()}/"><img src="{img_for(p, idx)}" alt="{esc(p['name'])}" loading="lazy"></a>
<div class="body">
<h3><a href="/products/{p['id'].lower()}/">{esc(p['name'])}</a></h3>
<p class="spec">{esc(p['material'])}</p>
<p class="size">{esc(p['size'])} • {esc(cat['name'])}</p>
<p class="price">Price on Enquiry<small>Best price on WhatsApp</small></p>
<a class="btn btn-peach btn-sm" href="{wa_link('Hello Nidhi Homes Furniture! I want the price of ' + p['name'] + ' (' + p['id'] + ').')}">Enquire on WhatsApp</a>
</div>
</article>
"""

def cat_card(c):
    first = PRODS_BY_CAT[c["slug"]][0]
    n = len(PRODS_BY_CAT[c["slug"]])
    return f"""
<article class="cat-card">
<a href="/categories/{c['slug']}/"><img src="{img_for(first, 1)}" alt="{esc(c['name'])}" loading="lazy"></a>
<div class="body">
<h3>{esc(c['name'])}</h3>
<p>{esc(c['description'])}</p>
<span class="count">{n} designs →</span>
</div>
</article>
"""

# ---------------- Home ----------------
def build_home():
    best = []
    for c in CATS:
        best.append((PRODS_BY_CAT[c["slug"]][0], 1))
    reviews = [
        ("Vishnu Shakya", "Amazing team and good quality stuff, very impressed by the designs they gave me. Nidhi Homes Agra."),
        ("Devesh Shakya", "Very nice furniture, Nidhi Homes Agra."),
        ("Rohit Kumar", "Its furniture is very nice."),
    ]
    rev_html = "".join(
        f'<div class="rev"><div class="stars">★★★★★</div><p>“{esc(t)}”</p><b>{esc(n)}</b><br><small>Google review</small></div>'
        for n, t in reviews)
    faq_ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": "Do you make custom-size furniture?",
             "acceptedAnswer": {"@type": "Answer", "text": "Yes. Most of our furniture is made to order — beds, wardrobes, modular kitchens and TV units can be customised to your room size, wood and finish. Share your measurements on WhatsApp for a quote."}},
            {"@type": "Question", "name": "Do you deliver outside Agra?",
             "acceptedAnswer": {"@type": "Answer", "text": "Yes, we deliver across India. Delivery charges depend on distance and order size — ask on WhatsApp for your city."}},
            {"@type": "Question", "name": "How do I get the price of a product?",
             "acceptedAnswer": {"@type": "Answer", "text": "Tap the WhatsApp button on any product or fill the enquiry form. Share the product name and your requirements, and we will share the best price."}},
            {"@type": "Question", "name": "What are your showroom timings?",
             "acceptedAnswer": {"@type": "Answer", "text": "Monday to Saturday, 9 AM to 6 PM. Sunday closed. Visit by appointment is welcome — call 8076273509."}},
        ],
    }
    store_ld = {
        "@context": "https://schema.org", "@type": "FurnitureStore",
        "name": "Nidhi Homes Furniture",
        "address": {"@type": "PostalAddress", "streetAddress": "Arsena", "addressLocality": "Agra",
                    "addressRegion": "Uttar Pradesh", "postalCode": "282007", "addressCountry": "IN"},
        "telephone": "+91-8076273509",
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "8"},
        "url": DOMAIN + "/", "priceRange": "₹₹",
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], "opens": "09:00", "closes": "18:00"}],
    }
    import json as _j
    extra = ('<script type="application/ld+json">' + _j.dumps(store_ld) + '</script>\n'
             '<script type="application/ld+json">' + _j.dumps(faq_ld) + '</script>')
    body = f"""
<section class="hero">
<img class="bg" src="/images/hero/hero.webp" alt="Beautiful living room with Nidhi Homes furniture">
<div class="shade"></div>
<div class="wrap">
<h1>Beautiful furniture for <em>your dream home</em></h1>
<p class="lede">Custom-made beds, sofas, modular kitchens, almirahs and more — crafted with perfect finishing, made for your house and villas.</p>
<div class="cta-row">
<a class="btn btn-peach" href="{wa_link('Hello Nidhi Homes Furniture! I want to enquire about furniture.')}">Enquire on WhatsApp</a>
<a class="btn btn-ghost" href="/categories/beds/" style="background:rgba(255,255,255,.92)">Explore Categories</a>
</div>
<p class="rating"><b>★★★★★ 5.0</b> rated on Google • 8 reviews • Pan India Delivery</p>
</div>
</section>

<section class="trust"><div class="wrap">
<div>🚚 Free Delivery<span>in Agra &amp; nearby areas</span></div>
<div>🛠️ Custom Sizes<span>made to fit your home</span></div>
<div>🪵 Solid Wood<span>quality you can feel</span></div>
<div>🇮🇳 Pan India Delivery<span>anywhere in India</span></div>
</div></section>

<section><div class="wrap">
<div class="sec-head"><span class="eyebrow">Shop by Category</span><h2>Everything your home needs</h2><p>From the bedroom to the kitchen — every piece made with care.</p></div>
<div class="cat-grid">{''.join(cat_card(c) for c in CATS)}</div>
</div></section>

<section style="background:var(--white)"><div class="wrap">
<div class="sec-head"><span class="eyebrow">Most Loved</span><h2>Our bestsellers</h2><p>Customer favourites from every category.</p></div>
<div class="prod-grid">{''.join(prod_card(p, i) for p, i in best)}</div>
</div></section>

<section><div class="wrap">
<div class="spotlight"><div class="in">
<img src="{img_for(PRODS_BY_CAT['modular-kitchens'][0], 1)}" alt="Modular kitchen by Nidhi Homes Furniture" loading="lazy">
<div class="txt">
<span class="eyebrow" style="background:var(--peach);color:#5B4632">Modular Kitchen</span>
<h2>Your dream kitchen, built for your space</h2>
<p>Tell us your kitchen size and style — we design, build and install a modular kitchen that fits perfectly.</p>
<ul>
<li>Free design consultation</li>
<li>Premium plywood, soft-close fittings</li>
<li>Quartz &amp; granite countertops</li>
<li>Professional installation</li>
</ul>
<a class="btn btn-peach" href="{wa_link('Hello Nidhi Homes Furniture! I want a free quote for a modular kitchen. My kitchen size is: ')}">Get a Free Kitchen Quote →</a>
</div>
</div></div>
</div></section>

<section style="background:var(--white)"><div class="wrap">
<div class="sec-head"><span class="eyebrow">Why Nidhi Homes</span><h2>Why Agra trusts us</h2></div>
<div class="why-grid">
<div class="why"><div class="ico">🪵</div><h3>Solid Wood Quality</h3><p>Sheesham, teak and premium plywood — furniture built to last for years.</p></div>
<div class="why"><div class="ico">📐</div><h3>Fully Customisable</h3><p>Size, wood, colour, finish — every piece made to your exact needs.</p></div>
<div class="why"><div class="ico">🏠</div><h3>Visit &amp; Feel</h3><p>See the furniture in our Arsena showroom before you buy. Touch and feel the quality.</p></div>
<div class="why"><div class="ico">⭐</div><h3>5.0 Google Rating</h3><p>Every single customer review is 5 stars. That is the Nidhi Homes promise.</p></div>
</div>
</div></section>

<section><div class="wrap">
<div class="sec-head"><span class="eyebrow">Visit Us</span><h2>Our showroom</h2><p>Come see the furniture in person — or call us first and we will keep your favourites ready.</p></div>
<div class="showroom"><div class="in">
<div class="map-box"><iframe src="{esc(SITE['maps_embed'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Nidhi Homes Furniture on Google Maps"></iframe></div>
<div class="visit">
<h3>Nidhi Homes Furniture</h3>
<p>📍 {esc(SITE['address'])}</p>
<p>📞 <a href="tel:+91{PHONE}">+91 {PHONE}</a></p>
<p>📸 <a href="{esc(SITE['instagram'])}" target="_blank" rel="noopener">@nidhi_homes_furniture</a></p>
<div class="hours">
<div><span>Monday – Saturday</span><b>9 AM – 6 PM</b></div>
<div><span>Sunday</span><b>Closed</b></div>
</div>
<a class="btn btn-green" href="{esc(SITE['maps_url'])}" target="_blank" rel="noopener">Get Directions →</a>
</div>
</div></div>
</div></section>

<section style="background:var(--white)"><div class="wrap">
<div class="sec-head"><span class="eyebrow">Customer Love</span><h2>What our customers say</h2><p>Real Google reviews — all 5 stars.</p></div>
<div class="rev-grid">{rev_html}</div>
</div></section>

<section class="enquiry"><div class="wrap"><div class="in">
<div>
<span class="eyebrow" style="background:#fff;color:var(--pista-deep)">Enquiry</span>
<h2>Ask us anything — we reply fast on WhatsApp</h2>
<p>Tell us what you need — a bed, a full modular kitchen, or furniture for a whole villa. Share your room size and we will send designs and the best price.</p>
<p style="margin-top:16px"><b>Or call directly:</b> <a href="tel:+91{PHONE}">+91 {PHONE}</a></p>
</div>
{enquiry_form()}
</div></div></section>

<section><div class="wrap">
<div class="sec-head"><span class="eyebrow">Good to Know</span><h2>Frequently asked questions</h2></div>
<div class="faq">
<details><summary>Do you make custom-size furniture?</summary><p>Yes. Most of our furniture is made to order — beds, wardrobes, modular kitchens and TV units can be customised to your room size, wood and finish. Share your measurements on WhatsApp for a quote.</p></details>
<details><summary>Do you deliver outside Agra?</summary><p>Yes, we deliver across India. Delivery charges depend on distance and order size — ask on WhatsApp for your city.</p></details>
<details><summary>How do I get the price of a product?</summary><p>Tap the WhatsApp button on any product or fill the enquiry form. Share the product name and your requirements, and we will share the best price.</p></details>
<details><summary>What are your showroom timings?</summary><p>Monday to Saturday, 9 AM to 6 PM. Sunday closed. Visit by appointment is welcome — call 8076273509.</p></details>
</div>
</div></section>
"""
    page = (head("Nidhi Homes Furniture — Beds, Sofas, Modular Kitchens in Agra | Stylish Homes, Happy Lives",
                 "Nidhi Homes Furniture, Arsena Agra — custom-made beds, sofas, dining tables, almirahs, modular kitchens, TV units and mandirs. 5.0 rated on Google. Pan India delivery. Enquire on WhatsApp.",
                 "/", extra=extra) + HEADER + body + FOOTER)
    return page

# ---------------- Category pages ----------------
def build_category(c):
    prods = PRODS_BY_CAT[c["slug"]]
    cards = "".join(prod_card(p, i + 1) for i, p in enumerate(prods))
    crumbs = f'<div class="wrap crumbs"><a href="/">Home</a> &nbsp;/&nbsp; {esc(c["name"])}</div>'
    body = f"""
{crumbs}
<section><div class="wrap">
<div class="sec-head"><span class="eyebrow">{esc(c['tagline'])}</span><h2>{esc(c['name'])}</h2><p>{esc(c['description'])} {len(prods)} designs to choose from.</p></div>
<div class="prod-grid">{cards}</div>
</div></section>
<section style="background:var(--white)"><div class="wrap" style="text-align:center">
<h2 style="margin-bottom:8px">Need a custom size or design?</h2>
<p style="color:var(--muted);margin-bottom:20px">Every {esc(c['name'].lower())} can be made to your measurements, wood and finish.</p>
<a class="btn btn-peach" href="{wa_link('Hello Nidhi Homes Furniture! I want a custom ' + c['name'].rstrip('s') + '. My requirements: ')}">Ask for a Custom Quote →</a>
</div></div></section>
"""
    page = (head(f"{c['name']} in Agra — Nidhi Homes Furniture",
                 f"{c['description']} {len(prods)} designs. Price on enquiry — WhatsApp for the best price. Nidhi Homes Furniture, Arsena, Agra.",
                 f"/categories/{c['slug']}/", og_img=img_for(prods[0], 1)) + HEADER + body + FOOTER)
    return page

# ---------------- Product pages ----------------
def build_product(p, idx):
    cat = CAT_BY_SLUG[p["category"]]
    others = [q for q in PRODS_BY_CAT[p["category"]] if q["id"] != p["id"]][:4]
    other_cards = "".join(prod_card(q, PRODS_BY_CAT[p["category"]].index(q) + 1) for q in others)
    crumbs = (f'<div class="wrap crumbs"><a href="/">Home</a> &nbsp;/&nbsp; '
              f'<a href="/categories/{cat["slug"]}/">{esc(cat["name"])}</a> &nbsp;/&nbsp; {esc(p["name"])}</div>')
    body = f"""
{crumbs}
<section><div class="wrap">
<div class="detail">
<img class="main" src="{img_for(p, idx)}" alt="{esc(p['name'])}">
<div>
<h1>{esc(p['name'])}</h1>
<p style="color:var(--muted);margin-top:6px">{esc(cat['name'])} • Product ID: {esc(p['id'])}</p>
<div class="spec-list">
<div><span>Material</span><b>{esc(p['material'])}</b></div>
<div><span>Size</span><b>{esc(p['size'])}</b></div>
<div><span>Customisation</span><b>Size, wood &amp; finish</b></div>
<div><span>Delivery</span><b>Agra &amp; Pan India</b></div>
</div>
<div class="note">💰 <b>Price on Enquiry</b> — share your requirements on WhatsApp and we will send the best price with photos of the actual piece.</div>
<div class="cta-row">
<a class="btn btn-peach" href="{wa_link('Hello Nidhi Homes Furniture! I want the price of ' + p['name'] + ' (' + p['id'] + ').')}">Enquire on WhatsApp</a>
<a class="btn btn-ghost" href="tel:+91{PHONE}">📞 Call +91 {PHONE}</a>
</div>
</div>
</div>
</div></section>
<section style="background:var(--white)"><div class="wrap">
<div class="sec-head"><h2>More {esc(cat['name'])}</h2></div>
<div class="prod-grid">{other_cards}</div>
</div></section>
"""
    import json as _j
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"],
          "image": DOMAIN + img_for(p, idx), "description": f"{p['name']} — {p['material']}, {p['size']}. By Nidhi Homes Furniture, Agra.",
          "sku": p["id"], "brand": {"@type": "Brand", "name": "Nidhi Homes Furniture"},
          "offers": {"@type": "Offer", "availability": "https://schema.org/InStock", "priceCurrency": "INR",
                     "url": DOMAIN + f"/products/{p['id'].lower()}/"}}
    extra = '<script type="application/ld+json">' + _j.dumps(ld) + '</script>'
    page = (head(f"{p['name']} — Nidhi Homes Furniture, Agra",
                 f"{p['name']} ({p['material']}, {p['size']}). Price on enquiry. Custom sizes available. Nidhi Homes Furniture, Arsena, Agra.",
                 f"/products/{p['id'].lower()}/", og_img=img_for(p, idx), extra=extra) + HEADER + body + FOOTER)
    return page

# ---------------- About / Contact ----------------
def build_about():
    body = f"""
<section><div class="wrap" style="max-width:820px">
<div class="sec-head"><span class="eyebrow">About Us</span><h2>Natural home design, perfect finishing</h2></div>
<p style="font-size:17px">Nidhi Homes Furniture is a furniture manufacturer in Arsena, Agra. We design and build furniture for homes and villas — beds, sofas, dining tables, almirahs, modular kitchens, TV units and mandirs — with natural materials and a perfect finish.</p>
<p style="margin-top:14px">Every piece is made to order. Tell us your room size, your wood and your finish, and we will build it for you. Our customers rate us <b>5.0 out of 5 on Google</b> — every single review is five stars.</p>
<p style="margin-top:14px">Visit our showroom in Arsena, Agra (Monday–Saturday, 9 AM–6 PM), or enquire on WhatsApp at <a href="tel:+91{PHONE}">+91 {PHONE}</a>. We deliver across India.</p>
</div></section>
<section style="background:var(--white)"><div class="wrap">
<div class="sec-head"><h2>Why Nidhi Homes</h2></div>
<div class="why-grid">
<div class="why"><div class="ico">🪵</div><h3>Solid Wood Quality</h3><p>Sheesham, teak and premium plywood — furniture built to last for years.</p></div>
<div class="why"><div class="ico">📐</div><h3>Fully Customisable</h3><p>Size, wood, colour, finish — every piece made to your exact needs.</p></div>
<div class="why"><div class="ico">🏠</div><h3>Visit &amp; Feel</h3><p>See the furniture in our Arsena showroom before you buy. Touch and feel the quality.</p></div>
<div class="why"><div class="ico">⭐</div><h3>5.0 Google Rating</h3><p>Every single customer review is 5 stars. That is the Nidhi Homes promise.</p></div>
</div>
</div></section>
"""
    return head("About Us — Nidhi Homes Furniture, Agra",
                "Nidhi Homes Furniture, Arsena Agra — natural home design with perfect finishing furniture. Custom furniture for houses and villas, Pan India delivery.",
                "/about/") + HEADER + body + FOOTER

def build_contact():
    body = f"""
<section><div class="wrap">
<div class="sec-head"><span class="eyebrow">Contact</span><h2>Visit us or send an enquiry</h2></div>
<div class="showroom"><div class="in">
<div class="visit">
<h3>Nidhi Homes Furniture</h3>
<p>📍 {esc(SITE['address'])}</p>
<p>📞 <a href="tel:+91{PHONE}">+91 {PHONE}</a></p>
<p>📸 <a href="{esc(SITE['instagram'])}" target="_blank" rel="noopener">@nidhi_homes_furniture</a></p>
<div class="hours">
<div><span>Monday – Saturday</span><b>9 AM – 6 PM</b></div>
<div><span>Sunday</span><b>Closed</b></div>
</div>
<a class="btn btn-green" href="{esc(SITE['maps_url'])}" target="_blank" rel="noopener">Get Directions →</a>
</div>
{enquiry_form()}
</div></div>
</div></section>
<section><div class="wrap"><div class="map-box"><iframe src="{esc(SITE['maps_embed'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Nidhi Homes Furniture on Google Maps"></iframe></div></div></section>
"""
    return head("Contact — Nidhi Homes Furniture, Arsena, Agra",
                "Contact Nidhi Homes Furniture, Arsena, Agra. Call or WhatsApp 8076273509. Open Monday–Saturday 9 AM–6 PM.",
                "/contact/") + HEADER + body + FOOTER

# ---------------- Build ----------------
def write(path, content):
    full = os.path.join(DIST, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    # assets
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    # images
    if os.path.isdir(IMG_SRC):
        shutil.copytree(IMG_SRC, os.path.join(DIST, "images"),
                        ignore=shutil.ignore_patterns("contact-sheets", "manifest.json", "search"))
    # pages
    write("/index.html", build_home())
    for c in CATS:
        write(f"/categories/{c['slug']}/index.html", build_category(c))
    for p in PRODUCTS:
        idx = PRODS_BY_CAT[p["category"]].index(p) + 1
        write(f"/products/{p['id'].lower()}/index.html", build_product(p, idx))
    write("/about/index.html", build_about())
    write("/contact/index.html", build_contact())
    # sitemap
    urls = ["/", "/about/", "/contact/"]
    urls += [f"/categories/{c['slug']}/" for c in CATS]
    urls += [f"/products/{p['id'].lower()}/" for p in PRODUCTS]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{DOMAIN}{u}</loc></url>")
    sm.append("</urlset>")
    write("/sitemap.xml", "\n".join(sm))
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    write("/llms.txt", f"""# Nidhi Homes Furniture

> {SITE['short_about']}

## Key pages
- Home: {DOMAIN}/
- Categories: {DOMAIN}/categories/beds/ | {DOMAIN}/categories/sofas/ | {DOMAIN}/categories/modular-kitchens/ | {DOMAIN}/categories/almirahs-wardrobes/ | {DOMAIN}/categories/dining-tables/ | {DOMAIN}/categories/kitchen-cabinets/ | {DOMAIN}/categories/tv-units/ | {DOMAIN}/categories/mandirs/
- Contact & enquiry: {DOMAIN}/contact/

## Contact
- Phone / WhatsApp: +91 {PHONE}
- Address: {SITE['address']}
- Hours: {SITE['hours']}
- Instagram: {SITE['instagram']}
- Google rating: {SITE['rating']} ({SITE['reviews_count']} reviews)
""")
    # 404
    write("/404.html", head("Page Not Found — Nidhi Homes Furniture", "This page does not exist.", "/404.html")
          + HEADER + '<section><div class="wrap" style="text-align:center"><h2>Page not found</h2><p style="color:var(--muted)">This page may have moved. <a href="/">Go to the home page →</a></p></div></section>' + FOOTER)
    n_pages = 3 + len(CATS) + len(PRODUCTS) + 1
    print(f"Built {n_pages} pages + sitemap ({len(urls)} URLs) into {DIST}")

if __name__ == "__main__":
    main()
