# Beaubleu Paris, livrables SEO / GEO

- **llms.txt** : fichier à déposer à la racine du site (`https://beaubleu-paris.com/llms.txt`) pour présenter la Maison et ses pages clés aux moteurs IA. Aperçu navigateur : [index.html](https://charliedatashake.github.io/beaubleu/)
- **sitemap-html/** : plan du site HTML. Aperçu : [sitemap-html/](https://charliedatashake.github.io/beaubleu/sitemap-html/)
  - `index.html` : page générée, prête à intégrer
  - `template.html` : gabarit de la page
  - `data.json` : inventaire des URLs du site (statut, noindex, titre)
  - `build.py` : script qui génère `index.html` à partir du gabarit et des données (`python3 build.py`)
