#!/usr/bin/env python3
from __future__ import annotations

import html as html_mod
import re
import shutil
from pathlib import Path

from lxml import html as lxml_html


TARGET_DIR = Path(__file__).resolve().parent
BACKUP_DIR = TARGET_DIR.parent / "BlenderMarket_Backup"
PRODUCT_GLOB = "[0-9][0-9]_*"


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def html_escape(value: str) -> str:
    return html_mod.escape(str(value), quote=True)


def read_html(path: Path):
    return lxml_html.fromstring(path.read_text(encoding="utf-8"))


def class_xpath(name: str) -> str:
    return f"contains(concat(' ', normalize-space(@class), ' '), ' {name} ')"


def first(nodes):
    return nodes[0] if nodes else None


def inner_html(node) -> str:
    if node is None:
        return ""
    parts = []
    if node.text:
        parts.append(node.text)
    for child in node:
        parts.append(lxml_html.tostring(child, encoding="unicode"))
    return "".join(parts).strip()


def body_without_first_h1(path: Path) -> str:
    if not path.exists():
        return ""
    doc = read_html(path)
    body = first(doc.xpath("//body"))
    if body is None:
        return ""
    parts = []
    skipped_h1 = False
    if body.text and body.text.strip():
        parts.append(body.text)
    for child in body:
        tag = (child.tag or "").lower() if isinstance(child.tag, str) else ""
        if not skipped_h1 and tag == "h1":
            skipped_h1 = True
            continue
        parts.append(lxml_html.tostring(child, encoding="unicode"))
    return "".join(parts).strip()


def split_categories(value: str) -> list[str]:
    value = normalize_text(value)
    if not value:
        return []
    parts = re.split(r"\s*(?:,|，|、|/)\s*", value)
    return [part for part in parts if part]


def slugify(title: str) -> str:
    text = title.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "product"


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def find_cover_image(product_dir: Path) -> str:
    images_dir = product_dir / "images"
    if not images_dir.exists():
        return ""
    cover = sorted(images_dir.glob("00_cover.*"))
    if cover:
        return cover[0].name
    all_images = sorted(path.name for path in images_dir.iterdir() if path.is_file())
    return all_images[0] if all_images else ""


def build_gallery_images(product_dir: Path) -> list[str]:
    images_dir = product_dir / "images"
    if not images_dir.exists():
        return []

    files = sorted(path.name for path in images_dir.iterdir() if path.is_file())
    cover = [name for name in files if name.startswith("00_cover")]
    gallery = [
        name
        for name in files
        if not name.startswith("desc_")
        and not name.startswith("00_cover")
        and (
            "gallery" in name.lower()
            or re.match(r"0[1-9]_", name)
            or re.match(r"[1-9][0-9]_", name)
        )
    ]

    result = []
    if cover:
        result.extend(cover[:1])
    result.extend(gallery)
    if result:
        return result

    return [name for name in files if not name.startswith("desc_")][:1]


def build_file_entries(product_dir: Path) -> list[dict[str, str]]:
    files_dir = product_dir / "files"
    if not files_dir.exists():
        return []
    entries = []
    for path in sorted(files_dir.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file():
            continue
        entries.append(
            {
                "name": path.name,
                "href": f"files/{path.name}",
                "size": format_size(path.stat().st_size),
            }
        )
    return entries


def extract_backup_product(folder_name: str) -> dict:
    product_dir = BACKUP_DIR / folder_name
    product_page = product_dir / "product_page.html"
    description_page = product_dir / "description.html"
    documentation_page = product_dir / "documentation.html"

    doc = read_html(product_page)

    title = normalize_text(doc.xpath("string(//header//h1[1])")) or normalize_text(
        doc.xpath("string(//h1[1])")
    )
    price = normalize_text(
        doc.xpath(f"string(//*[self::span or self::div][{class_xpath('price')}][1])")
    )

    meta_items = []
    categories = []
    for item in doc.xpath(f"//div[{class_xpath('meta-item')}]"):
        label = normalize_text(item.xpath("string(.//span[1])"))
        value = normalize_text(item.xpath("string(.//span[last()])"))
        if label and value:
            meta_items.append((label, value))
            if "分类" in label or "categor" in label.lower():
                categories = split_categories(value)

    tags = [
        normalize_text(tag.text_content())
        for tag in doc.xpath(f"//div[{class_xpath('tags')}]//*[self::span or self::a][{class_xpath('tag')}]")
    ]
    tags = [tag for tag in tags if tag]

    description_node = first(doc.xpath(f"//div[{class_xpath('description')}]"))
    documentation_node = first(doc.xpath(f"//div[{class_xpath('documentation')}]"))
    files_node = first(doc.xpath(f"//ul[{class_xpath('file-list')}]"))

    description_html = inner_html(description_node) or body_without_first_h1(description_page)
    documentation_html = inner_html(documentation_node) or body_without_first_h1(documentation_page)
    file_entries = build_file_entries(TARGET_DIR / folder_name)
    if not file_entries and files_node is not None:
        for anchor in files_node.xpath(".//a[@href]"):
            name = normalize_text(anchor.text_content())
            href = anchor.get("href", "")
            size = normalize_text(anchor.xpath("string(following-sibling::*[1])"))
            if name and href:
                file_entries.append({"name": name, "href": href, "size": size.strip("()")})

    license_value = ""
    for label, value in meta_items:
        if "许可" in label or "授权" in label or "license" in label.lower():
            license_value = value
            break

    if not categories:
        categories = [
            value
            for label, value in meta_items
            if "分类" in label or "categor" in label.lower()
        ]

    return {
        "title": title,
        "price": price,
        "meta_items": meta_items,
        "categories": categories,
        "tags": tags,
        "description_html": description_html,
        "documentation_html": documentation_html,
        "file_entries": file_entries,
        "license_value": license_value,
    }


def build_nav(relative_home: str) -> str:
    return f"""
    <nav class="top-nav">
        <div class="nav-container">
            <div class="nav-left">
                <a href="{relative_home}">
                    <svg class="logo-icon" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 20 L20 10 L30 20 L20 30 Z" stroke="white" stroke-width="2" fill="none"/>
                        <circle cx="20" cy="20" r="3" fill="white"/>
                    </svg>
                    <span class="logo-text">SyncTools</span>
                </a>
            </div>
            <div class="nav-right">
                <a href="{relative_home}" class="nav-link">商店</a>
                <a href="#" class="nav-link">文档</a>
                <a href="#" class="nav-link">下载</a>
                <a href="#" class="nav-link nav-login">登录</a>
            </div>
        </div>
    </nav>
""".strip()


def render_file_list(file_entries: list[dict[str, str]]) -> str:
    if not file_entries:
        return '<p class="empty-note">当前备份里没有可下载的产品文件。</p>'
    items = []
    for entry in file_entries:
        items.append(
            f'                <li><a href="{html_escape(entry["href"])}">{html_escape(entry["name"])}</a><span class="file-size">{html_escape(entry["size"])}</span></li>'
        )
    return "\n".join(
        [
            '            <ul class="file-list">',
            *items,
            "            </ul>",
        ]
    )


def render_meta_chips(categories: list[str]) -> str:
    if not categories:
        return '                    <span class="meta-tag">产品备份</span>'
    return "\n".join(
        f'                    <span class="meta-tag">{html_escape(category)}</span>'
        for category in categories
    )


def render_sidebar_items(meta_items: list[tuple[str, str]]) -> str:
    rows = []
    for label, value in meta_items:
        lower_label = label.lower()
        if "价格" in label or "price" in lower_label:
            continue
        rows.append(
            f'                    <div class="sidebar-info-item"><span class="sidebar-info-label">{html_escape(label)}</span><span class="sidebar-info-value">{html_escape(value)}</span></div>'
        )
    return "\n".join(rows)


def render_tags(tags: list[str]) -> str:
    if not tags:
        return '                    <span class="compat-chip">backup</span>'
    return "\n".join(
        f'                    <span class="compat-chip">{html_escape(tag)}</span>'
        for tag in tags
    )


def render_product_index(folder_name: str, backup_data: dict):
    target_product_dir = TARGET_DIR / folder_name
    gallery_images = build_gallery_images(target_product_dir)
    main_image = gallery_images[0] if gallery_images else ""
    thumbs_html = "\n".join(
        (
            f'                <img src="images/{html_escape(image_name)}" alt="{html_escape(backup_data["title"])}"'
            + (' class="active"' if index == 0 else "")
            + f' data-index="{index}">'
        )
        for index, image_name in enumerate(gallery_images)
    )

    docs_html = backup_data["documentation_html"].strip()
    files_html = render_file_list(backup_data["file_entries"])

    tabs = ['            <button class="desc-tab active" data-tab="desc">产品介绍</button>']
    panels = [
        f"""        <div class="desc-panel active" id="panel-desc">
            <div class="desc-content">
                {backup_data["description_html"]}
            </div>
        </div>"""
    ]

    if docs_html:
        tabs.append('            <button class="desc-tab" data-tab="docs">使用文档</button>')
        panels.append(
            f"""        <div class="desc-panel" id="panel-docs">
            <div class="desc-content">
                {docs_html}
            </div>
        </div>"""
        )

    if backup_data["file_entries"]:
        tabs.append('            <button class="desc-tab" data-tab="files">产品文件</button>')
        panels.append(
            f"""        <div class="desc-panel" id="panel-files">
            <div class="desc-content">
{files_html}
            </div>
        </div>"""
        )

    action_href = (
        backup_data["file_entries"][0]["href"]
        if backup_data["file_entries"]
        else "product_page.html"
    )
    action_text = "下载产品文件" if backup_data["file_entries"] else "打开备份页"
    license_text = backup_data["license_value"] or "离线备份"
    main_block = (
        f'<div class="gallery-main"><img id="mainImg" src="images/{html_escape(main_image)}" alt="{html_escape(backup_data["title"])}"></div>'
        if main_image
        else '<div class="gallery-empty">没有可用的预览图</div>'
    )
    thumbs_block = f'<div class="gallery-thumbs" id="thumbs">{thumbs_html}</div>' if thumbs_html else ""

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_escape(backup_data["title"])} - SyncTools Pro</title>
    <meta name="description" content="{html_escape(backup_data["title"])} - 离线产品备份页面">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #050505 100%);
            color: #ffffff;
            min-height: 100vh;
        }}
        .top-nav {{ position: sticky; top: 0; background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255, 255, 255, 0.1); z-index: 1001; padding: 0 20px; height: 60px; display: flex; align-items: center; }}
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
        .gallery-empty {{ display: flex; align-items: center; justify-content: center; min-height: 320px; border: 1px dashed rgba(255,255,255,0.15); border-radius: 16px; color: #666; }}
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
        .sidebar-info-item {{ display: flex; justify-content: space-between; gap: 20px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 0.88rem; }}
        .sidebar-info-label {{ color: #888; flex-shrink: 0; }}
        .sidebar-info-value {{ color: #ddd; font-weight: 500; text-align: right; word-break: break-word; }}
        .compat-list {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }}
        .compat-chip {{ background: rgba(74,222,128,0.1); color: #4ade80; border: 1px solid rgba(74,222,128,0.2); border-radius: 6px; padding: 3px 10px; font-size: 0.78rem; font-weight: 600; }}
        .description {{ max-width: 1200px; margin: 48px auto 0; padding: 0 20px; }}
        .desc-tabs {{ display: flex; gap: 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 32px; overflow-x: auto; }}
        .desc-tab {{ padding: 12px 28px; color: #888; font-weight: 600; font-size: 0.95rem; cursor: pointer; border-bottom: 2px solid transparent; transition: all .2s; background: none; border-top: none; border-left: none; border-right: none; flex-shrink: 0; }}
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
        .file-list {{ list-style: none; }}
        .file-list li {{ background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
        .file-list a {{ color: #fff; text-decoration: none; font-weight: 600; }}
        .file-list a:hover {{ text-decoration: underline; }}
        .file-size {{ color: #888; font-size: 0.85rem; flex-shrink: 0; }}
        .empty-note {{ color: #777; }}
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
            .file-list li {{ flex-direction: column; align-items: flex-start; }}
        }}
    </style>
</head>
<body>
    {build_nav("../index.html")}

    <div class="breadcrumb">
        <a href="../index.html">首页</a> &rsaquo; <a href="../index.html">产品列表</a> &rsaquo; {html_escape(backup_data["title"])}
    </div>

    <section class="product">
        <div class="gallery">
            {main_block}
            {thumbs_block}
        </div>
        <aside class="sidebar">
            <div class="sidebar-card">
                <h1 class="product-title">{html_escape(backup_data["title"])}</h1>
                <div class="product-meta">
{render_meta_chips(backup_data["categories"])}
                </div>
                <div class="price-row">
                    <span class="price-now">{html_escape(backup_data["price"] or "价格未标注")}</span>
                    <span class="price-license">{html_escape(license_text)}</span>
                </div>
                <a class="buy-btn" href="{html_escape(action_href)}">{action_text}</a>
                <div class="sidebar-info">
{render_sidebar_items(backup_data["meta_items"])}
                </div>
                <div class="compat-list">
{render_tags(backup_data["tags"])}
                </div>
            </div>
        </aside>
    </section>

    <section class="description">
        <div class="desc-tabs">
{chr(10).join(tabs)}
        </div>
{chr(10).join(panels)}
    </section>

    <footer>
        <p>&copy; 2026 SyncTools Pro &nbsp;|&nbsp; <a href="../index.html">返回产品列表</a></p>
    </footer>

    <script>
        const mainImg = document.getElementById('mainImg');
        const thumbs = document.getElementById('thumbs');
        if (thumbs && mainImg) {{
            thumbs.addEventListener('click', (event) => {{
                const thumb = event.target.closest('img');
                if (!thumb) return;
                mainImg.src = thumb.src;
                thumbs.querySelectorAll('img').forEach((image) => image.classList.remove('active'));
                thumb.classList.add('active');
            }});
        }}

        document.querySelectorAll('.desc-tab').forEach((tab) => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.desc-tab').forEach((item) => item.classList.remove('active'));
                document.querySelectorAll('.desc-panel').forEach((panel) => panel.classList.remove('active'));
                tab.classList.add('active');
                const panel = document.getElementById('panel-' + tab.dataset.tab);
                if (panel) panel.classList.add('active');
            }});
        }});
    </script>
</body>
</html>
"""

    (target_product_dir / "index.html").write_text(page, encoding="utf-8")


def extract_catalog_cards() -> tuple[str, str, list[dict[str, str]]]:
    doc = read_html(BACKUP_DIR / "index.html")
    title = normalize_text(doc.xpath("string(//h1[1])")) or "BlenderMarket 产品备份"
    subtitle = normalize_text(
        doc.xpath(f"string(//*[self::p or self::div][{class_xpath('subtitle')}][1])")
    )
    cards = []
    for link in doc.xpath(f"//a[{class_xpath('card')}]"):
        href = link.get("href", "")
        folder = href.split("/")[0].strip()
        title_text = normalize_text(link.xpath("string(.//h3[1])"))
        meta_text = normalize_text(
            link.xpath(f"string(.//*[self::p or self::div][{class_xpath('card-meta')}][1])")
        )
        price_text = normalize_text(
            link.xpath(f"string(.//*[self::span or self::div][{class_xpath('card-price')}][1])")
        )
        if folder:
            cards.append(
                {
                    "folder": folder,
                    "title": title_text,
                    "meta": meta_text,
                    "price": price_text,
                }
            )
    return title, subtitle, cards


def render_root_index():
    title, subtitle, cards = extract_catalog_cards()

    card_html = []
    for card in cards:
        cover = find_cover_image(TARGET_DIR / card["folder"])
        img_html = (
            f'<img src="{html_escape(card["folder"])}/images/{html_escape(cover)}" alt="{html_escape(card["title"])}" loading="lazy">'
            if cover
            else '<div class="no-cover">无封面</div>'
        )
        card_html.append(
            f"""            <a class="card" href="{html_escape(card["folder"])}/index.html" data-name="{html_escape(card["title"])}">
                <div class="card-img">{img_html}</div>
                <div class="card-body">
                    <h3>{html_escape(card["title"])}</h3>
                    <p class="card-meta">{html_escape(card["meta"])}</p>
                    <div class="card-bottom">
                        <span class="card-price">{html_escape(card["price"])}</span>
                    </div>
                </div>
            </a>"""
        )

    fallback_subtitle = subtitle or f"共归档 {len(cards)} 个产品"
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_escape(title)}</title>
    <meta name="description" content="{html_escape(fallback_subtitle)}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #050505 100%);
            color: #ffffff;
            min-height: 100vh;
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
        .hero {{ padding: 80px 20px 20px; text-align: center; }}
        .hero h1 {{ font-size: 2.8rem; font-weight: 900; letter-spacing: -1px; }}
        .hero p {{ margin-top: 12px; color: #888; font-size: 1.05rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .filter-bar {{ display: flex; align-items: center; gap: 12px; margin: 30px 0 24px; flex-wrap: wrap; }}
        .filter-input {{
            flex: 1;
            min-width: 220px;
            padding: 10px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
            transition: border-color .2s;
        }}
        .filter-input::placeholder {{ color: #555; }}
        .filter-input:focus {{ border-color: rgba(255,255,255,0.3); }}
        .filter-count {{ color: #666; font-size: 0.85rem; white-space: nowrap; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .card {{
            display: block;
            text-decoration: none;
            color: inherit;
            background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            overflow: hidden;
            transition: all .3s ease;
        }}
        .card:hover {{ transform: translateY(-6px); border-color: rgba(255,255,255,0.2); box-shadow: 0 20px 60px rgba(0,0,0,.5); }}
        .card-img {{ height: 180px; overflow: hidden; background: #0a0a0a; display: flex; align-items: center; justify-content: center; }}
        .card-img img {{ width: 100%; height: 100%; object-fit: cover; transition: transform .4s; }}
        .card:hover .card-img img {{ transform: scale(1.05); }}
        .no-cover {{ color: #666; font-size: 0.9rem; }}
        .card-body {{ padding: 18px; }}
        .card-body h3 {{ font-size: 1rem; font-weight: 700; color: #f0f0f0; margin-bottom: 8px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        .card-meta {{ font-size: 0.78rem; color: #666; margin-bottom: 10px; }}
        .card-bottom {{ display: flex; justify-content: space-between; align-items: center; }}
        .card-price {{ font-size: 1.1rem; font-weight: 800; color: #ffffff; }}
        footer {{ margin-top: 60px; padding: 40px 20px; border-top: 1px solid rgba(255,255,255,0.06); text-align: center; color: #555; font-size: 0.85rem; }}
        @media (max-width: 768px) {{
            .hero {{ padding: 60px 16px 16px; }}
            .hero h1 {{ font-size: 2rem; }}
            .grid {{ grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }}
            .nav-right {{ gap: 16px; }}
            .nav-link {{ font-size: 0.8rem; }}
        }}
        @media (max-width: 480px) {{
            .nav-link:not(.nav-login) {{ display: none; }}
            .grid {{ grid-template-columns: 1fr; }}
            .hero h1 {{ font-size: 1.6rem; }}
        }}
    </style>
</head>
<body>
    {build_nav("index.html")}

    <header class="hero">
        <h1>{html_escape(title)}</h1>
        <p>{html_escape(fallback_subtitle)}</p>
    </header>

    <main class="container">
        <div class="filter-bar">
            <input class="filter-input" type="text" id="search" placeholder="搜索产品名称..." autocomplete="off">
            <span class="filter-count" id="count">显示 {len(cards)} / {len(cards)}</span>
        </div>
        <div class="grid" id="grid">
{chr(10).join(card_html)}
        </div>
    </main>

    <footer>
        <p>&copy; 2026 SyncTools Pro</p>
    </footer>

    <script>
        const searchInput = document.getElementById('search');
        const count = document.getElementById('count');
        const cards = Array.from(document.querySelectorAll('.card'));
        const total = cards.length;

        searchInput.addEventListener('input', () => {{
            const keyword = searchInput.value.trim().toLowerCase();
            let visible = 0;
            cards.forEach((card) => {{
                const haystack = [
                    card.dataset.name || '',
                    card.querySelector('h3')?.textContent || '',
                    card.querySelector('.card-meta')?.textContent || '',
                ].join(' ').toLowerCase();
                const matched = !keyword || haystack.includes(keyword);
                card.style.display = matched ? '' : 'none';
                if (matched) visible += 1;
            }});
            count.textContent = `显示 ${{visible}} / ${{total}}`;
        }});
    </script>
</body>
</html>
"""

    (TARGET_DIR / "index.html").write_text(page, encoding="utf-8")


def sync_backup_html():
    for source in BACKUP_DIR.rglob("*.html"):
        rel = source.relative_to(BACKUP_DIR)
        if rel == Path("index.html"):
            continue
        destination = TARGET_DIR / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def verify_synced_html():
    problems = []
    for source in BACKUP_DIR.rglob("*.html"):
        rel = source.relative_to(BACKUP_DIR)
        if rel == Path("index.html"):
            continue
        destination = TARGET_DIR / rel
        if not destination.exists():
            problems.append(f"缺少文件: {rel}")
            continue
        if source.read_bytes() != destination.read_bytes():
            problems.append(f"文件不同步: {rel}")
    return problems


def normalize_fragment_text(fragment_html: str) -> str:
    if not fragment_html:
        return ""
    return normalize_text(lxml_html.fromstring(f"<div>{fragment_html}</div>").text_content())


def verify_product_indexes():
    problems = []
    for backup_product_dir in sorted(BACKUP_DIR.glob(PRODUCT_GLOB)):
        folder_name = backup_product_dir.name
        source_data = extract_backup_product(folder_name)
        generated = read_html(TARGET_DIR / folder_name / "index.html")

        generated_title = normalize_text(generated.xpath("string(//h1[@class='product-title'][1])"))
        generated_price = normalize_text(generated.xpath("string(//*[contains(@class,'price-now')][1])"))
        generated_desc = normalize_text(
            generated.xpath("string(//*[@id='panel-desc']//*[contains(@class,'desc-content')][1])")
        )
        generated_docs = normalize_text(
            generated.xpath("string(//*[@id='panel-docs']//*[contains(@class,'desc-content')][1])")
        )
        generated_files = [
            normalize_text(link.text_content())
            for link in generated.xpath("//*[@id='panel-files']//a[@href]")
        ]

        source_desc = normalize_fragment_text(source_data["description_html"])
        source_docs = normalize_fragment_text(source_data["documentation_html"])
        source_files = [entry["name"] for entry in source_data["file_entries"]]

        if generated_title != source_data["title"]:
            problems.append(f"{folder_name}: 标题不一致")
        if generated_price != (source_data["price"] or "价格未标注"):
            problems.append(f"{folder_name}: 价格不一致")
        if generated_desc != source_desc:
            problems.append(f"{folder_name}: 产品介绍不一致")
        if source_docs and generated_docs != source_docs:
            problems.append(f"{folder_name}: 使用文档不一致")
        if source_files and generated_files != source_files:
            problems.append(f"{folder_name}: 产品文件列表不一致")
    return problems


def verify_root_index():
    _, _, source_cards = extract_catalog_cards()
    generated = read_html(TARGET_DIR / "index.html")
    generated_cards = []
    for card in generated.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' card ')]"):
        generated_cards.append(
            {
                "folder": card.get("href", "").split("/")[0],
                "title": normalize_text(card.xpath("string(.//h3[1])")),
                "meta": normalize_text(card.xpath("string(.//*[contains(@class,'card-meta')][1])")),
                "price": normalize_text(card.xpath("string(.//*[contains(@class,'card-price')][1])")),
            }
        )
    return source_cards == generated_cards


def main():
    if not BACKUP_DIR.exists():
        raise SystemExit(f"Backup directory not found: {BACKUP_DIR}")

    sync_backup_html()

    for backup_product_dir in sorted(BACKUP_DIR.glob(PRODUCT_GLOB)):
        render_product_index(
            backup_product_dir.name,
            extract_backup_product(backup_product_dir.name),
        )

    render_root_index()

    sync_problems = verify_synced_html()
    index_problems = verify_product_indexes()
    root_ok = verify_root_index()

    if sync_problems or index_problems or not root_ok:
        for problem in sync_problems + index_problems:
            print(problem)
        if not root_ok:
            print("根目录 index.html 校验失败")
        raise SystemExit(1)

    product_count = len(list(BACKUP_DIR.glob(PRODUCT_GLOB)))
    print(
        f"修复完成：同步 {product_count} 个产品目录的备份 HTML，"
        f"重建 {product_count} 个产品 index.html，并重建根目录 index.html。"
    )


if __name__ == "__main__":
    main()
