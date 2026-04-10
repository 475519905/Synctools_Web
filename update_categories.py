#!/usr/bin/env python3
"""Update existing product backups with Categories, Software & License data.
Reads from each product edit page and updates info.txt and raw_data.json.
"""

import subprocess
import json
import base64
import os
import time
import re
import tempfile
import glob

BASE_DIR = os.path.expanduser("~/Desktop/BlenderMarket_Backup")
LOG_FILE = os.path.join(BASE_DIR, "update_categories.log")

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
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_osascript_file(content):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".scpt", delete=False) as f:
        f.write(content)
        tmp = f.name
    try:
        result = subprocess.run(
            ["osascript", tmp], capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception:
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


def extract_categories_data():
    """Extract only the categories/software/license fields."""
    js_file = os.path.join(BASE_DIR, "_extract_tmp.js")
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
        return json.loads(result)
    except json.JSONDecodeError as e:
        log(f"  JSON parse error: {e}")
        return None


def find_product_dir(num):
    """Find existing product directory by number prefix."""
    pattern = os.path.join(BASE_DIR, f"{num:02d}_*")
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def main():
    open(LOG_FILE, "w").close()

    log("=" * 50)
    log("Updating Categories, Software & License for all products")
    log("=" * 50)

    for idx, slug in enumerate(SLUGS):
        num = idx + 1
        log(f"")
        log(f"[{num}/{len(SLUGS)}] Processing: {slug}")

        product_dir = find_product_dir(num)
        if not product_dir:
            log(f"  SKIP: No directory found for product #{num}")
            continue

        url = f"https://superhivemarket.com/creator/products/{slug}/edit"
        navigate_to(url)
        time.sleep(3)

        if not wait_for_page():
            log(f"  ERROR: Page did not load for {slug}")
            continue

        time.sleep(1)

        data = extract_categories_data()
        if not data:
            log(f"  ERROR: Failed to extract data for {slug}")
            continue

        title = data.get("title", "") or slug
        categories = data.get("categories", [])
        tags = data.get("tags", [])
        blender_min = data.get("blenderVersionMin", "")
        blender_max = data.get("blenderVersionMax", "")
        render_engines = data.get("renderEngines", [])
        misc_data = data.get("miscData", [])
        license_type = data.get("license", "")

        log(f"  Title: {title}")
        log(f"  Categories: {', '.join(categories)}")
        log(f"  Tags: {', '.join(tags)}")
        log(f"  Blender: {blender_min} - {blender_max}")
        log(f"  Render Engines: {', '.join(render_engines) if render_engines else 'None'}")
        log(f"  Misc Data: {', '.join(misc_data) if misc_data else 'None'}")
        log(f"  License: {license_type}")

        # Update raw_data.json - merge categories fields
        raw_file = os.path.join(product_dir, "raw_data.json")
        raw = {}
        if os.path.exists(raw_file):
            try:
                with open(raw_file, "r") as f:
                    raw = json.load(f)
            except Exception:
                pass

        raw["categories"] = categories
        raw["tags"] = tags
        raw["blenderVersionMin"] = blender_min
        raw["blenderVersionMax"] = blender_max
        raw["renderEngines"] = render_engines
        raw["miscData"] = misc_data
        raw["license"] = license_type

        with open(raw_file, "w") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)

        # Update info.txt - append categories section
        info_file = os.path.join(product_dir, "info.txt")
        info_lines = []
        if os.path.exists(info_file):
            with open(info_file, "r") as f:
                # Read existing lines but remove old categories section if any
                for line in f:
                    if line.strip().startswith("--- Categories"):
                        break
                    info_lines.append(line)

        # Append categories section
        info_lines.append("\n--- Categories, Software & License ---\n")
        info_lines.append(f"Categories: {', '.join(categories)}\n")
        info_lines.append(f"Tags: {', '.join(tags)}\n")
        info_lines.append(f"Blender Version Min: {blender_min}\n")
        info_lines.append(f"Blender Version Max: {blender_max}\n")
        info_lines.append(f"Render Engines: {', '.join(render_engines) if render_engines else 'None'}\n")
        info_lines.append(f"Misc Data: {', '.join(misc_data) if misc_data else 'None'}\n")
        info_lines.append(f"License: {license_type}\n")

        with open(info_file, "w") as f:
            f.writelines(info_lines)

        log(f"  Updated info.txt and raw_data.json")

    log("")
    log("=" * 50)
    log("Categories update complete!")
    log("=" * 50)


if __name__ == "__main__":
    main()
