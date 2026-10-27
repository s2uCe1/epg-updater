import gzip
import io
import os
import re
import time
import datetime
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from channel_map import CHANNEL_MAPPING  # Imports your offline channel map

# Complete list of EPG sources (Open-EPG + EPGShare01 + EPG.lat)
URLS = [
    # EPGShare01 Regional & Master Feeds
    "https://epgshare01.online/epgshare01/epg_ripper_AL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AT1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_BA1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_HR1.xml.gz",  # Auto-fixed from .txt to .xml.gz
    "https://epgshare01.online/epgshare01/epg_ripper_MN1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_NZ1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_RS1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SA1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SA2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz",

    # EPG.lat Regional Feeds
    "https://epg.lat/files/al.xml.gz",
    "https://epg.lat/files/dz.xml.gz",
    "https://epg.lat/files/au.xml.gz",
    "https://epg.lat/files/ba.xml.gz",
    "https://epg.lat/files/hr.xml.gz",
    "https://epg.lat/files/eg.xml.gz",
    "https://epg.lat/files/sa.xml.gz",
    "https://epg.lat/files/ae.xml.gz",

    # Open-EPG Country & Category Feeds
    "https://www.open-epg.com/files/albania.xml.gz",
    "https://www.open-epg.com/files/argentina.xml.gz",
    "https://www.open-epg.com/files/australia.xml.gz",
    "https://www.open-epg.com/files/austria.xml.gz",
    "https://www.open-epg.com/files/belgium.xml.gz",
    "https://www.open-epg.com/files/bosnia.xml.gz",
    "https://www.open-epg.com/files/brazil1.xml.gz",
    "https://www.open-epg.com/files/bulgaria1.xml.gz",
    "https://www.open-epg.com/files/bulgaria2.xml.gz",
    "https://www.open-epg.com/files/canada1.xml.gz",
    "https://www.open-epg.com/files/canada2.xml.gz",
    "https://www.open-epg.com/files/croatia.xml.gz",
    "https://www.open-epg.com/files/czech1.xml.gz",
    "https://www.open-epg.com/files/denmark.xml.gz",
    "https://www.open-epg.com/files/egypt1.xml.gz",
    "https://www.open-epg.com/files/egypt2.xml.gz",
    "https://www.open-epg.com/files/finland.xml.gz",
    "https://www.open-epg.com/files/france1.xml.gz",
    "https://www.open-epg.com/files/france2.xml.gz",
    "https://www.open-epg.com/files/germany.xml.gz",
    "https://www.open-epg.com/files/greece.xml.gz",
    "https://www.open-epg.com/files/hungary1.xml.gz",
    "https://www.open-epg.com/files/india1.xml.gz",
    "https://www.open-epg.com/files/ireland.xml.gz",
    "https://www.open-epg.com/files/israel.xml.gz",
    "https://www.open-epg.com/files/italy1.xml.gz",
    "https://www.open-epg.com/files/italy2.xml.gz",
    "https://www.open-epg.com/files/italy3.xml.gz",
    "https://www.open-epg.com/files/italy4.xml.gz",
    "https://www.open-epg.com/files/latvia.xml.gz",
    "https://www.open-epg.com/files/lithuania.xml.gz",
    "https://www.open-epg.com/files/macedonia1.xml.gz",
    "https://www.open-epg.com/files/mexico1.xml.gz",
    "https://www.open-epg.com/files/montenegro1.xml.gz",
    "https://www.open-epg.com/files/morocco1.xml.gz",
    "https://www.open-epg.com/files/netherlands.xml.gz",
    "https://www.open-epg.com/files/newzealand.xml.gz",
    "https://www.open-epg.com/files/norway.xml.gz",
    "https://www.open-epg.com/files/poland1.xml.gz",
    "https://www.open-epg.com/files/poland2.xml.gz",
    "https://www.open-epg.com/files/portugal1.xml.gz",
    "https://www.open-epg.com/files/qatar1.xml.gz",
    "https://www.open-epg.com/files/qatar2.xml.gz",
    "https://www.open-epg.com/files/qatar3.xml.gz",
    "https://www.open-epg.com/files/qatar4.xml.gz",
    "https://www.open-epg.com/files/qatar5.xml.gz",
    "https://www.open-epg.com/files/qatar6.xml.gz",
    "https://www.open-epg.com/files/romania1.xml.gz",
    "https://www.open-epg.com/files/russia.xml.gz",
    "https://www.open-epg.com/files/saudiarabia1.xml.gz",
    "https://www.open-epg.com/files/saudiarabia2.xml.gz",
    "https://www.open-epg.com/files/saudiarabia3.xml.gz",
    "https://www.open-epg.com/files/saudiarabia4.xml.gz",
    "https://www.open-epg.com/files/saudiarabia5.xml.gz",
    "https://www.open-epg.com/files/saudiarabia6.xml.gz",
    "https://www.open-epg.com/files/serbia1.xml.gz",
    "https://www.open-epg.com/files/serbia2.xml.gz",
    "https://www.open-epg.com/files/serbia4.xml.gz",
    "https://www.open-epg.com/files/serbia5.xml.gz",
    "https://www.open-epg.com/files/slovakia.xml.gz",
    "https://www.open-epg.com/files/slovenia.xml.gz",
    "https://www.open-epg.com/files/southafrica1.xml.gz",
    "https://www.open-epg.com/files/spain1.xml.gz",
    "https://www.open-epg.com/files/sports1.xml.gz",
    "https://www.open-epg.com/files/sports2.xml.gz",
    "https://www.open-epg.com/files/sports3.xml.gz",
    "https://www.open-epg.com/files/sports4.xml.gz",
    "https://www.open-epg.com/files/sweden.xml.gz",
    "https://www.open-epg.com/files/switzerland.xml.gz",
    "https://www.open-epg.com/files/turkey1.xml.gz",
    "https://www.open-epg.com/files/turkey2.xml.gz",
    "https://www.open-epg.com/files/uae1.xml.gz",
    "https://www.open-epg.com/files/uae2.xml.gz",
    "https://www.open-epg.com/files/uae3.xml.gz",
    "https://www.open-epg.com/files/uae4.xml.gz",
    "https://www.open-epg.com/files/uae5.xml.gz",
    "https://www.open-epg.com/files/uae6.xml.gz",
    "https://www.open-epg.com/files/ukraine.xml.gz",
    "https://www.open-epg.com/files/unitedkingdom.xml.gz",
    "https://www.open-epg.com/files/unitedstates1.xml.gz",
    "https://www.open-epg.com/files/unitedstates2.xml.gz",
    "https://www.open-epg.com/files/unitedstates3.xml.gz",
    "https://www.open-epg.com/files/unitedstates4.xml.gz",
    "https://www.open-epg.com/files/unitedstates5.xml.gz",
    "https://www.open-epg.com/files/unitedstates6.xml.gz",
    "https://www.open-epg.com/files/unitedstates7.xml.gz",
    "https://www.open-epg.com/files/unitedstates8.xml.gz",
    "https://www.open-epg.com/files/unitedstates9.xml.gz",
    "https://www.open-epg.com/files/unitedstates10.xml.gz",
    "https://www.open-epg.com/files/unitedstates11.xml.gz",
]

OUTPUT_FILE = "combined_epg.xml.gz"
PLAYLIST_FILE = "playlist.m3u"  # Optional: if present, auto-detects 24/7 VOD channels
DUMMY_TITLE = "."               # Single dot for 24/7 VOD dummy programming
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# -------------------------------------------------------------------------
# 1. BUILD SMART LOOKUP TABLES FROM CHANNEL_MAPPING
# -------------------------------------------------------------------------
# Group all playlist keys/aliases by their target EPG ID (case-insensitive)
epg_to_aliases = {}
canonical_epg_id = {}
dummy_vod_channels = set()

VOD_KEYWORDS = re.compile(r"\b(24/7|24-7|vod|loop|nonstop|non-stop)\b", re.IGNORECASE)

for playlist_key, epg_id in CHANNEL_MAPPING.items():
    if not epg_id:
        continue
    # Check if this entry is a 24/7 / Dummy channel in channel_map.py
    if epg_id.upper() in ("DUMMY", "24/7", ".") or VOD_KEYWORDS.search(playlist_key) or "dummy" in epg_id.lower():
        dummy_vod_channels.add(playlist_key)
        if epg_id.upper() not in ("DUMMY", "24/7", "."):
            dummy_vod_channels.add(epg_id)
        continue

    epg_low = epg_id.lower()
    if epg_low not in epg_to_aliases:
        epg_to_aliases[epg_low] = []
        canonical_epg_id[epg_low] = epg_id  # Keep exact original EPG ID casing
    if playlist_key not in epg_to_aliases[epg_low]:
        epg_to_aliases[epg_low].append(playlist_key)

# Optional: Also scan local playlist.m3u if available in repo to catch 24/7 VOD streams automatically
if os.path.exists(PLAYLIST_FILE):
    try:
        with open(PLAYLIST_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#EXTINF"):
                    group_m = re.search(r'group-title="([^"]*)"', line)
                    tvgid_m = re.search(r'tvg-id="([^"]*)"', line)
                    name_m = line.rsplit(",", 1)
                    ch_name = name_m[1].strip() if len(name_m) > 1 else ""
                    grp = group_m.group(1).strip() if group_m else ""
                    tid = tvgid_m.group(1).strip() if tvgid_m else ""

                    if VOD_KEYWORDS.search(grp) or VOD_KEYWORDS.search(ch_name):
                        if tid:
                            dummy_vod_channels.add(tid)
                        if ch_name:
                            dummy_vod_channels.add(ch_name)
                        if grp and ch_name:
                            dummy_vod_channels.add(f"[{grp}] {ch_name}")
    except Exception as e:
        print(f"Note: Could not scan {PLAYLIST_FILE} for 24/7 VODs: {e}")

target_epg_ids = set(epg_to_aliases.keys())
print(f"Loaded {len(target_epg_ids)} unique target EPG IDs ({len(CHANNEL_MAPPING)} total mapped keys).")
print(f"Detected {len(dummy_vod_channels)} 24/7 VOD / Dummy channel identifiers.")

# Time window: 24h past to 48h future
now = datetime.datetime.now(datetime.timezone.utc)
min_time = (now - datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")
max_time = (now + datetime.timedelta(days=2)).strftime("%Y%m%d%H%M%S")


# -------------------------------------------------------------------------
# 2. CONCURRENT STREAMING FETCHER & PARSER
# -------------------------------------------------------------------------
def fetch_and_parse(idx, total, url):
    # Auto-correct accidental .txt extension on epgshare01 XML feeds
    if url.endswith(".txt") and "epgshare01" in url:
        url = url[:-4] + ".xml.gz"

    feed_name = url.split("/")[-1]
    local_channels = {}
    local_programmes = []

    try:
        res = requests.get(url, headers=HEADERS, timeout=60)
        if res.status_code != 200:
            print(f"[{idx}/{total}] Skipped {feed_name} (HTTP {res.status_code})")
            return local_channels, local_programmes

        # Support both .gz compressed and plain XML feeds
        content_bytes = res.content
        if url.endswith(".gz") or content_bytes[:2] == b"\x1f\x8b":
            stream = gzip.GzipFile(fileobj=io.BytesIO(content_bytes))
        else:
            stream = io.BytesIO(content_bytes)

        with stream as xml_file:
            for event, elem in ET.iterparse(xml_file, events=("end",)):
                if elem.tag == "channel":
                    cid = elem.get("id")
                    if cid and cid.lower() in target_epg_ids:
                        cid_low = cid.lower()
                        if cid_low not in local_channels:
                            # Keep canonical target EPG ID
                            true_id = canonical_epg_id[cid_low]
                            elem.set("id", true_id)

                            # Add all mapped keys (Group-scoped, Flat name, src tags) as <display-name>
                            # so TiviMate / m3u4u matches by ID OR by Name automatically
                            existing_names = {
                                dn.text.strip() for dn in elem.findall("display-name") if dn.text
                            }
                            for alias in epg_to_aliases[cid_low]:
                                if alias not in existing_names:
                                    dn_elem = ET.SubElement(elem, "display-name")
                                    dn_elem.text = alias
                                    existing_names.add(alias)

                            local_channels[cid_low] = ET.tostring(elem, encoding="unicode")
                    elem.clear()

                elif elem.tag == "programme":
                    ch_ref = elem.get("channel")
                    if ch_ref and ch_ref.lower() in target_epg_ids:
                        start = elem.get("start", "")[:14]
                        if min_time <= start <= max_time:
                            ch_low = ch_ref.lower()
                            true_id = canonical_epg_id[ch_low]
                            elem.set("channel", true_id)

                            # Strip heavy descriptions to keep combined_epg.xml.gz fast & lightweight
                            for desc in elem.findall("desc"):
                                elem.remove(desc)

                            dedup_key = (true_id, start)
                            local_programmes.append((dedup_key, ET.tostring(elem, encoding="unicode")))
                    elem.clear()

        print(f"[{idx}/{total}] Done {feed_name}: +{len(local_channels)} ch, +{len(local_programmes)} prog")
    except Exception as e:
        print(f"[{idx}/{total}] Error fetching {feed_name}: {e}")

    return local_channels, local_programmes


channels_dict = {}
programmes_dict = {}

# Download using 6 worker threads for high speed without hitting rate limits
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [
        executor.submit(fetch_and_parse, idx, len(URLS), url)
        for idx, url in enumerate(URLS, 1)
    ]
    for future in as_completed(futures):
        ch_res, pr_res = future.result()
        for k, v in ch_res.items():
            if k not in channels_dict:
                channels_dict[k] = v
        for dedup_key, pr_xml in pr_res:
            if dedup_key not in programmes_dict:
                programmes_dict[dedup_key] = pr_xml


# -------------------------------------------------------------------------
# 3. GENERATE 24/7 VOD DUMMY PROGRAMMING (TITLE = ".")
# -------------------------------------------------------------------------
# Also generate dummy schedule for any target channel that had 0 programmes found
matched_true_ids = {canonical_epg_id[k] for k in channels_dict}
channels_with_progs = {dedup_key[0] for dedup_key in programmes_dict}

# Combine explicit 24/7 VOD channels + any mapped channel missing programme data
all_dummy_targets = set(dummy_vod_channels) | (matched_true_ids - channels_with_progs)

dummy_channels_xml = []
dummy_programmes_xml = []

if all_dummy_targets:
    # Build 6-hour dummy blocks from -24h to +48h
    start_base = (now - datetime.timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
    time_slots = []
    for block in range(12):  # 12 blocks * 6 hours = 72 hours total coverage
        b_start = start_base + datetime.timedelta(hours=block * 6)
        b_stop = b_start + datetime.timedelta(hours=6)
        time_slots.append((
            b_start.strftime("%Y%m%d%H%M%S +0000"),
            b_stop.strftime("%Y%m%d%H%M%S +0000")
        ))

    for d_id in sorted(all_dummy_targets):
        if d_id.lower() not in channels_dict:
            ch_el = ET.Element("channel", id=d_id)
            dn_el = ET.SubElement(ch_el, "display-name")
            dn_el.text = d_id
            dummy_channels_xml.append(ET.tostring(ch_el, encoding="unicode"))

        for s_str, e_str in time_slots:
            pr_el = ET.Element("programme", start=s_str, stop=e_str, channel=d_id)
            t_el = ET.SubElement(pr_el, "title")
            t_el.text = DUMMY_TITLE  # Single "." as requested
            dummy_programmes_xml.append(ET.tostring(pr_el, encoding="unicode"))

print(
    f"\nSummary: {len(channels_dict)} EPG Channels | "
    f"{len(programmes_dict)} Unique Programmes | "
    f"{len(all_dummy_targets)} Dummy/VOD Channels filled with '{DUMMY_TITLE}'"
)

# -------------------------------------------------------------------------
# 4. WRITE COMPRESSED XMLTV OUTPUT
# -------------------------------------------------------------------------
print(f"Writing {OUTPUT_FILE}...")
with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8", compresslevel=9) as gz_out:
    gz_out.write('<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="smart-epg-combiner">\n')
    for ch_xml in channels_dict.values():
        gz_out.write("  " + ch_xml.strip() + "\n")
    for d_ch_xml in dummy_channels_xml:
        gz_out.write("  " + d_ch_xml.strip() + "\n")
    for pr_xml in programmes_dict.values():
        gz_out.write("  " + pr_xml.strip() + "\n")
    for d_pr_xml in dummy_programmes_xml:
        gz_out.write("  " + d_pr_xml.strip() + "\n")
    gz_out.write("</tv>\n")

print("Finished successfully!")