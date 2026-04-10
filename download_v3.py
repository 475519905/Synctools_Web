#!/usr/bin/env python3
"""BlenderMarket Creator Dashboard - Full Product Backup Script v3
Uses temporary AppleScript files to avoid escaping issues.
"""

import subprocess
import json
import base64
import os
import time
import re
import tempfile
import urllib.request
import ssl

BASE_DIR = os.path.expanduser("~/Desktop/BlenderMarket_Backup")
LOG_FILE = os.path.join(BASE_DIR, "download.log")

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

# The extraction JavaScript
EXTRACT_JS = r"""(function() {
  var data = {};
  data.title = document.querySelector('#product_title') ? document.querySelector('#product_title').value : '';
  var gallerySection = document.querySelector('#gallery');
  var hiddenInputs = gallerySection ? gallerySection.querySelectorAll('input[type=hidden]') : [];
  data.coverImage = '';
  data.galleryImages = [];
  for(var i=0; i<hiddenInputs.length; i++) {
    var val = hiddenInputs[i].value;
    var name = hiddenInputs[i].name;
    if(val && val.includes('superhivemarket.com')) {
      if(name === 'product[image]') {
        data.coverImage = val.split('|').pop();
      } else {
        data.galleryImages.push(val.split('|').pop());
      }
    }
  }
  var descSection = document.querySelector('#description');
  var descTextarea = descSection ? descSection.querySelector('textarea') : null;
  data.description = descTextarea ? btoa(unescape(encodeURIComponent(descTextarea.value))) : '';
  var docsSection = document.querySelector('#documentation');
  var docsTextarea = docsSection ? docsSection.querySelector('textarea') : null;
  data.documentation = docsTextarea ? btoa(unescape(encodeURIComponent(docsTextarea.value))) : '';
  var filesSection = document.querySelector('#files');
  data.files = [];
  if(filesSection) {
    var fileLinks = filesSection.querySelectorAll('a[href*=cloudflarestorage]');
    var fileNames = [];
    var allText = filesSection.innerText;
    var lines = allText.split('\n');
    for(var i=0; i<lines.length; i++) {
      var line = lines[i].trim();
      if(line.match(/\.(zip|blend|py|rar|7z|pdf|txt)$/i)) {
        fileNames.push(line);
      }
    }
    for(var i=0; i<fileLinks.length; i++) {
      data.files.push({
        url: fileLinks[i].href,
        name: (i < fileNames.length) ? fileNames[i] : ('file_' + i + '.zip')
      });
    }
  }
  var descDiv = document.createElement('div');
  if(descTextarea) descDiv.innerHTML = descTextarea.value;
  var descImgs = descDiv.querySelectorAll('img');
  data.descriptionImages = [];
  for(var i=0; i<descImgs.length; i++) {
    var src = descImgs[i].getAttribute('src');
    if(src) data.descriptionImages.push(src);
  }
  data.price = '';
  var priceEl = document.querySelector('.price-box span:last-child');
  if(priceEl) data.price = priceEl.textContent.trim();
  return JSON.stringify(data);
})()"""


def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_osascript_file(content):
    """Write AppleScript to temp file and run it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".scpt", delete=False) as f:
        f.write(content)
        tmp = f.name
    try:
        result = subprocess.run(
            ["osascript", tmp],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return ""
    finally:
        os.unlink(tmp)


def navigate_to(url):
    script = f'''tell application "Google Chrome"
    tell active tab of front window
        set URL to "{url}"
    end tell
end tell'''
    run_osascript_file(script)


def wait_for_page(max_wait=15):
    script = '''tell application "Google Chrome"
    tell active tab of front window
        execute javascript "document.querySelector('#product_title') ? 'yes' : 'no'"
    end tell
end tell'''
    for _ in range(max_wait):
        result = run_osascript_file(script)
        if result == "yes":
            return True
        time.sleep(1)
    return False


def extract_product_data():
    """Execute JS in Chrome via AppleScript file using do shell script."""
    js_file = os.path.join(BASE_DIR, "_extract_tmp.js")
    with open(js_file, "w") as f:
        f.write(EXTRACT_JS)

    script = f'''set jsCode to do shell script "cat {js_file}"
tell application "Google Chrome"
    tell active tab of front window
        execute javascript jsCode
    end tell
end tell'''

    result = run_osascript_file(script)
    if not result:
        return None

    try:
        data = json.loads(result)
        return data
    except json.JSONDecodeError as e:
        log(f"  JSON parse error: {e}")
        log(f"  Raw result (first 200): {result[:200]}")
        return None


def download_url(url, dest):
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
    if not url or url == "null":
        return False
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    try:
        subprocess.run(["curl", "-sL", "-o", dest, url], capture_output=True, timeout=300)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            return True
        if os.path.exists(dest):
            os.remove(dest)
    except Exception as e:
        log(f"  Curl failed: {os.path.basename(dest)} - {e}")
    return False


def safe_filename(name, max_len=80):
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:max_len] if name else "unknown"


def get_extension(url):
    path = url.split("?")[0]
    basename = os.path.basename(path)
    if "." in basename:
        return basename.rsplit(".", 1)[-1]
    return "png"


def main():
    # Clear old log
    open(LOG_FILE, "w").close()

    log("=" * 50)
    log(f"Starting BlenderMarket Backup - {len(SLUGS)} products")
    log("=" * 50)

    summary = []

    for idx, slug in enumerate(SLUGS):
        num = idx + 1
        log("")
        log(f"[{num}/{len(SLUGS)}] Processing: {slug}")

        url = f"https://superhivemarket.com/creator/products/{slug}/edit"
        navigate_to(url)
        time.sleep(3)

        if not wait_for_page():
            log(f"  ERROR: Page did not load for {slug}")
            continue

        time.sleep(1)

        data = extract_product_data()
        if not data:
            log(f"  ERROR: Failed to extract data for {slug}")
            continue

        title = data.get("title", "") or slug
        log(f"  Title: {title}")

        safe_name = safe_filename(title)
        product_dir = os.path.join(BASE_DIR, f"{num:02d}_{safe_name}")
        images_dir = os.path.join(product_dir, "images")
        files_dir = os.path.join(product_dir, "files")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(files_dir, exist_ok=True)

        # Save raw JSON
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
        with open(os.path.join(product_dir, "raw_data.json"), "w") as f:
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
<html><head><meta charset="utf-8"><title>{title} - Description</title>
<style>body{{font-family:-apple-system,sans-serif;max-width:900px;margin:40px auto;padding:20px;}}img{{max-width:100%;height:auto;}}</style>
</head><body><h1>{title}</h1>{desc_html}</body></html>""")
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
<html><head><meta charset="utf-8"><title>{title} - Documentation</title>
<style>body{{font-family:-apple-system,sans-serif;max-width:900px;margin:40px auto;padding:20px;}}img{{max-width:100%;height:auto;}}</style>
</head><body><h1>{title} - Documentation</h1>{docs_html}</body></html>""")
            log(f"  Saved documentation.html ({len(docs_html)} chars)")

        # Download cover image
        img_count = 0
        cover_url = data.get("coverImage", "")
        if cover_url:
            ext = get_extension(cover_url)
            if download_url(cover_url, os.path.join(images_dir, f"00_cover.{ext}")):
                img_count += 1
                log(f"  Downloaded cover image")

        # Download gallery images
        for gi, gurl in enumerate(data.get("galleryImages", [])):
            ext = get_extension(gurl)
            if download_url(gurl, os.path.join(images_dir, f"{gi+1:02d}_gallery.{ext}")):
                img_count += 1
        if data.get("galleryImages"):
            log(f"  Downloaded {len(data['galleryImages'])} gallery images")

        # Download description embedded images
        for di, durl in enumerate(data.get("descriptionImages", [])):
            fname = os.path.basename(durl.split("?")[0])
            if "." not in fname:
                fname = f"{fname}.png"
            fname = re.sub(r'[^\w.-]', '_', fname)
            if download_url(durl, os.path.join(images_dir, f"desc_{di:02d}_{fname}")):
                img_count += 1
        if data.get("descriptionImages"):
            log(f"  Downloaded {len(data['descriptionImages'])} description images")

        # Download product files
        file_count = 0
        for fi in data.get("files", []):
            fname = fi.get("name", f"file_{file_count}.zip")
            fname = re.sub(r'[^\w.-]', '_', fname)
            dest = os.path.join(files_dir, fname)
            if download_file_curl(fi.get("url", ""), dest):
                size = os.path.getsize(dest)
                sz = f"{size/1024:.1f}KB" if size < 1048576 else f"{size/1048576:.1f}MB"
                log(f"  Downloaded file: {fname} ({sz})")
                file_count += 1

        # Save info
        with open(os.path.join(product_dir, "info.txt"), "w") as f:
            f.write(f"Product: {title}\nSlug: {slug}\nPrice: {data.get('price','N/A')}\n")
            f.write(f"Cover: {'Yes' if cover_url else 'No'}\n")
            f.write(f"Gallery images: {len(data.get('galleryImages',[]))}\n")
            f.write(f"Description images: {len(data.get('descriptionImages',[]))}\n")
            f.write(f"Product files: {len(data.get('files',[]))}\n")
            for fi in data.get("files", []):
                f.write(f"  - {fi.get('name','?')}\n")

        summary.append({"num": num, "title": title, "images": img_count, "files": file_count})
        log(f"  Complete: {img_count} images, {file_count} files")

    log("")
    log("=" * 50)
    log("BACKUP COMPLETE!")
    log("=" * 50)
    total_imgs = sum(s["images"] for s in summary)
    total_files = sum(s["files"] for s in summary)
    for s in summary:
        log(f"  {s['num']:2d}. {s['title'][:50]:50s} | {s['images']:3d} imgs | {s['files']:2d} files")
    log(f"\nTotal: {len(summary)} products, {total_imgs} images, {total_files} files")
    log(f"Location: {BASE_DIR}")


if __name__ == "__main__":
    main()
