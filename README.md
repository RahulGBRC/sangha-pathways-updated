# Sanghapathways Tour India — Complete Website

Live website: https://sanghapathways.rahulgbrc.chatgpt.site

## Contents
- dist/: ready-to-host website, all seven pages, CSS, JavaScript, images and logo.
- dist/itineraries/downloads/: five branded itinerary PDFs.
- build_content.py and expanded_pages.py: website content generation scripts.
- build_pdfs.py: itinerary PDF generation script.
- itineraries.json: structured itinerary content.
- .openai/hosting.json: existing Sites project configuration.

## Preview locally
Install Python 3, open a terminal in this folder, and run:

    python -m http.server 8000 --directory dist

Then open http://localhost:8000 in your browser. A local web server is necessary for the root-relative navigation and asset paths to work correctly.

## Host the website
Upload the contents of dist/ to the web root of a static web host. No build is required for the included website. Keep its folder structure intact.

## Optional regeneration
The original generation scripts are included as saved. Before running build_content.py on another computer, change its root setting to Path(__file__).resolve().parent / 'dist'. PDF generation requires reportlab, Pillow and the DejaVu fonts currently referenced under /usr/share/fonts/truetype/dejavu/; adjust the font paths for your computer if necessary. The ready-to-use PDFs are already included.

Git internals, Python cache files and temporary working files are excluded. This archive contains the complete saved website project; the original uploaded Word rough sheets are not part of the website project.
