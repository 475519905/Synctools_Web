#!/usr/bin/env python3
"""BlenderMarket Creator Dashboard - Full Product Backup Script
Downloads: descriptions, images, cover, product files, documentation for all products.
Uses AppleScript to control Chrome and extract data from authenticated pages.
"""

import subprocess
import json
import base64
import os
import time
import re
import urllib.request
import urllib.error
import ssl

BASE_DIR = os.path.expanduser("~/Desktop/BlenderMarket_Backup")
JS_FILE = os.path.join(BASE_DIR, "extract.js")
LOG_FILE = os.path.join(BASE_DIR, "download.log")

# All 40 product slugs
SLUGS = [
    "super3d-io-addon",
    "synctools-for-unity",
    "outliner-follow-active-object-smart---a-smarter-way-to-navigate-your-scene",
    "import-coreldraw-graphics-file",
    "midi-piano-motion-tools-pro-max---transform-music-into-visual-magic",
    "voxelizer-pro---advanced-model-voxelization-tool-for-blender",
    "inport-adobe-illustrator-ai-file",
    "alt-surface-navigation",
    "crossfire-ucc-file-export-import-",
    "autodesk-3ds-max-file-import-export",
    "advanced-maze-generator-pro---professional-maze-creation-for-blender",
    "smart-normals-fix-tool---intelligent-mesh-normal-repair",
    "easybake-the-ultimate-all-in-one-baking-toolkit",
    "super-bake-pro--the-ultimate-animation-baking-solution-for-blender",
    "maxon-cinema-4d-import-export-pro",
    "autodesk-maya-file-import-export-mb-",
    "synctools-for-sketchup",
    "octane-material-transfer-master",
    "synctools-for-zbrush",
    "midi-piano-motion-tools-pro",
    "after-effects-link-for-blender",
    "synctools-dcc-integration-suite",
    "synctools-for-unreal-engine",
    "import-export-3d-manufacturing-file",
    "synctools-for-houdini",
    "synctools-for-marvelous-designer",
    "synctools-for-rhino",
    "synctools-for-3ds-max",
    "sidefx-houdini-import-export-",
    "synctools-for-maya",
    "photoshop-link-for-blender",
    "-origin-adjustment-control",
    "material-manager-user-manual",
    "x-particles-importer-for-blender",
    "import-keyframe-animation-for-blender",
    "batch-script-execution",
    "midi-pianomotion-tools",
    "maxon-cinema-4d--file-import-export-convenient-script",
    "seamless-c4d-to-blender-material-conversion",
    "synctools-pro-v2",
]


def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_applescript(script):
    """Run AppleScript and return stdout."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def navigate_to(url):
    """Navigate Chrome active tab to URL."""
    script = f'''
    tell application "Google Chrome"
        tell active tab of front window
            set URL to "{url}"
        end tell
    end tell
    '''
    run_applescript(script)


def wait_for_page(max_wait=15):
    """Wait until product edit form is loaded."""
    for _ in range(max_wait):
        try:
            result = run_applescript('''
            tell application "Google Chrome"
                tell active tab of front window
                    execute javascript "document.querySelector('#product_title') ? 'yes' : 'no'"
                end tell
            end tell
            ''')
            if result == "yes":
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def extract_product_data():
    """Execute JS extraction in Chrome and return parsed data."""
    with open(JS_FILE, "r") as f:
        js_code = f.read()

    # Use heredoc-style AppleScript to avoid escaping issues
    script = '''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "''' + js_code.replace('"', '\\"').replace('\n', ' ') + '''"
        end tell
    end tell
    '''

    result = run_applescript(script)
    if not result:
        return None

    try:
        data = json.loads(result)
        return data
    except json.JSONDecodeError as e:
        log(f"  JSON parse error: {e}")
        return None


def download_url(url, dest):
    """Download a URL to destination file."""
    if not url or url == "null":
        return False
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
            data = response.read()
            if len(data) > 0:
                with open(dest, "wb") as f:
                    f.write(data)
                return True
    except Exception as e:
        log(f"  Download failed: {os.path.basename(dest)} - {e}")
    return False


def download_file_curl(url, dest):
    """Use curl for large file downloads (product files)."""
    if not url or url == "null":
        return False
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True

    try:
        result = subprocess.run(
            ["curl", "-sL", "-o", dest, url],
            capture_output=True, timeout=300
        )
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            return True
        else:
            if os.path.exists(dest):
                os.remove(dest)
    except Exception as e:
        log(f"  Curl download failed: {os.path.basename(dest)} - {e}")
    return False


def safe_filename(name, max_len=80):
    """Create a filesystem-safe name."""
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:max_len]


def get_extension(url):
    """Extract file extension from URL."""
    path = url.split("?")[0]
    basename = os.path.basename(path)
    if "." in basename:
        return basename.rsplit(".", 1)[-1]
    return "png"


def main():
    log("=" * 50)
    log(f"Starting BlenderMarket Backup - {len(SLUGS)} products")
    log("=" * 50)

    summary = []

    for idx, slug in enumerate(SLUGS):
        num = idx + 1
        log("")
        log(f"[{num}/{len(SLUGS)}] Processing: {slug}")

        # Navigate to product edit page
        url = f"https://superhivemarket.com/creator/products/{slug}/edit"
        navigate_to(url)
        time.sleep(3)

        # Wait for page to fully load
        if not wait_for_page():
            log(f"  ERROR: Page did not load for {slug}")
            continue

        # Small extra wait for dynamic content
        time.sleep(1)

        # Extract data
        data = extract_product_data()
        if not data:
            log(f"  ERROR: Failed to extract data for {slug}")
            continue

        title = data.get("title", "") or slug
        log(f"  Title: {title}")

        # Create product directory
        safe_name = safe_filename(title)
        product_dir = os.path.join(BASE_DIR, f"{num:02d}_{safe_name}")
        images_dir = os.path.join(product_dir, "images")
        files_dir = os.path.join(product_dir, "files")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(files_dir, exist_ok=True)

        # Save raw JSON
        with open(os.path.join(product_dir, "raw_data.json"), "w") as f:
            # Decode base64 fields for the raw dump
            raw = dict(data)
            try:
                if raw.get("description"):
                    raw["description"] = base64.b64decode(raw["description"]).decode("utf-8")
            except Exception:
                pass
            try:
                if raw.get("documentation"):
                    raw["documentation"] = base64.b64decode(raw["documentation"]).decode("utf-8")
            except Exception:
                pass
            json.dump(raw, f, ensure_ascii=False, indent=2)

        # Decode and save description
        desc_html = ""
        if data.get("description"):
            try:
                desc_html = base64.b64decode(data["description"]).decode("utf-8")
            except Exception:
                desc_html = data["description"]

        if desc_html:
            with open(os.path.join(product_dir, "description.html"), "w") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title} - Description</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
img {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
<h1>{title}</h1>
{desc_html}
</body>
</html>""")
            log(f"  Saved description.html ({len(desc_html)} chars)")

        # Decode and save documentation
        docs_html = ""
        if data.get("documentation"):
            try:
                docs_html = base64.b64decode(data["documentation"]).decode("utf-8")
            except Exception:
                docs_html = data["documentation"]

        if docs_html:
            with open(os.path.join(product_dir, "documentation.html"), "w") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title} - Documentation</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
img {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
<h1>{title} - Documentation</h1>
{docs_html}
</body>
</html>""")
            log(f"  Saved documentation.html ({len(docs_html)} chars)")

        # Download cover image
        img_count = 0
        cover_url = data.get("coverImage", "")
        if cover_url:
            ext = get_extension(cover_url)
            dest = os.path.join(images_dir, f"00_cover.{ext}")
            if download_url(cover_url, dest):
                log(f"  Downloaded cover image")
                img_count += 1

        # Download gallery images
        for gi, gurl in enumerate(data.get("galleryImages", [])):
            ext = get_extension(gurl)
            dest = os.path.join(images_dir, f"{gi+1:02d}_gallery.{ext}")
            if download_url(gurl, dest):
                img_count += 1
        if data.get("galleryImages"):
            log(f"  Downloaded {len(data['galleryImages'])} gallery images")

        # Download description embedded images
        desc_img_count = 0
        for di, durl in enumerate(data.get("descriptionImages", [])):
            fname = os.path.basename(durl.split("?")[0])
            if "." not in fname:
                fname = f"{fname}.png"
            # Sanitize filename
            fname = re.sub(r'[^\w.-]', '_', fname)
            dest = os.path.join(images_dir, f"desc_{di:02d}_{fname}")
            if download_url(durl, dest):
                desc_img_count += 1
        if desc_img_count > 0:
            log(f"  Downloaded {desc_img_count} description images")

        img_count += desc_img_count

        # Download product files
        file_count = 0
        for fi in data.get("files", []):
            fname = fi.get("name", f"file_{file_count}.zip")
            fname = re.sub(r'[^\w.-]', '_', fname)
            dest = os.path.join(files_dir, fname)
            if download_file_curl(fi.get("url", ""), dest):
                size = os.path.getsize(dest)
                size_str = f"{size/1024:.1f}KB" if size < 1048576 else f"{size/1048576:.1f}MB"
                log(f"  Downloaded file: {fname} ({size_str})")
                file_count += 1

        # Save info summary
        with open(os.path.join(product_dir, "info.txt"), "w") as f:
            f.write(f"Product: {title}\n")
            f.write(f"Slug: {slug}\n")
            f.write(f"Price: {data.get('price', 'N/A')}\n")
            f.write(f"Cover image: {'Yes' if cover_url else 'No'}\n")
            f.write(f"Gallery images: {len(data.get('galleryImages', []))}\n")
            f.write(f"Description images: {len(data.get('descriptionImages', []))}\n")
            f.write(f"Product files: {len(data.get('files', []))}\n")
            for fi in data.get("files", []):
                f.write(f"  - {fi.get('name', '?')}\n")

        summary.append({
            "num": num,
            "title": title,
            "images": img_count,
            "files": file_count
        })

        log(f"  Done: {img_count} images, {file_count} files")

    # Print summary
    log("")
    log("=" * 50)
    log("BACKUP COMPLETE!")
    log("=" * 50)
    log("")
    total_imgs = 0
    total_files = 0
    for s in summary:
        log(f"  {s['num']:2d}. {s['title'][:50]:50s} | {s['images']:3d} imgs | {s['files']:2d} files")
        total_imgs += s["images"]
        total_files += s["files"]
    log("")
    log(f"Total: {len(summary)} products, {total_imgs} images, {total_files} files")
    log(f"Location: {BASE_DIR}")


if __name__ == "__main__":
    main()
