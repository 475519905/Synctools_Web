#!/usr/bin/env python3
"""Backup all events from BlenderMarket Creator Reports including View Event details."""

import subprocess
import json
import os
import time
import tempfile
import csv

BASE_DIR = os.path.expanduser("~/Desktop/BlenderMarket_Backup")
EVENTS_DIR = os.path.join(BASE_DIR, "events_report")
LOG_FILE = os.path.join(EVENTS_DIR, "events_backup.log")

os.makedirs(EVENTS_DIR, exist_ok=True)

# JS to extract event rows from a list page
EXTRACT_LIST_JS = r"""(function() {
  var rows = document.querySelectorAll('table tbody tr');
  var events = [];
  for(var i=0; i<rows.length; i++) {
    var cells = rows[i].querySelectorAll('td');
    if(cells.length >= 3) {
      var link = rows[i].querySelector('a[href*="/events/"]');
      var eventId = '';
      if(link) {
        var m = link.href.match(/events\/(\d+)/);
        if(m) eventId = m[1];
      }
      events.push({
        created: cells[0] ? cells[0].textContent.trim() : '',
        event: cells[1] ? cells[1].textContent.trim() : '',
        productId: cells[2] ? cells[2].textContent.trim() : '',
        eventId: eventId
      });
    }
  }
  // Also get summary stats
  var statsText = document.body.innerText;
  var stats = {};
  var viewsMatch = statsText.match(/(\d+)\s*\n\s*Product Views/);
  if(viewsMatch) stats.productViews = viewsMatch[1];
  var cartMatch = statsText.match(/(\d+)\s*\n[\d.]+%\s*\n\s*Added to Cart/);
  if(cartMatch) stats.addedToCart = cartMatch[1];
  var checkoutMatch = statsText.match(/(\d+)\s*\n[\d.]+%\s*\n\s*Reached Checkout/);
  if(checkoutMatch) stats.reachedCheckout = checkoutMatch[1];
  var purchasedMatch = statsText.match(/(\d+)\s*\n[\d.]+%\s*\n\s*Purchased/);
  if(purchasedMatch) stats.purchased = purchasedMatch[1];
  var convMatch = statsText.match(/([\d.]+%)\s*\n\s*Shop Conversion/);
  if(convMatch) stats.conversionRate = convMatch[1];

  // Referrers
  var refSection = statsText.match(/Top 10 Referrers\n([\s\S]*?)Creator Dashboard/);
  stats.referrers = refSection ? refSection[1].trim() : '';

  var totalMatch = statsText.match(/Displaying events \d+-\d+ of (\d+)/);
  stats.totalEvents = totalMatch ? totalMatch[1] : '0';

  return JSON.stringify({events: events, stats: stats});
})()"""

# JS to extract View Event details
EXTRACT_DETAIL_JS = r"""(function() {
  var text = document.querySelector('.container-fluid').innerText;
  var data = {};
  var fields = ['Created', 'Product ID', 'Referrer', 'Affiliate', 'Landing Page',
    'Browser', 'OS', 'Device Type', 'Region', 'City', 'Country',
    'UTM Campaign', 'UTM Source', 'UTM Medium', 'UTM Term', 'UTM Content'];
  for(var i=0; i<fields.length; i++) {
    var re = new RegExp(fields[i] + ':\\s*(.*)');
    var m = text.match(re);
    data[fields[i]] = m ? m[1].trim() : '';
  }
  // Get event type from header
  var header = text.match(/(Viewed Product|Added To Cart|Reached Checkout|Purchased) Event #(\d+)/);
  if(header) {
    data['Event Type'] = header[1];
    data['Event ID'] = header[2];
  }
  return JSON.stringify(data);
})()"""


def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_osascript(content):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".scpt", delete=False) as f:
        f.write(content)
        tmp = f.name
    try:
        result = subprocess.run(["osascript", tmp], capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception:
        return ""
    finally:
        os.unlink(tmp)


def navigate_to(url):
    run_osascript(f'''tell application "Google Chrome"
    tell active tab of front window
        set URL to "{url}"
    end tell
end tell''')


def execute_js_file(js_code):
    js_file = os.path.join(EVENTS_DIR, "_tmp.js")
    with open(js_file, "w") as f:
        f.write(js_code)
    result = run_osascript(f'''set jsCode to do shell script "cat {js_file}"
tell application "Google Chrome"
    tell active tab of front window
        execute javascript jsCode
    end tell
end tell''')
    return result


def wait_for_table(max_wait=10):
    script = '''tell application "Google Chrome"
    tell active tab of front window
        execute javascript "document.querySelector('table tbody tr') ? 'yes' : 'no'"
    end tell
end tell'''
    for _ in range(max_wait):
        if run_osascript(script) == "yes":
            return True
        time.sleep(1)
    return False


def wait_for_event_page(max_wait=10):
    script = '''tell application "Google Chrome"
    tell active tab of front window
        execute javascript "document.body.innerText.includes('Event #') ? 'yes' : 'no'"
    end tell
end tell'''
    for _ in range(max_wait):
        if run_osascript(script) == "yes":
            return True
        time.sleep(1)
    return False


def main():
    open(LOG_FILE, "w").close()
    log("=" * 50)
    log("Backing up Events Report")
    log("=" * 50)

    # Phase 1: Collect all events from list pages
    all_events = []
    stats = {}
    total_pages = 36  # 717 events / 20 per page

    log(f"\nPhase 1: Scraping {total_pages} pages of event listings...")

    for page in range(1, total_pages + 1):
        url = f"https://superhivemarket.com/creator/reports/events?page={page}"
        navigate_to(url)
        time.sleep(2)

        if not wait_for_table():
            log(f"  Page {page}: table not found, retrying...")
            time.sleep(3)
            if not wait_for_table(5):
                log(f"  Page {page}: SKIPPED")
                continue

        result = execute_js_file(EXTRACT_LIST_JS)
        if not result:
            log(f"  Page {page}: no data")
            continue

        try:
            data = json.loads(result)
            events = data.get("events", [])
            all_events.extend(events)

            if page == 1:
                stats = data.get("stats", {})

            log(f"  Page {page}/{total_pages}: {len(events)} events (total so far: {len(all_events)})")
        except json.JSONDecodeError:
            log(f"  Page {page}: JSON parse error")

    log(f"\nCollected {len(all_events)} events from list pages")

    # Save list data immediately as CSV
    csv_file = os.path.join(EVENTS_DIR, "events_list.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Created", "Event", "Product ID", "Event ID"])
        for ev in all_events:
            writer.writerow([ev["created"], ev["event"], ev["productId"], ev["eventId"]])
    log(f"Saved events_list.csv ({len(all_events)} rows)")

    # Save stats
    stats_file = os.path.join(EVENTS_DIR, "summary_stats.json")
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    log(f"Saved summary_stats.json")

    # Phase 2: Fetch View Event details for each event
    log(f"\nPhase 2: Fetching {len(all_events)} event details...")
    event_details = []

    for idx, ev in enumerate(all_events):
        eid = ev.get("eventId", "")
        if not eid:
            event_details.append({
                "Event ID": "", "Event Type": ev["event"],
                "Created": ev["created"], "Product ID": ev["productId"]
            })
            continue

        if (idx + 1) % 20 == 0 or idx == 0:
            log(f"  [{idx+1}/{len(all_events)}] Fetching event details...")

        url = f"https://superhivemarket.com/creator/reports/events/{eid}"
        navigate_to(url)
        time.sleep(1.5)

        if not wait_for_event_page(8):
            # Fallback: use list data
            event_details.append({
                "Event ID": eid, "Event Type": ev["event"],
                "Created": ev["created"], "Product ID": ev["productId"],
                "Referrer": "", "Affiliate": "", "Landing Page": "",
                "Browser": "", "OS": "", "Device Type": "",
                "Region": "", "City": "", "Country": "",
                "UTM Campaign": "", "UTM Source": "", "UTM Medium": "",
                "UTM Term": "", "UTM Content": ""
            })
            continue

        result = execute_js_file(EXTRACT_DETAIL_JS)
        if result:
            try:
                detail = json.loads(result)
                event_details.append(detail)
            except json.JSONDecodeError:
                event_details.append({
                    "Event ID": eid, "Event Type": ev["event"],
                    "Created": ev["created"], "Product ID": ev["productId"]
                })
        else:
            event_details.append({
                "Event ID": eid, "Event Type": ev["event"],
                "Created": ev["created"], "Product ID": ev["productId"]
            })

    # Save detailed CSV
    detail_csv = os.path.join(EVENTS_DIR, "events_detailed.csv")
    fieldnames = ["Event ID", "Event Type", "Created", "Product ID", "Referrer",
                  "Affiliate", "Landing Page", "Browser", "OS", "Device Type",
                  "Region", "City", "Country",
                  "UTM Campaign", "UTM Source", "UTM Medium", "UTM Term", "UTM Content"]

    with open(detail_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for d in event_details:
            writer.writerow(d)
    log(f"Saved events_detailed.csv ({len(event_details)} rows)")

    # Save as JSON too
    detail_json = os.path.join(EVENTS_DIR, "events_detailed.json")
    with open(detail_json, "w") as f:
        json.dump(event_details, f, indent=2, ensure_ascii=False)
    log(f"Saved events_detailed.json")

    # Build summary HTML
    build_summary_html(stats, all_events, event_details)

    log("")
    log("=" * 50)
    log("Events backup complete!")
    log(f"Location: {EVENTS_DIR}")
    log("=" * 50)


def build_summary_html(stats, events, details):
    """Build a nice HTML summary of all events."""

    # Count by type
    type_counts = {}
    for ev in events:
        t = ev.get("event", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    # Count by product
    product_counts = {}
    for ev in events:
        pid = ev.get("productId", "Unknown")
        product_counts[pid] = product_counts.get(pid, 0) + 1
    top_products = sorted(product_counts.items(), key=lambda x: -x[1])[:20]

    # Browser/OS/Device stats from details
    browsers = {}
    oses = {}
    devices = {}
    countries = {}
    referrers_detail = {}
    for d in details:
        b = d.get("Browser", "").strip()
        if b: browsers[b] = browsers.get(b, 0) + 1
        o = d.get("OS", "").strip()
        if o: oses[o] = oses.get(o, 0) + 1
        dv = d.get("Device Type", "").strip()
        if dv: devices[dv] = devices.get(dv, 0) + 1
        c = d.get("Country", "").strip()
        if c: countries[c] = countries.get(c, 0) + 1
        r = d.get("Referrer", "").strip()
        if r: referrers_detail[r] = referrers_detail.get(r, 0) + 1

    def stat_table(data, limit=15):
        items = sorted(data.items(), key=lambda x: -x[1])[:limit]
        rows = ""
        for k, v in items:
            rows += f"<tr><td>{k}</td><td>{v}</td></tr>\n"
        return rows

    # Events table rows
    events_rows = ""
    for i, d in enumerate(details):
        eid = d.get("Event ID", "")
        etype = d.get("Event Type", "")
        created = d.get("Created", "")
        pid = d.get("Product ID", "")
        ref = d.get("Referrer", "")
        browser = d.get("Browser", "")
        os_name = d.get("OS", "")
        device = d.get("Device Type", "")
        country = d.get("Country", "")

        type_class = ""
        if "Cart" in etype: type_class = "type-cart"
        elif "Checkout" in etype: type_class = "type-checkout"
        elif "Purchased" in etype: type_class = "type-purchased"

        events_rows += f"""<tr>
<td>{eid}</td><td class="{type_class}">{etype}</td><td>{created}</td>
<td>{pid}</td><td class="ref-cell">{ref}</td>
<td>{browser}</td><td>{os_name}</td><td>{device}</td><td>{country}</td>
</tr>\n"""

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Events Report Backup</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0d1117;color:#c9d1d9;}}
.container{{max-width:1400px;margin:0 auto;padding:20px;}}
h1{{color:#f0f6fc;margin-bottom:4px;}}
h2{{color:#f0f6fc;margin:30px 0 12px;font-size:1.2em;}}
.subtitle{{color:#8b949e;margin-bottom:20px;}}
.stats-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:30px;}}
.stat-card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;text-align:center;}}
.stat-num{{font-size:2em;color:#58a6ff;font-weight:700;}}
.stat-label{{color:#8b949e;font-size:.85em;margin-top:4px;}}
.stat-pct{{color:#3fb950;font-size:.9em;}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
.grid-3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px;}}
table{{width:100%;border-collapse:collapse;font-size:.85em;}}
th{{background:#161b22;color:#8b949e;text-align:left;padding:8px;border-bottom:1px solid #30363d;position:sticky;top:0;}}
td{{padding:6px 8px;border-bottom:1px solid #21262d;}}
tr:hover{{background:#161b22;}}
.type-cart{{color:#d29922;}}
.type-checkout{{color:#f0883e;}}
.type-purchased{{color:#3fb950;font-weight:600;}}
.ref-cell{{max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.mini-table td,.mini-table th{{padding:4px 8px;}}
.search{{margin:12px 0;}}
.search input{{background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:8px 12px;border-radius:6px;width:300px;}}
footer{{margin-top:30px;padding:16px;border-top:1px solid #30363d;color:#8b949e;font-size:.85em;text-align:center;}}
</style>
</head><body>
<div class="container">
<h1>Events Report</h1>
<p class="subtitle">{stats.get('totalEvents','717')} total events | Backed up {time.strftime('%Y-%m-%d %H:%M')}</p>

<div class="stats-grid">
  <div class="stat-card"><div class="stat-num">{stats.get('productViews','--')}</div><div class="stat-label">Product Views</div></div>
  <div class="stat-card"><div class="stat-num">{stats.get('addedToCart','--')}</div><div class="stat-label">Added to Cart</div></div>
  <div class="stat-card"><div class="stat-num">{stats.get('reachedCheckout','--')}</div><div class="stat-label">Reached Checkout</div></div>
  <div class="stat-card"><div class="stat-num">{stats.get('purchased','--')}</div><div class="stat-label">Purchased</div></div>
  <div class="stat-card"><div class="stat-num">{stats.get('conversionRate','--')}</div><div class="stat-label">Conversion Rate</div></div>
</div>

<div class="grid-3">
  <div class="card"><h2>Top Products</h2><table class="mini-table"><tr><th>Product ID</th><th>Events</th></tr>
  {stat_table(dict(top_products), 20)}</table></div>
  <div class="card"><h2>Browsers</h2><table class="mini-table"><tr><th>Browser</th><th>Count</th></tr>
  {stat_table(browsers)}</table></div>
  <div class="card"><h2>Operating Systems</h2><table class="mini-table"><tr><th>OS</th><th>Count</th></tr>
  {stat_table(oses)}</table></div>
</div>

<div class="grid-3">
  <div class="card"><h2>Device Types</h2><table class="mini-table"><tr><th>Device</th><th>Count</th></tr>
  {stat_table(devices)}</table></div>
  <div class="card"><h2>Countries</h2><table class="mini-table"><tr><th>Country</th><th>Count</th></tr>
  {stat_table(countries)}</table></div>
  <div class="card"><h2>Top Referrers</h2><table class="mini-table"><tr><th>Referrer</th><th>Count</th></tr>
  {stat_table(referrers_detail)}</table></div>
</div>

<h2>All Events ({len(details)})</h2>
<div class="search"><input type="text" id="searchBox" placeholder="Filter events..." oninput="filterTable()"></div>
<div style="overflow-x:auto;">
<table id="eventsTable">
<thead><tr><th>Event ID</th><th>Type</th><th>Created</th><th>Product</th><th>Referrer</th><th>Browser</th><th>OS</th><th>Device</th><th>Country</th></tr></thead>
<tbody>
{events_rows}
</tbody>
</table>
</div>

<footer>Backup from Superhive (Blender Market) Creator Dashboard - Events Report</footer>
</div>
<script>
function filterTable(){{
  var q=document.getElementById('searchBox').value.toLowerCase();
  var rows=document.querySelectorAll('#eventsTable tbody tr');
  rows.forEach(function(r){{r.style.display=r.innerText.toLowerCase().includes(q)?'':'none';}});
}}
</script>
</body></html>"""

    with open(os.path.join(EVENTS_DIR, "events_report.html"), "w") as f:
        f.write(html)
    log("Saved events_report.html")


if __name__ == "__main__":
    main()
