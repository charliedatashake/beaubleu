import json, html, re

BASE = 'https://beaubleu-paris.com'
data = json.load(open('data.json'))
by = {d['path']: d for d in data}
esc = html.escape

EXCLUDE = {
    '/', '/collections/frontpage', '/pages/render-product-card', '/pages/just-post-purchase',
    '/pages/le-club-beaubleu-login', '/pages/vitruve',
}

def ok(d):
    return d['status'] == 200 and not d['noindex'] and d['path'] not in EXCLUDE

def link(path, label=None):
    d = by[path]
    return (path, label or d['title'])

# Libellés propres pour les pages et collections (les H1 du site sont parfois décalés)
pages_collections = [
    ('/collections/all', 'Toutes les montres'),
    ('/collections/collection-permanente', 'Collection permanente'),
    ('/collections/editions-limitees', 'Éditions limitées'),
    ('/collections/accessoires', 'Accessoires'),
    ('/pages/collection-la-piece', 'Collection La Pièce'),
    ('/pages/collection-seconde-francaise', 'Collection Seconde Française'),
    ('/pages/seconde-francaise-19-24', 'Seconde Française 19.24'),
    ('/pages/seconde-francaise-20-24', 'Seconde Française 20.24'),
    ('/collections/collection-seconde-francaise-2024', 'Collection Seconde Française 2024'),
    ('/pages/collection-ecce-figura', 'Collection Ecce Figura'),
    ('/pages/collection-ecce', 'Collection Ecce'),
    ('/pages/flat-white', 'Collection Flat White'),
    ('/pages/collection-vitruve', 'Collection Vitruve'),
    ('/collections/archives', 'Archives'),
    ('/pages/excaetera', 'Ex.Caetera, label créatif'),
]
maison = [
    ('/pages/histoire', 'Histoire de la Maison'),
    ('/pages/savoir-faire', 'Savoir-faire'),
    ('/pages/concue-et-assemblee-en-france', 'Conçue et assemblée en France'),
    ('/pages/nosboutiques', 'Nos boutiques'),
    ('/pages/club-login', 'Le Club Ambassadeur'),
    ('/pages/actualite', 'Actualités'),
]
services = [
    ('/pages/garanties', 'Les garanties'),
    ('/pages/garantie-36-mois', 'Garantie 36 mois'),
    ('/pages/livraison-et-retours-offerts', 'Livraison offerte'),
    ('/pages/utilisation', 'Utilisation et entretien de votre montre'),
    ('/pages/faq', 'F.A.Q.'),
    ('/pages/detaxe', 'Détaxe'),
    ('/pages/contact', 'Nous contacter'),
    ('/pages/contacter-latelier', "Contacter l'atelier"),
]
for lst in (pages_collections, maison, services):
    for p, _ in lst:
        assert p in by, p
        assert ok(by[p]), p

# Produits groupés par gamme
products = [d for d in data if d['k'] == 'products' and ok(d)]
groups = [
    ('La Pièce', lambda s: s.startswith('la-piece-')),
    ('Seconde Française', lambda s: s.startswith('seconde-francaise-')),
    ('Ecce Figura', lambda s: s.startswith('ecce-figura-')),
    ('Ecce', lambda s: s.startswith('ecce-')),
    ('Flat White', lambda s: s.startswith('flat-white-')),
    ('Vitruve', lambda s: s.startswith('vitruve-')),
    ('B01', lambda s: s.startswith('b01-')),
    ('Union', lambda s: s.startswith('union-')),
]
grouped = {g: [] for g, _ in groups}
others = []
for d in products:
    slug = d['path'].split('/')[-1]
    for g, f in groups:
        if f(slug):
            grouped[g].append(d)
            break
    else:
        others.append(d)
grouped['Bracelets, boucle et Ambassador Plus'] = others

# Magazine
blog_labels = {
    'actualites': 'Actualités',
    'guides': 'Guides',
    'communaute': 'Communauté',
    'carnets-de-bord': 'Carnets de bord',
}
articles = {}
for d in data:
    if d['k'] == 'articles' and ok(d):
        articles.setdefault(d['path'].split('/')[2], []).append(d)

def a(path, label):
    return f'<a href="{BASE}{esc(path)}">{esc(label)}</a>'

def rows(items):
    return '<ul class="sitemap__list">' + ''.join(f'<li>{a(p, l)}</li>' for p, l in items) + '</ul>'

def accordion(title, count, body, title_path=None):
    t = esc(title)
    return f'''<details class="accordion group">
  <summary><span class="accordion__toggle"><span class="accordion__title">{t}<span class="accordion__count">{count}</span></span><span class="animated-plus" aria-hidden="true"></span></span></summary>
  <div class="accordion__content">{body}</div>
</details>'''

def table_rows(items):
    # lignes "pages" : même gabarit que les questions de la FAQ, avec une flèche à la place du plus
    return ''.join(f'<a class="sitemap__row" href="{BASE}{esc(p)}"><span>{esc(l)}</span><span class="sitemap__arrow" aria-hidden="true"></span></a>' for p, l in items)

sections = []
total = 0

# 1. Collections
sections.append(('collections', 'Collections', table_rows(pages_collections), len(pages_collections)))
total += len(pages_collections)

# 2. Montres
body = ''
n_prod = 0
for g, items in grouped.items():
    if not items:
        continue
    n_prod += len(items)
    lst = rows([(d['path'], d['title']) for d in items])
    body += accordion(g, len(items), lst)
sections.append(('montres', 'Montres et accessoires', body, n_prod))
total += n_prod

# 3. Maison
sections.append(('maison', 'La Maison', table_rows(maison), len(maison)))
total += len(maison)

# 4. Magazine
body = ''
n_art = 0
for slug in ['actualites', 'guides', 'communaute', 'carnets-de-bord']:
    items = articles.get(slug, [])
    n_art += len(items)
    head = f'<p class="sitemap__blog-link">{a("/blogs/" + slug, "Voir tous les articles : " + blog_labels[slug])}</p>'
    lst = rows([(d['path'], d['title']) for d in items])
    body += accordion(blog_labels[slug], len(items), head + lst)
sections.append(('magazine', 'Magazine', body, n_art))
total += n_art

# 5. Services
sections.append(('services', 'Services et informations', table_rows(services), len(services)))
total += len(services)

toc = ''.join(
    f'<a class="faq__toc-item font-w-semibold{" is-active" if i == 0 else ""}" href="#{sid}">{esc(t)}</a>'
    for i, (sid, t, _, _) in enumerate(sections)
)
content = ''
for sid, title, body, n in sections:
    content += f'<p id="{sid}" class="faq__category h3">{esc(title)}<span class="faq__count">{n}</span></p>\n{body}\n'

page = open('template.html').read()
page = page.replace('{{TOC}}', toc).replace('{{CONTENT}}', content).replace('{{TOTAL}}', str(total))
open('index.html', 'w').write(page)
print('total liens', total, {s[0]: s[3] for s in sections})
