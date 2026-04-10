#!/usr/bin/env python3
"""
Batch-generate hanyue.io-style product detail pages from BlenderMarket backup data.
Reads raw_data.json + images/ from each product folder, writes index.html alongside.
"""

import json, os, re, html as html_mod, glob

SRC = os.path.dirname(os.path.abspath(__file__))

def slugify(title):
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def escape(text):
    return html_mod.escape(str(text))

def convert_desc_html(raw_html, img_base):
    """Convert description HTML: rewrite image URLs to local paths."""
    if not raw_html:
        return ''
    # Replace remote image URLs with local desc_* files
    def replace_img(m):
        src = m.group(1)
        # Extract the hash portion from the URL
        hash_match = re.search(r'([a-f0-9]{32})\.\w+$', src)
        if hash_match:
            h = hash_match.group(0)
            # Find matching local file
            local = f'{img_base}/desc_*{h}'
            matches = glob.glob(local)
            if matches:
                fname = os.path.basename(matches[0])
                return f'<img src="images/{fname}" alt="" style="max-width:100%;">'
        return m.group(0)

    result = re.sub(r'<img[^>]*src="([^"]*)"[^>]*>', replace_img, raw_html)
    # Strip inline max-width styles on imgs (we handle via CSS)
    result = re.sub(r'style="max-width:100%;?"', '', result)
    return result

def build_gallery_html(images_dir, slug):
    """Build gallery thumbs from available image files."""
    files = sorted(glob.glob(os.path.join(images_dir, '*')))
    cover = None
    gallery = []
    for f in files:
        name = os.path.basename(f)
        if name.startswith('00_cover'):
            cover = name
        elif name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_')) and 'gallery' in name:
            gallery.append(name)
        elif name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_')) and 'desc' not in name:
            gallery.append(name)

    all_imgs = []
    if cover:
        all_imgs.append(cover)
    all_imgs.extend(gallery)

    if not all_imgs:
        # fallback: use any non-desc image
        for f in files:
            name = os.path.basename(f)
            if not name.startswith('desc_'):
                all_imgs.append(name)
        if not all_imgs:
            all_imgs = [os.path.basename(f) for f in files[:1]]

    main_img = all_imgs[0] if all_imgs else ''
    thumbs_html = ''
    for i, img in enumerate(all_imgs):
        active = ' class="active"' if i == 0 else ''
        thumbs_html += f'                <img src="images/{img}" alt=""{active} data-index="{i}">\n'

    return main_img, thumbs_html

def build_page(data, folder_path, images_dir):
    title = data.get('title', 'Product')
    slug = slugify(title)
    price = data.get('price', '$0.00')
    categories = data.get('categories', [])
    tags = data.get('tags', [])
    blender_min = data.get('blenderVersionMin', '')
    blender_max = data.get('blenderVersionMax', '')
    license_type = data.get('license', 'GPL').upper()
    files_list = data.get('files', [])
    file_name = files_list[0]['name'] if files_list else ''
    desc_html = data.get('description', '')
    docs_html = data.get('documentation', '')

    # Convert images in description/docs to local paths
    desc_html = convert_desc_html(desc_html, images_dir)
    docs_html = convert_desc_html(docs_html, images_dir)

    # Gallery
    main_img, thumbs_html = build_gallery_html(images_dir, slug)

    # Categories HTML
    cats_html = ''.join(f'                    <span class="meta-tag">{escape(c)}</span>\n' for c in categories)

    # Tags for compat list (top 10)
    tags_display = tags[:12]
    tags_html = ''.join(f'                    <span class="compat-chip">{escape(t)}</span>\n' for t in tags_display)

    # Blender version string
    ver_str = ''
    if blender_min and blender_max:
        ver_str = f'{blender_min} - {blender_max}'
    elif blender_min:
        ver_str = f'{blender_min}+'
    else:
        ver_str = 'All'

    # Sidebar info items
    sidebar_items = f'''                    <div class="sidebar-info-item">
                        <span class="sidebar-info-label">Blender 版本</span>
                        <span class="sidebar-info-value">{escape(ver_str)}</span>
                    </div>'''
    if file_name:
        sidebar_items += f'''
                    <div class="sidebar-info-item">
                        <span class="sidebar-info-label">文件</span>
                        <span class="sidebar-info-value">{escape(file_name)}</span>
                    </div>'''
    sidebar_items += f'''
                    <div class="sidebar-info-item">
                        <span class="sidebar-info-label">许可协议</span>
                        <span class="sidebar-info-value">{escape(license_type)}</span>
                    </div>'''

    # Docs tab (only show if docs exist)
    docs_tab = ''
    docs_panel = ''
    if docs_html and docs_html.strip():
        docs_tab = '            <button class="desc-tab" data-tab="docs">使用文档</button>'
        docs_panel = f'''        <div class="desc-panel" id="panel-docs">
            <div class="desc-content">
                {docs_html}
            </div>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - SyncTools Pro</title>
    <link rel="icon" href="/favicon.ico">
    <meta name="description" content="{escape(title)} - SyncTools Pro 商品详情">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #050505 100%);
            color: #ffffff; min-height: 100vh;
        }}
        .top-nav {{ position: sticky; top: 0; background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.1); z-index: 1001; padding: 0 20px; height: 60px; display: flex; align-items: center; }}
        .nav-container {{ max-width: 1200px; margin: 0 auto; width: 100%; display: flex; justify-content: space-between; align-items: center; }}
        .nav-left {{ display: flex; align-items: center; gap: 12px; }}
        .nav-left a {{ display: flex; align-items: center; gap: 12px; text-decoration: none; color: inherit; }}
        .logo-icon {{ width: 35px; height: 35px; }}
        .logo-text {{ font-size: 1.5rem; font-weight: 700; color: #fff; letter-spacing: -0.5px; }}
        .nav-right {{ display: flex; align-items: center; gap: 32px; }}
        .nav-link {{ color: #999; text-decoration: none; font-size: 0.9rem; font-weight: 500; letter-spacing: .5px; transition: color .3s; }}
        .nav-link:hover {{ color: #fff; }}
        .nav-login {{ background: #fff; color: #000 !important; padding: 8px 18px; border-radius: 20px; font-weight: 600; }}
        .nav-login:hover {{ background: #f0f0f0; }}
        .breadcrumb {{ max-width: 1200px; margin: 24px auto 0; padding: 0 20px; font-size: 0.85rem; color: #666; }}
        .breadcrumb a {{ color: #888; text-decoration: none; transition: color .2s; }}
        .breadcrumb a:hover {{ color: #fff; }}
        .product {{ max-width: 1200px; margin: 24px auto 0; padding: 0 20px; display: grid; grid-template-columns: 1fr 380px; gap: 48px; }}
        .gallery {{ position: relative; }}
        .gallery-main {{ width: 100%; aspect-ratio: 16/9; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); background: #111; }}
        .gallery-main img {{ width: 100%; height: 100%; object-fit: contain; display: block; transition: opacity .3s; }}
        .gallery-thumbs {{ display: flex; gap: 10px; margin-top: 14px; overflow-x: auto; padding-bottom: 4px; }}
        .gallery-thumbs img {{ width: 90px; height: 56px; object-fit: cover; border-radius: 8px; border: 2px solid transparent; cursor: pointer; opacity: 0.5; transition: all .2s; flex-shrink: 0; }}
        .gallery-thumbs img:hover {{ opacity: 0.8; }}
        .gallery-thumbs img.active {{ border-color: #fff; opacity: 1; }}
        .sidebar {{ position: sticky; top: 84px; align-self: start; }}
        .sidebar-card {{ background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 28px; }}
        .product-title {{ font-size: 1.6rem; font-weight: 800; line-height: 1.3; margin-bottom: 8px; }}
        .product-meta {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
        .meta-tag {{ background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 3px 10px; font-size: 0.75rem; color: #aaa; }}
        .price-row {{ display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .price-now {{ font-size: 2.2rem; font-weight: 900; }}
        .price-license {{ font-size: 0.85rem; color: #888; }}
        .buy-btn {{ display: block; width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 9999px; font-size: 1.05rem; font-weight: 700; cursor: pointer; transition: all .3s; text-align: center; text-decoration: none; }}
        .buy-btn:hover {{ background: #f0f0f0; transform: translateY(-2px); box-shadow: 0 10px 30px rgba(255,255,255,0.15); }}
        .sidebar-info {{ margin-top: 20px; }}
        .sidebar-info-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 0.88rem; }}
        .sidebar-info-label {{ color: #888; }}
        .sidebar-info-value {{ color: #ddd; font-weight: 500; }}
        .compat-list {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }}
        .compat-chip {{ background: rgba(74,222,128,0.1); color: #4ade80; border: 1px solid rgba(74,222,128,0.2); border-radius: 6px; padding: 3px 10px; font-size: 0.78rem; font-weight: 600; }}
        .description {{ max-width: 1200px; margin: 48px auto 0; padding: 0 20px; }}
        .desc-tabs {{ display: flex; gap: 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 32px; }}
        .desc-tab {{ padding: 12px 28px; color: #888; font-weight: 600; font-size: 0.95rem; cursor: pointer; border-bottom: 2px solid transparent; transition: all .2s; background: none; border-top: none; border-left: none; border-right: none; }}
        .desc-tab:hover {{ color: #ccc; }}
        .desc-tab.active {{ color: #fff; border-bottom-color: #fff; }}
        .desc-panel {{ display: none; }}
        .desc-panel.active {{ display: block; }}
        .desc-content {{ max-width: 820px; line-height: 1.8; color: #ccc; }}
        .desc-content h1 {{ font-size: 1.8rem; font-weight: 800; color: #fff; margin: 32px 0 16px; }}
        .desc-content h2 {{ font-size: 1.4rem; font-weight: 700; color: #fff; margin: 28px 0 12px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); }}
        .desc-content h3 {{ font-size: 1.15rem; font-weight: 700; color: #eee; margin: 20px 0 10px; }}
        .desc-content h4 {{ font-size: 1rem; font-weight: 600; color: #ddd; margin: 16px 0 8px; }}
        .desc-content p {{ margin-bottom: 12px; }}
        .desc-content ul, .desc-content ol {{ margin: 8px 0 16px 24px; }}
        .desc-content li {{ margin-bottom: 6px; }}
        .desc-content hr {{ border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 24px 0; }}
        .desc-content img {{ max-width: 100%; border-radius: 12px; margin: 16px 0; border: 1px solid rgba(255,255,255,0.08); }}
        .desc-content blockquote {{ border-left: 3px solid #4ade80; padding: 12px 16px; margin: 16px 0; background: rgba(74,222,128,0.05); border-radius: 0 8px 8px 0; color: #aaa; }}
        .desc-content code {{ background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-size: 0.88rem; color: #ff90e8; }}
        .desc-content pre {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 16px; overflow-x: auto; margin: 12px 0; }}
        .desc-content pre code {{ background: none; padding: 0; color: #ccc; }}
        .desc-content table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
        .desc-content th, .desc-content td {{ padding: 10px 14px; border: 1px solid rgba(255,255,255,0.1); text-align: left; }}
        .desc-content th {{ background: rgba(255,255,255,0.04); color: #fff; font-weight: 600; }}
        .desc-content strong {{ color: #fff; }}
        footer {{ margin-top: 80px; padding: 40px 20px; border-top: 1px solid rgba(255,255,255,0.06); text-align: center; color: #555; font-size: 0.85rem; }}
        footer a {{ color: #666; text-decoration: none; }}
        footer a:hover {{ color: #fff; }}
        @media (max-width: 900px) {{
            .product {{ grid-template-columns: 1fr; gap: 24px; }}
            .sidebar {{ position: static; }}
            .gallery-main {{ aspect-ratio: 4/3; }}
        }}
        @media (max-width: 768px) {{
            .nav-right {{ gap: 16px; }}
            .nav-link {{ font-size: 0.8rem; }}
            .product-title {{ font-size: 1.3rem; }}
            .price-now {{ font-size: 1.8rem; }}
            .desc-tab {{ padding: 10px 16px; font-size: 0.88rem; }}
        }}
        @media (max-width: 480px) {{
            .nav-link:not(.nav-login) {{ display: none; }}
            .gallery-thumbs img {{ width: 70px; height: 44px; }}
        }}
    </style>
</head>
<body>
    <nav class="top-nav">
        <div class="nav-container">
            <div class="nav-left">
                <a href="/">
                    <svg class="logo-icon" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 20 L20 10 L30 20 L20 30 Z" stroke="white" stroke-width="2" fill="none"/>
                        <circle cx="20" cy="20" r="3" fill="white"/>
                    </svg>
                    <span class="logo-text">SyncTools</span>
                </a>
            </div>
            <div class="nav-right">
                <a href="/store.html" class="nav-link">商店</a>
                <a href="/docs.html" class="nav-link">文档</a>
                <a href="/download.html" class="nav-link">下载</a>
                <a href="#login" class="nav-link nav-login">登录</a>
            </div>
        </div>
    </nav>

    <div class="breadcrumb">
        <a href="/">首页</a> &rsaquo; <a href="/store.html">商店</a> &rsaquo; {escape(title)}
    </div>

    <section class="product">
        <div class="gallery">
            <div class="gallery-main">
                <img id="mainImg" src="images/{main_img}" alt="{escape(title)}">
            </div>
            <div class="gallery-thumbs" id="thumbs">
{thumbs_html}            </div>
        </div>
        <aside class="sidebar">
            <div class="sidebar-card">
                <h1 class="product-title">{escape(title)}</h1>
                <div class="product-meta">
{cats_html}                </div>
                <div class="price-row">
                    <span class="price-now">{escape(price)}</span>
                    <span class="price-license">永久授权</span>
                </div>
                <a class="buy-btn" href="/payment.html?product={slug}">立即购买</a>
                <div class="sidebar-info">
{sidebar_items}
                </div>
                <div class="compat-list">
{tags_html}                </div>
            </div>
        </aside>
    </section>

    <section class="description">
        <div class="desc-tabs">
            <button class="desc-tab active" data-tab="desc">产品介绍</button>
{docs_tab}
        </div>
        <div class="desc-panel active" id="panel-desc">
            <div class="desc-content">
                {desc_html}
            </div>
        </div>
{docs_panel}
    </section>

    <footer>
        <p>&copy; 2026 SyncTools Pro. All rights reserved. &nbsp;|&nbsp; <a href="/">首页</a> &nbsp;|&nbsp; <a href="/store.html">商店</a> &nbsp;|&nbsp; <a href="/docs.html">文档</a></p>
    </footer>

    <script src="/auth-modal.js"></script>
    <script>
        const mainImg = document.getElementById('mainImg');
        const thumbs = document.getElementById('thumbs');
        if (thumbs) thumbs.addEventListener('click', (e) => {{
            const t = e.target.closest('img');
            if (!t) return;
            mainImg.src = t.src;
            thumbs.querySelectorAll('img').forEach(i => i.classList.remove('active'));
            t.classList.add('active');
        }});
        document.querySelectorAll('.desc-tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.desc-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.desc-panel').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
            }});
        }});
    </script>
</body>
</html>'''


def main():
    output_dir = SRC
    count = 0
    errors = []

    for folder_name in sorted(os.listdir(output_dir)):
        folder_path = os.path.join(output_dir, folder_name)
        json_path = os.path.join(folder_path, 'raw_data.json')

        if not os.path.isdir(folder_path) or not os.path.isfile(json_path):
            continue

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            errors.append(f'{folder_name}: JSON error: {e}')
            continue

        images_dir = os.path.join(folder_path, 'images')
        if not os.path.isdir(images_dir):
            errors.append(f'{folder_name}: no images/ directory')
            continue

        html = build_page(data, folder_path, images_dir)
        out_path = os.path.join(folder_path, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)

        count += 1
        print(f'  [{count:02d}] {folder_name}')

    print(f'\nGenerated {count} pages.')
    if errors:
        print(f'\nErrors ({len(errors)}):')
        for e in errors:
            print(f'  - {e}')


if __name__ == '__main__':
    main()
