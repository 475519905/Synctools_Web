#!/bin/bash
# BlenderMarket Creator Dashboard - Full Product Backup Script
# Downloads: descriptions, images, cover, product files, documentation for all products

BASE_DIR="$HOME/Desktop/BlenderMarket_Backup"
LOG_FILE="$BASE_DIR/download.log"

# All 40 product slugs
SLUGS=(
  "super3d-io-addon"
  "synctools-for-unity"
  "outliner-follow-active-object-smart---a-smarter-way-to-navigate-your-scene"
  "import-coreldraw-graphics-file"
  "midi-piano-motion-tools-pro-max---transform-music-into-visual-magic"
  "voxelizer-pro---advanced-model-voxelization-tool-for-blender"
  "inport-adobe-illustrator-ai-file"
  "alt-surface-navigation"
  "crossfire-ucc-file-export-import-"
  "autodesk-3ds-max-file-import-export"
  "advanced-maze-generator-pro---professional-maze-creation-for-blender"
  "smart-normals-fix-tool---intelligent-mesh-normal-repair"
  "easybake-the-ultimate-all-in-one-baking-toolkit"
  "super-bake-pro--the-ultimate-animation-baking-solution-for-blender"
  "maxon-cinema-4d-import-export-pro"
  "autodesk-maya-file-import-export-mb-"
  "synctools-for-sketchup"
  "octane-material-transfer-master"
  "synctools-for-zbrush"
  "midi-piano-motion-tools-pro"
  "after-effects-link-for-blender"
  "synctools-dcc-integration-suite"
  "synctools-for-unreal-engine"
  "import-export-3d-manufacturing-file"
  "synctools-for-houdini"
  "synctools-for-marvelous-designer"
  "synctools-for-rhino"
  "synctools-for-3ds-max"
  "sidefx-houdini-import-export-"
  "synctools-for-maya"
  "photoshop-link-for-blender"
  "-origin-adjustment-control"
  "material-manager-user-manual"
  "x-particles-importer-for-blender"
  "import-keyframe-animation-for-blender"
  "batch-script-execution"
  "midi-pianomotion-tools"
  "maxon-cinema-4d--file-import-export-convenient-script"
  "seamless-c4d-to-blender-material-conversion"
  "synctools-pro-v2"
)

log() {
  echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

extract_product_data() {
  local slug="$1"
  local url="https://superhivemarket.com/creator/products/${slug}/edit"

  # Navigate to the product edit page
  osascript -e "
    tell application \"Google Chrome\"
      tell active tab of front window
        set URL to \"${url}\"
      end tell
    end tell
  " 2>/dev/null

  # Wait for page to load
  sleep 4

  # Wait until page is fully loaded (check for form)
  for attempt in 1 2 3 4 5; do
    local loaded
    loaded=$(osascript -e '
      tell application "Google Chrome"
        tell active tab of front window
          execute javascript "document.querySelector(\"#product_title\") ? \"yes\" : \"no\""
        end tell
      end tell
    ' 2>/dev/null)
    if [ "$loaded" = "yes" ]; then
      break
    fi
    sleep 2
  done

  # Extract all data as JSON
  osascript -e '
    tell application "Google Chrome"
      tell active tab of front window
        execute javascript "
          (function() {
            var data = {};

            // 1. Product title
            var titleEl = document.querySelector(\"#product_title\");
            data.title = titleEl ? titleEl.value : \"\";

            // 2. Featured image (cover) and gallery images
            var gallerySection = document.querySelector(\"#gallery\");
            var hiddenInputs = gallerySection ? gallerySection.querySelectorAll(\"input[type=hidden]\") : [];
            data.coverImage = \"\";
            data.galleryImages = [];
            for(var i=0; i<hiddenInputs.length; i++) {
              var val = hiddenInputs[i].value;
              var name = hiddenInputs[i].name;
              if(val && val.includes(\"superhivemarket.com\")) {
                if(name === \"product[image]\") {
                  data.coverImage = val.split(\"|\").pop();
                } else {
                  data.galleryImages.push(val.split(\"|\").pop());
                }
              }
            }

            // 3. Description HTML
            var descSection = document.querySelector(\"#description\");
            var descTextarea = descSection ? descSection.querySelector(\"textarea\") : null;
            data.description = descTextarea ? descTextarea.value : \"\";

            // 4. Extract images embedded in description
            var descDiv = document.createElement(\"div\");
            descDiv.innerHTML = data.description;
            var descImgs = descDiv.querySelectorAll(\"img\");
            data.descriptionImages = [];
            for(var i=0; i<descImgs.length; i++) {
              if(descImgs[i].src) data.descriptionImages.push(descImgs[i].src);
            }

            // 5. Documentation HTML
            var docsSection = document.querySelector(\"#documentation\");
            var docsTextarea = docsSection ? docsSection.querySelector(\"textarea\") : null;
            data.documentation = docsTextarea ? docsTextarea.value : \"\";

            // 6. Product file download links and names
            var filesSection = document.querySelector(\"#files\");
            data.files = [];
            if(filesSection) {
              var fileLinks = filesSection.querySelectorAll(\"a[href*=cloudflarestorage], a[href*=r2.cloud]\");
              var fileItems = filesSection.querySelectorAll(\".filepond--item\");

              // Get file names from the items
              var fileNames = [];
              var fileNameEls = filesSection.querySelectorAll(\".filepond--file-info-main\");
              for(var i=0; i<fileNameEls.length; i++) {
                fileNames.push(fileNameEls[i].textContent.trim());
              }

              // If no filepond names, try to extract from text
              if(fileNames.length === 0) {
                var allText = filesSection.innerText;
                var lines = allText.split(\"\\n\");
                for(var i=0; i<lines.length; i++) {
                  var line = lines[i].trim();
                  if(line.match(/\\.(zip|blend|py|rar|7z|pdf|txt)$/i)) {
                    fileNames.push(line);
                  }
                }
              }

              for(var i=0; i<fileLinks.length; i++) {
                data.files.push({
                  url: fileLinks[i].href,
                  name: (i < fileNames.length) ? fileNames[i] : (\"file_\" + i + \".zip\")
                });
              }
            }

            // 7. FAQ section
            var faqSection = document.querySelector(\"#documentation\");
            var faqItems = faqSection ? faqSection.querySelectorAll(\".faq-item, .accordion-item\") : [];
            data.faqHTML = \"\";
            for(var i=0; i<faqItems.length; i++) {
              data.faqHTML += faqItems[i].outerHTML;
            }

            // 8. Also get the short description / tagline
            var taglineEl = document.querySelector(\"textarea[id*=tagline], input[id*=tagline], #product_tagline\");
            data.tagline = taglineEl ? taglineEl.value : \"\";

            // 9. Price info
            var priceEl = document.querySelector(\".price-box span:last-child\");
            data.price = priceEl ? priceEl.textContent.trim() : \"\";

            return JSON.stringify(data);
          })()
        "
      end tell
    end tell
  ' 2>/dev/null
}

download_image() {
  local url="$1"
  local dest="$2"

  if [ -z "$url" ] || [ "$url" = "null" ]; then
    return
  fi

  if [ -f "$dest" ]; then
    log "  Already exists: $(basename "$dest")"
    return
  fi

  curl -sL -o "$dest" "$url" 2>/dev/null
  if [ -f "$dest" ] && [ -s "$dest" ]; then
    log "  Downloaded: $(basename "$dest")"
  else
    log "  FAILED: $(basename "$dest") from $url"
    rm -f "$dest"
  fi
}

download_file() {
  local url="$1"
  local dest="$2"

  if [ -z "$url" ] || [ "$url" = "null" ]; then
    return
  fi

  if [ -f "$dest" ]; then
    log "  Already exists: $(basename "$dest")"
    return
  fi

  curl -sL -o "$dest" "$url" 2>/dev/null
  if [ -f "$dest" ] && [ -s "$dest" ]; then
    local size
    size=$(ls -lh "$dest" | awk '{print $5}')
    log "  Downloaded file: $(basename "$dest") ($size)"
  else
    log "  FAILED file: $(basename "$dest")"
    rm -f "$dest"
  fi
}

# Main loop
log "========================================="
log "Starting BlenderMarket Backup"
log "Total products: ${#SLUGS[@]}"
log "========================================="

for idx in "${!SLUGS[@]}"; do
  slug="${SLUGS[$idx]}"
  num=$((idx + 1))

  log ""
  log "[$num/${#SLUGS[@]}] Processing: $slug"

  # Extract data
  json_data=$(extract_product_data "$slug")

  if [ -z "$json_data" ] || [ "$json_data" = "null" ]; then
    log "  ERROR: Failed to extract data for $slug"
    continue
  fi

  # Parse JSON with python
  title=$(echo "$json_data" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('title',''))" 2>/dev/null)

  if [ -z "$title" ]; then
    title="$slug"
  fi

  # Create safe directory name
  safe_name=$(echo "$title" | sed 's/[^a-zA-Z0-9_ -]//g' | sed 's/  */ /g' | head -c 80)
  product_dir="$BASE_DIR/${num}_${safe_name}"
  mkdir -p "$product_dir/images"
  mkdir -p "$product_dir/files"

  log "  Title: $title"
  log "  Dir: $(basename "$product_dir")"

  # Save raw JSON data for reference
  echo "$json_data" | python3 -m json.tool > "$product_dir/raw_data.json" 2>/dev/null

  # Save description
  desc=$(echo "$json_data" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
print(d.get('description', ''))
" 2>/dev/null)

  if [ -n "$desc" ]; then
    cat > "$product_dir/description.html" << HTMLEOF
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>${title} - Description</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }
img { max-width: 100%; height: auto; }
</style>
</head>
<body>
<h1>${title}</h1>
${desc}
</body>
</html>
HTMLEOF
    log "  Saved description.html"
  fi

  # Save documentation
  docs=$(echo "$json_data" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
print(d.get('documentation', ''))
" 2>/dev/null)

  if [ -n "$docs" ]; then
    cat > "$product_dir/documentation.html" << HTMLEOF
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>${title} - Documentation</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }
img { max-width: 100%; height: auto; }
</style>
</head>
<body>
<h1>${title} - Documentation</h1>
${docs}
</body>
</html>
HTMLEOF
    log "  Saved documentation.html"
  fi

  # Download cover image
  cover_url=$(echo "$json_data" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
print(d.get('coverImage', ''))
" 2>/dev/null)

  if [ -n "$cover_url" ] && [ "$cover_url" != "" ]; then
    ext="${cover_url##*.}"
    ext="${ext%%\?*}"
    download_image "$cover_url" "$product_dir/images/00_cover.${ext}"
  fi

  # Download gallery images
  gallery_urls=$(echo "$json_data" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
for i, url in enumerate(d.get('galleryImages', [])):
    print(f'{i}|{url}')
" 2>/dev/null)

  while IFS='|' read -r gidx gurl; do
    if [ -n "$gurl" ]; then
      ext="${gurl##*.}"
      ext="${ext%%\?*}"
      padded=$(printf "%02d" $((gidx + 1)))
      download_image "$gurl" "$product_dir/images/${padded}_gallery.${ext}"
    fi
  done <<< "$gallery_urls"

  # Download description embedded images
  desc_img_urls=$(echo "$json_data" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
for i, url in enumerate(d.get('descriptionImages', [])):
    print(f'{i}|{url}')
" 2>/dev/null)

  while IFS='|' read -r didx durl; do
    if [ -n "$durl" ] && [ "$durl" != "" ]; then
      # Get extension from URL
      fname=$(basename "$durl" | sed 's/\?.*//')
      if [[ "$fname" != *.* ]]; then
        fname="${fname}.png"
      fi
      download_image "$durl" "$product_dir/images/desc_${didx}_${fname}"
    fi
  done <<< "$desc_img_urls"

  # Download product files
  file_data=$(echo "$json_data" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
for f in d.get('files', []):
    name = f.get('name', 'unknown.zip').replace(' ', '_')
    url = f.get('url', '')
    print(f'{name}|{url}')
" 2>/dev/null)

  while IFS='|' read -r fname furl; do
    if [ -n "$furl" ] && [ "$furl" != "" ]; then
      download_file "$furl" "$product_dir/files/${fname}"
    fi
  done <<< "$file_data"

  # Save product info summary
  echo "$json_data" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
print(f\"Product: {d.get('title', 'N/A')}\")
print(f\"Tagline: {d.get('tagline', 'N/A')}\")
print(f\"Price: {d.get('price', 'N/A')}\")
print(f\"Cover: {d.get('coverImage', 'N/A')}\")
print(f\"Gallery images: {len(d.get('galleryImages', []))}\")
print(f\"Description images: {len(d.get('descriptionImages', []))}\")
print(f\"Product files: {len(d.get('files', []))}\")
for f in d.get('files', []):
    print(f\"  - {f.get('name', '?')}\")
" 2>/dev/null > "$product_dir/info.txt"

  log "  Done processing $slug"
done

log ""
log "========================================="
log "Backup complete!"
log "Location: $BASE_DIR"
log "========================================="

# Generate summary
echo ""
echo "=== BACKUP SUMMARY ==="
for d in "$BASE_DIR"/*/; do
  if [ -d "$d" ]; then
    name=$(basename "$d")
    imgs=$(find "$d/images" -type f 2>/dev/null | wc -l | tr -d ' ')
    files=$(find "$d/files" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "$name: ${imgs} images, ${files} files"
  fi
done
