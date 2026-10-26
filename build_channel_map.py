import glob
import re
import gzip
import io
import datetime
import xml.etree.ElementTree as ET
import requests

URLS = [
    "https://www.open-epg.com/files/albania.xml.gz",
    "https://www.open-epg.com/files/australia.xml.gz",
    "https://www.open-epg.com/files/austria.xml.gz",
    "https://www.open-epg.com/files/bosnia.xml.gz",
    "https://www.open-epg.com/files/bulgaria2.xml.gz",
    "https://www.open-epg.com/files/croatia.xml.gz",
    "https://www.open-epg.com/files/egypt1.xml.gz",
    "https://www.open-epg.com/files/egypt2.xml.gz",
    "https://www.open-epg.com/files/germany.xml.gz",
    "https://www.open-epg.com/files/hungary1.xml.gz",
    "https://www.open-epg.com/files/italy4.xml.gz",
    "https://www.open-epg.com/files/macedonia1.xml.gz",
    "https://www.open-epg.com/files/montenegro1.xml.gz",
    "https://www.open-epg.com/files/morocco1.xml.gz",
    "https://www.open-epg.com/files/newzealand.xml.gz",
    "https://www.open-epg.com/files/qatar1.xml.gz",
    "https://www.open-epg.com/files/qatar2.xml.gz",
    "https://www.open-epg.com/files/qatar3.xml.gz",
    "https://www.open-epg.com/files/qatar4.xml.gz",
    "https://www.open-epg.com/files/qatar5.xml.gz",
    "https://www.open-epg.com/files/qatar6.xml.gz",
    "https://www.open-epg.com/files/russia.xml.gz",
    "https://www.open-epg.com/files/saudiarabia1.xml.gz",
    "https://www.open-epg.com/files/saudiarabia2.xml.gz",
    "https://www.open-epg.com/files/saudiarabia4.xml.gz",
    "https://www.open-epg.com/files/saudiarabia3.xml.gz",
    "https://www.open-epg.com/files/saudiarabia5.xml.gz",
    "https://www.open-epg.com/files/saudiarabia6.xml.gz",
    "https://www.open-epg.com/files/serbia1.xml.gz",
    "https://www.open-epg.com/files/serbia2.xml.gz",
    "https://www.open-epg.com/files/serbia4.xml.gz",
    "https://www.open-epg.com/files/serbia5.xml.gz",
    "https://www.open-epg.com/files/slovenia.xml.gz",
    "https://www.open-epg.com/files/sports1.xml.gz",
    "https://www.open-epg.com/files/sports4.xml.gz",
    "https://www.open-epg.com/files/turkey2.xml.gz",
    "https://www.open-epg.com/files/uae6.xml.gz",
    "https://www.open-epg.com/files/unitedkingdom.xml.gz",
    "https://www.open-epg.com/files/unitedstates10.xml.gz",
    "https://www.open-epg.com/files/unitedstates11.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_HR1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SA1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SA2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SPORTKLUB1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_BEIN1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_BA1.xml.gz",
]

ARABIC_SUFFIXES = (".sa", ".qa", ".eg", ".ae", ".ma", ".ps")
BALKAN_SUFFIXES = (".hr", ".rs", ".ba", ".me", ".si")

GROUP_QUARANTINE = {
    "hrvatska - sport": BALKAN_SUFFIXES,
    "hrvatska": BALKAN_SUFFIXES,
    "slovenia": BALKAN_SUFFIXES,
    "bosna i hercegovina": BALKAN_SUFFIXES,
    "crna gora": BALKAN_SUFFIXES,
    "srbija - sport": BALKAN_SUFFIXES,
    "srbija": BALKAN_SUFFIXES,
    "austria - sport": (".at",),
    "austria": (".at",),
    "germany": (".de",),
    "albania": (".al",),
    "macedonia": (".mk",),
    "czech": (".cz",),
    "bulgaria": (".bg",),
    "hungary": (".hu",),
    "italy": (".it",),
    "russia": (".ru",),
    "turkey": (".tr",),
    "baltic": (".ee", ".lv", ".lt"),
    "united kingdom": (".uk",),
    "united states": (".us",),
    "arabic": ARABIC_SUFFIXES,
}

m3u_files = glob.glob("*.m3u*")
if not m3u_files:
    raise FileNotFoundError("No .m3u file found in directory!")
m3u_path = m3u_files[0]
print(f"Loading playlist: {m3u_path}")

def clean(text):
    if not text:
        return ""
    text = re.sub(r'\(src\d+\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(m3u4u\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    text = re.sub(r'\b(fhd|uhd|hevc|4k|raw|sd|h\.265|1080p|720p|hd)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^[A-Z]{2,4}\s*[:|]\s*', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return " ".join(text.lower().split())

def strip_suffix(cid):
    return re.sub(r'\.[a-z]{2,3}$', '', cid, flags=re.IGNORECASE)

def extract_src_id(raw_text):
    m = re.search(r'([a-zA-Z0-9._+-]+)\s*\((?:src\d+|m3u4u)\)', raw_text, re.IGNORECASE)
    return m.group(1).strip() if m else None

now = datetime.datetime.now(datetime.timezone.utc)
min_time = (now - datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")
max_time = (now + datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")

print(f"Downloading and indexing feeds from {len(URLS)} sources...")
headers = {"User-Agent": "Mozilla/5.0"}

channels_with_data = set()
raw_channels = {}
all_cids_lower = {}

for idx, u in enumerate(URLS, 1):
    fname = u.split("/")[-1]
    print(f"[{idx}/{len(URLS)}] Fetching {fname}...")
    try:
        r = requests.get(u, headers=headers, timeout=45)
        if r.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as gz:
                tree = ET.parse(gz)
                root = tree.getroot()
                
                for ch in root.findall("channel"):
                    cid = ch.get("id")
                    if cid and cid not in raw_channels:
                        dns = [clean(d.text) for d in ch.findall("display-name") if d.text]
                        c_id_base = clean(strip_suffix(cid))
                        raw_channels[cid] = (c_id_base, dns)
                        all_cids_lower[cid.lower()] = cid

                for pr in root.findall("programme"):
                    start = pr.get("start", "")[:14]
                    if min_time <= start <= max_time:
                        ch_ref = pr.get("channel")
                        if ch_ref:
                            channels_with_data.add(ch_ref.lower())
    except Exception as e:
        print(f"Error reading {fname}: {e}")

print(f"Indexing complete. Verified {len(channels_with_data)} active data feeds.\n")

indexed_by_group = {grp: [] for grp in GROUP_QUARANTINE}
for cid, (clean_cid_base, clean_dns) in raw_channels.items():
    cid_low = cid.lower()
    if cid_low not in channels_with_data:
        continue
    for grp, suffixes in GROUP_QUARANTINE.items():
        if cid_low.endswith(suffixes):
            indexed_by_group[grp].append((cid, clean_cid_base, clean_dns))

matches = {}
unmatched_list = []
total_count = 0

print("Sweeping through all playlist channels with deep substring & token fallback...")
with open(m3u_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line.startswith("#EXTINF"):
            continue
        total_count += 1

        grp_match = re.search(r'group-title="([^"]+)"', line, re.IGNORECASE)
        grp = grp_match.group(1).strip().lower() if grp_match else ""

        tvg_match = re.search(r'tvg-id="([^"]+)"', line)
        tvg_id = tvg_match.group(1).strip() if tvg_match else ""
        raw_name = line.split(",", 1)[-1].strip() if "," in line else ""

        if tvg_id.upper() == "NULL":
            tvg_id = ""

        target_rule = None
        for rule_key in GROUP_QUARANTINE:
            if rule_key in grp:
                target_rule = rule_key
                break

        if not target_rule:
            continue

        allowed_suffixes = GROUP_QUARANTINE[target_rule]
        candidates = indexed_by_group[target_rule]
        matched_cid = None

        # Priority 1: Extracted src ID check
        src_id = extract_src_id(tvg_id) or extract_src_id(raw_name)
        if src_id and src_id.lower() in all_cids_lower:
            candidate_cid = all_cids_lower[src_id.lower()]
            if candidate_cid.lower().endswith(allowed_suffixes) and candidate_cid.lower() in channels_with_data:
                matched_cid = candidate_cid

        # Priority 2: Direct tvg-id check
        if not matched_cid and tvg_id and tvg_id.lower() in all_cids_lower:
            candidate_cid = all_cids_lower[tvg_id.lower()]
            if candidate_cid.lower().endswith(allowed_suffixes) and candidate_cid.lower() in channels_with_data:
                matched_cid = candidate_cid

        # Priority 3: Clean name comparison inside regional candidates
        if not matched_cid:
            c_name = clean(raw_name)
            c_tvg = clean(strip_suffix(tvg_id))

            for cid, clean_cid_base, clean_dns in candidates:
                if c_name and (c_name == clean_cid_base or c_name in clean_dns):
                    matched_cid = cid
                    break
                if c_tvg and (c_tvg == clean_cid_base or c_tvg in clean_dns):
                    matched_cid = cid
                    break

        # Priority 4: Token/Keyword Overlap Fallback Matcher
        if not matched_cid:
            c_name_tokens = set(clean(raw_name).split())
            c_name_tokens.discard("tv")
            c_name_tokens.discard("hd")
            c_name_tokens.discard("fhd")
            
            if c_name_tokens:
                best_match = None
                max_overlap = 0
                for cid, clean_cid_base, clean_dns in candidates:
                    base_tokens = set(clean_cid_base.split())
                    overlap = len(c_name_tokens.intersection(base_tokens))
                    if overlap > max_overlap and overlap >= len(c_name_tokens) * 0.5:
                        max_overlap = overlap
                        best_match = cid
                if best_match:
                    matched_cid = best_match

        # Priority 5: Substring Containment Fallback Matcher
        if not matched_cid:
            c_name_clean = clean(raw_name)
            if len(c_name_clean) > 3:
                for cid, clean_cid_base, clean_dns in candidates:
                    if c_name_clean in clean_cid_base or clean_cid_base in c_name_clean:
                        matched_cid = cid
                        break
                    found_sub = False
                    for dn in clean_dns:
                        if c_name_clean in dn or dn in c_name_clean:
                            matched_cid = cid
                            found_sub = True
                            break
                    if found_sub:
                        break

        if matched_cid:
            if tvg_id and tvg_id not in matches:
                matches[tvg_id] = matched_cid
            if raw_name and raw_name not in matches:
                matches[raw_name] = matched_cid
        else:
            if raw_name and raw_name not in unmatched_list:
                unmatched_list.append(f"[{grp.upper()}] {raw_name}")

print(f"\nScan Summary:")
print(f"Total scanned playlist entries: {total_count}")
print(f"Successfully auto-mapped: {len(matches)}")
print(f"Unmatched channels logged: {len(unmatched_list)}")

# Save outputs
with open("channel_map.py", "w", encoding="utf-8") as out:
    out.write("# Auto-generated strictly isolated & data-verified channel mappings\n")
    out.write("CHANNEL_MAPPING = {\n")
    for k, v in matches.items():
        escaped_k = k.replace('\\', '\\\\').replace('"', '\\"')
        out.write(f'    "{escaped_k}": "{v}",\n')
    out.write("}\n")

with open("unmatched_channels.txt", "w", encoding="utf-8") as un_out:
    un_out.write("\n".join(unmatched_list))

print("Saved updated channel_map.py and unmatched_channels.txt successfully.")