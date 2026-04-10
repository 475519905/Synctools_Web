#!/usr/bin/env python3
"""Build offline product pages with local images and proper formatting.
Generates a self-contained product_page.html for each product directory.
"""

import json
import os
import re
import glob
import base64

BASE_DIR = os.path.expanduser("~/Desktop/BlenderMarket_Backup")


def find_local_image(url, images_dir, desc_images_urls):
    """Map a remote URL to a local image file path."""
    if not url:
        return None

    # Check if it's a description image
    for i, durl in enumerate(desc_images_urls):
        if durl == url:
            # Find matching desc_XX_ file
            pattern = os.path.join(images_dir, f"desc_{i:02d}_*")
            matches = glob.glob(pattern)
            if matches:
                return os.path.basename(matches[0])

    # Check by URL basename
    url_base = os.path.basename(url.split("?")[0])
    for f in os.listdir(images_dir):
        if url_base in f:
            return f

    return None


def replace_img_urls(html, images_dir, desc_images_urls):
    """Replace remote image URLs in HTML with local paths."""
    def replacer(match):
        full_tag = match.group(0)
        src = match.group(1)
        local = find_local_image(src, images_dir, desc_images_urls)
        if local:
            return full_tag.replace(src, f"images/{local}")
        return full_tag

    return re.sub(r'<img\s[^>]*?src="([^"]+)"', replacer, html, flags=re.IGNORECASE)


def build_page(product_dir):
    """Build a complete offline product page for one product."""
    raw_file = os.path.join(product_dir, "raw_data.json")
    if not os.path.exists(raw_file):
        return False

    with open(raw_file, "r") as f:
        raw = json.load(f)

    title = raw.get("title", "Unknown Product")
    price = raw.get("price", "")
    categories = raw.get("categories", [])
    tags = raw.get("tags", [])
    blender_min = raw.get("blenderVersionMin", "")
    blender_max = raw.get("blenderVersionMax", "")
    render_engines = raw.get("renderEngines", [])
    misc_data = raw.get("miscData", [])
    license_type = raw.get("license", "")
    desc_html = raw.get("description", "")
    docs_html = raw.get("documentation", "")
    desc_images_urls = raw.get("descriptionImages", [])

    images_dir = os.path.join(product_dir, "images")
    files_dir = os.path.join(product_dir, "files")

    # Replace remote URLs in description with local paths
    if desc_html:
        desc_html = replace_img_urls(desc_html, images_dir, desc_images_urls)

    # Replace remote URLs in documentation too
    if docs_html:
        docs_html = replace_img_urls(docs_html, images_dir, desc_images_urls)

    # Build gallery HTML
    gallery_html = ""
    gallery_files = sorted([f for f in os.listdir(images_dir) if f.startswith(("00_cover", "01_", "02_", "03_", "04_", "05_", "06_", "07_", "08_", "09_")) and "gallery" in f or f.startswith("00_cover")]) if os.path.isdir(images_dir) else []

    # Get cover and gallery separately
    cover_files = sorted([f for f in os.listdir(images_dir) if f.startswith("00_cover")]) if os.path.isdir(images_dir) else []
    gallery_only = sorted([f for f in os.listdir(images_dir) if "gallery" in f]) if os.path.isdir(images_dir) else []

    if cover_files:
        gallery_html += f'<div class="cover-image"><img src="images/{cover_files[0]}" alt="Cover"></div>\n'

    if gallery_only:
        gallery_html += '<div class="gallery">\n'
        for gf in gallery_only:
            gallery_html += f'  <div class="gallery-item"><img src="images/{gf}" alt="Gallery"></div>\n'
        gallery_html += '</div>\n'

    # Build files list HTML
    files_html = ""
    if os.path.isdir(files_dir):
        file_list = sorted(os.listdir(files_dir))
        if file_list:
            files_html = '<ul class="file-list">\n'
            for fl in file_list:
                size = os.path.getsize(os.path.join(files_dir, fl))
                if size < 1024:
                    sz = f"{size} B"
                elif size < 1048576:
                    sz = f"{size/1024:.1f} KB"
                else:
                    sz = f"{size/1048576:.1f} MB"
                files_html += f'  <li><a href="files/{fl}">{fl}</a> <span class="file-size">({sz})</span></li>\n'
            files_html += '</ul>\n'

    # Build categories/meta info HTML
    meta_html = '<div class="meta-grid">\n'
    if categories:
        meta_html += f'  <div class="meta-item"><span class="meta-label">Categories</span><span class="meta-value">{", ".join(categories)}</span></div>\n'
    if blender_min or blender_max:
        ver = f"{blender_min}" + (f" ~ {blender_max}" if blender_max else "")
        meta_html += f'  <div class="meta-item"><span class="meta-label">Blender Version</span><span class="meta-value">{ver}</span></div>\n'
    if license_type:
        meta_html += f'  <div class="meta-item"><span class="meta-label">License</span><span class="meta-value">{license_type.upper()}</span></div>\n'
    if price:
        meta_html += f'  <div class="meta-item"><span class="meta-label">Price</span><span class="meta-value">{price}</span></div>\n'
    if render_engines:
        meta_html += f'  <div class="meta-item"><span class="meta-label">Render Engines</span><span class="meta-value">{", ".join(render_engines)}</span></div>\n'
    if misc_data:
        meta_html += f'  <div class="meta-item"><span class="meta-label">Features</span><span class="meta-value">{", ".join(misc_data)}</span></div>\n'
    meta_html += '</div>\n'

    # Tags
    tags_html = ""
    if tags:
        tags_html = '<div class="tags">\n'
        for t in tags:
            tags_html += f'  <span class="tag">{t}</span>\n'
        tags_html += '</div>\n'

    # Full page
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; line-height: 1.6; }}
.container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
header {{ border-bottom: 1px solid #30363d; padding-bottom: 20px; margin-bottom: 30px; }}
header h1 {{ font-size: 2em; color: #f0f6fc; margin-bottom: 8px; }}
header .price {{ font-size: 1.4em; color: #58a6ff; font-weight: 600; }}

.section {{ margin-bottom: 40px; }}
.section-title {{ font-size: 1.3em; color: #f0f6fc; border-bottom: 1px solid #30363d; padding-bottom: 8px; margin-bottom: 16px; }}

.cover-image {{ margin-bottom: 20px; text-align: center; }}
.cover-image img {{ max-width: 100%; border-radius: 8px; border: 1px solid #30363d; }}

.gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; margin-bottom: 20px; }}
.gallery-item img {{ width: 100%; border-radius: 6px; border: 1px solid #30363d; cursor: pointer; transition: transform 0.2s; }}
.gallery-item img:hover {{ transform: scale(1.02); }}

.meta-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }}
.meta-item {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px; }}
.meta-label {{ display: block; font-size: 0.8em; color: #8b949e; text-transform: uppercase; margin-bottom: 4px; }}
.meta-value {{ color: #f0f6fc; font-weight: 500; }}

.tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }}
.tag {{ background: #1f6feb22; color: #58a6ff; border: 1px solid #1f6feb44; border-radius: 20px; padding: 4px 12px; font-size: 0.85em; }}

.description {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }}
.description img {{ max-width: 100%; height: auto; border-radius: 6px; margin: 12px 0; }}
.description h2 {{ color: #f0f6fc; margin-top: 20px; margin-bottom: 10px; }}
.description h3 {{ color: #e6edf3; margin-top: 16px; margin-bottom: 8px; }}
.description p {{ margin-bottom: 10px; }}
.description ul, .description ol {{ margin-left: 20px; margin-bottom: 10px; }}
.description li {{ margin-bottom: 4px; }}
.description hr {{ border: none; border-top: 1px solid #30363d; margin: 20px 0; }}
.description strong {{ color: #f0f6fc; }}
.description a {{ color: #58a6ff; text-decoration: none; }}
.description a:hover {{ text-decoration: underline; }}

.documentation {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }}
.documentation p {{ margin-bottom: 8px; }}
.documentation img {{ max-width: 100%; height: auto; border-radius: 6px; margin: 12px 0; }}

.file-list {{ list-style: none; }}
.file-list li {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 10px 16px; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between; }}
.file-list a {{ color: #58a6ff; text-decoration: none; font-weight: 500; }}
.file-list a:hover {{ text-decoration: underline; }}
.file-size {{ color: #8b949e; font-size: 0.85em; }}

footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.85em; text-align: center; }}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>{title}</h1>
  {f'<span class="price">{price}</span>' if price else ''}
</header>

<div class="section">
  <h2 class="section-title">Gallery</h2>
  {gallery_html if gallery_html else '<p style="color:#8b949e;">No images available.</p>'}
</div>

<div class="section">
  <h2 class="section-title">Product Info</h2>
  {meta_html}
  {tags_html}
</div>

<div class="section">
  <h2 class="section-title">Description</h2>
  <div class="description">
    {desc_html if desc_html else '<p style="color:#8b949e;">No description available.</p>'}
  </div>
</div>

{f'''<div class="section">
  <h2 class="section-title">Documentation</h2>
  <div class="documentation">
    {docs_html}
  </div>
</div>''' if docs_html else ''}

{f'''<div class="section">
  <h2 class="section-title">Product Files</h2>
  {files_html}
</div>''' if files_html else ''}

<footer>
  Backup from Superhive (Blender Market) Creator Dashboard
</footer>

</div>
</body>
</html>"""

    out = os.path.join(product_dir, "product_page.html")
    with open(out, "w") as f:
        f.write(page)
    return True


def build_index():
    """Build an index page listing all products."""
    dirs = sorted(glob.glob(os.path.join(BASE_DIR, "[0-9][0-9]_*")))
    items = []
    for d in dirs:
        raw_file = os.path.join(d, "raw_data.json")
        if not os.path.exists(raw_file):
            continue
        with open(raw_file) as f:
            raw = json.load(f)
        dirname = os.path.basename(d)
        title = raw.get("title", dirname)
        price = raw.get("price", "")
        cats = ", ".join(raw.get("categories", []))
        cover_files = sorted(glob.glob(os.path.join(d, "images", "00_cover*")))
        cover = f"{dirname}/images/{os.path.basename(cover_files[0])}" if cover_files else ""

        items.append({
            "dir": dirname, "title": title, "price": price,
            "cats": cats, "cover": cover
        })

    cards = ""
    for item in items:
        cover_img = f'<img src="{item["cover"]}" alt="">' if item["cover"] else '<div class="no-cover">No Image</div>'
        cards += f'''
    <a href="{item["dir"]}/product_page.html" class="card">
      <div class="card-img">{cover_img}</div>
      <div class="card-body">
        <h3>{item["title"]}</h3>
        <p class="card-meta">{item["cats"]}</p>
        <span class="card-price">{item["price"]}</span>
      </div>
    </a>'''

    index = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BlenderMarket Products Backup</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
h1 {{ color: #f0f6fc; margin-bottom: 8px; }}
.subtitle {{ color: #8b949e; margin-bottom: 30px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
.card {{ display: block; background: #161b22; border: 1px solid #30363d; border-radius: 8px; overflow: hidden; text-decoration: none; color: inherit; transition: border-color 0.2s, transform 0.2s; }}
.card:hover {{ border-color: #58a6ff; transform: translateY(-2px); }}
.card-img {{ height: 180px; overflow: hidden; background: #0d1117; display: flex; align-items: center; justify-content: center; }}
.card-img img {{ width: 100%; height: 100%; object-fit: cover; }}
.no-cover {{ color: #8b949e; font-size: 0.9em; }}
.card-body {{ padding: 14px; }}
.card-body h3 {{ font-size: 1em; color: #f0f6fc; margin-bottom: 6px; line-height: 1.3; }}
.card-meta {{ font-size: 0.8em; color: #8b949e; margin-bottom: 6px; }}
.card-price {{ color: #58a6ff; font-weight: 600; font-size: 0.95em; }}
footer {{ margin-top: 40px; text-align: center; color: #8b949e; font-size: 0.85em; padding: 20px; border-top: 1px solid #30363d; }}
</style>
</head>
<body>
<div class="container">
  <h1>BlenderMarket Products Backup</h1>
  <p class="subtitle">{len(items)} products archived</p>
  <div class="grid">{cards}
  </div>
  <footer>Backup from Superhive (Blender Market) Creator Dashboard</footer>
</div>
</body>
</html>"""

    with open(os.path.join(BASE_DIR, "index.html"), "w") as f:
        f.write(index)


def main():
    dirs = sorted(glob.glob(os.path.join(BASE_DIR, "[0-9][0-9]_*")))
    print(f"Building offline pages for {len(dirs)} products...")

    for d in dirs:
        name = os.path.basename(d)
        if build_page(d):
            print(f"  Built: {name}/product_page.html")
        else:
            print(f"  SKIP: {name} (no raw_data.json)")

    print("\nBuilding index page...")
    build_index()
    print(f"Done! Open: file://{BASE_DIR}/index.html")


if __name__ == "__main__":
    main()
