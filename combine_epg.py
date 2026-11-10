import os
import gzip
import io
import time
import datetime
import re
import xml.etree.ElementTree as ET
import requests
from channel_map import CHANNEL_MAPPING

# =====================================================================
# 1. EPG SOURCES
# =====================================================================
URLS = [
    "https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz",
    "https://www.open-epg.com/files/albania.xml.gz",
    "https://www.open-epg.com/files/argentina.xml.gz",
    "https://www.open-epg.com/files/australia.xml.gz",
    "https://www.open-epg.com/files/austria.xml.gz",
    "https://www.open-epg.com/files/belgium.xml.gz",
    "https://www.open-epg.com/files/bosnia.xml.gz",
    "https://www.open-epg.com/files/brazil.xml.gz",
    "https://www.open-epg.com/files/bulgaria.xml.gz",
    "https://www.open-epg.com/files/canada1.xml.gz",
    "https://www.open-epg.com/files/canada2.xml.gz",
    "https://www.open-epg.com/files/croatia.xml.gz",
    "https://www.open-epg.com/files/czech.xml.gz",
    "https://www.open-epg.com/files/denmark.xml.gz",
    "https://www.open-epg.com/files/egypt.xml.gz",
    "https://www.open-epg.com/files/finland.xml.gz",
    "https://www.open-epg.com/files/france.xml.gz",
    "https://www.open-epg.com/files/germany.xml.gz",
    "https://www.open-epg.com/files/greece.xml.gz",
    "https://www.open-epg.com/files/hungary.xml.gz",
    "https://www.open-epg.com/files/india.xml.gz",
    "https://www.open-epg.com/files/ireland.xml.gz",
    "https://www.open-epg.com/files/israel.xml.gz",
    "https://www.open-epg.com/files/italy.xml.gz",
    "https://www.open-epg.com/files/latvia.xml.gz",
    "https://www.open-epg.com/files/lithuania.xml.gz",
    "https://www.open-epg.com/files/macedonia.xml.gz",
    "https://www.open-epg.com/files/mexico.xml.gz",
    "https://www.open-epg.com/files/montenegro.xml.gz",
    "https://www.open-epg.com/files/morocco.xml.gz",
    "https://www.open-epg.com/files/netherlands.xml.gz",
    "https://www.open-epg.com/files/newzealand.xml.gz",
    "https://www.open-epg.com/files/norway.xml.gz",
    "https://www.open-epg.com/files/poland.xml.gz",
    "https://www.open-epg.com/files/portugal.xml.gz",
    "https://www.open-epg.com/files/qatar.xml.gz",
    "https://www.open-epg.com/files/romania.xml.gz",
    "https://www.open-epg.com/files/russia.xml.gz",
    "https://www.open-epg.com/files/saudiarabia.xml.gz",
    "https://www.open-epg.com/files/serbia.xml.gz",
    "https://www.open-epg.com/files/slovakia.xml.gz",
    "https://www.open-epg.com/files/slovenia.xml.gz",
    "https://www.open-epg.com/files/southafrica.xml.gz",
    "https://www.open-epg.com/files/spain.xml.gz",
    "https://www.open-epg.com/files/sports.xml.gz",
    "https://www.open-epg.com/files/sweden.xml.gz",
    "https://www.open-epg.com/files/switzerland.xml.gz",
    "https://www.open-epg.com/files/turkey.xml.gz",
    "https://www.open-epg.com/files/uae.xml.gz",
    "https://www.open-epg.com/files/ukraine.xml.gz",
    "https://www.open-epg.com/files/unitedkingdom.xml.gz",
    "https://www.open-epg.com/files/unitedstates.xml.gz",
]

OUTPUT_FILE = "combined_epg.xml.gz"
headers = {"User-Agent": "Mozilla/5.0"}

target_epg_ids = {v.lower() for v in CHANNEL_MAPPING.values()}

epg_to_tvgid = {}
epg_to_search_slugs = {}

for mapped_key, epg_id in CHANNEL_MAPPING.items():
    epg_low = epg_id.lower()
    if epg_low not in epg_to_tvgid:
        epg_to_tvgid[epg_low] = mapped_key
    
    # Generate a clean text slug from the mapping key to search for logos
    clean_name = re.sub(r'\[.*?\]|\(.*?\)', ' ', mapped_key)
    clean_name = re.sub(r'\b(fhd|uhd|hdr|hevc|4k|8k|sd|hd)\b', ' ', clean_name, flags=re.IGNORECASE)
    slug = re.sub(r'[^a-z0-9]', '', clean_name.lower())
    
    if epg_low not in epg_to_search_slugs:
        epg_to_search_slugs[epg_low] = []
    if slug and slug not in epg_to_search_slugs[epg_low]:
        epg_to_search_slugs[epg_low].append(slug)

def fetch_github_logos():
    print("[GitHub Actions] Fetching latest logos from tv-logo/tv-logos...")
    country_logos = {}
    api_url = "https://api.github.com/repos/tv-logo/tv-logos/contents/countries"
    try:
        res = requests.get(api_url, headers=headers, timeout=30)
        if res.status_code == 200:
            for country_obj in res.json():
                if country_obj.get("type") == "dir":
                    c_folder = country_obj["name"].lower()
                    c_res = requests.get(country_obj["url"], headers=headers, timeout=30)
                    if c_res.status_code == 200:
                        logo_list = []
                        for f in c_res.json():
                            if f.get("type") == "file" and f["name"].endswith((".png", ".jpg", ".svg")):
                                clean_fname = re.sub(r'[^a-z0-9]', '', os.path.splitext(f["name"])[0].lower())
                                logo_list.append((f["download_url"], clean_fname))
                            elif f.get("type") == "dir":
                                sub_res = requests.get(f["url"], headers=headers, timeout=15)
                                if sub_res.status_code == 200:
                                    for sf in sub_res.json():
                                        if sf.get("type") == "file" and sf["name"].endswith((".png", ".jpg", ".svg")):
                                            clean_sfname = re.sub(r'[^a-z0-9]', '', os.path.splitext(sf["name"])[0].lower())
                                            logo_list.append((sf["download_url"], clean_sfname))
                        country_logos[c_folder] = logo_list
    except Exception as e:
        print(f"[Warning] Failed to fetch logos: {e}")
    return country_logos

def get_new_channel_id(epg_id_lower):
    return epg_to_tvgid.get(epg_id_lower, epg_id_lower)

channels_dict = {}
programmes_list = []
active_channel_ids = set() 

now = datetime.datetime.now(datetime.timezone.utc)
min_time = (now - datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")
max_time = (now + datetime.timedelta(days=2)).strftime("%Y%m%d%H%M%S")

repo_logos = fetch_github_logos()

for idx, url in enumerate(URLS, 1):
    feed_name = url.split('/')[-1]
    print(f"[{idx}/{len(URLS)}] Fetching {feed_name}...")
    try:
        res = requests.get(url, headers=headers, timeout=60, stream=True)
        if res.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as gz:
                for event, elem in ET.iterparse(gz, events=("end",)):
                    if elem.tag == "channel":
                        cid = elem.get("id")
                        if cid and cid.lower() in target_epg_ids:
                            if cid.lower() not in channels_dict:
                                new_id = get_new_channel_id(cid.lower())
                                elem.set("id", new_id)
                                
                                # --- NEW: APPEND ORIGINAL ID TO DISPLAY NAME ---
                                # This makes manual matching in TiviMate/Smarters much easier
                                # e.g., changes "HRT 1" to "HRT 1 [HRT1.hr]"
                                for dn in elem.findall("display-name"):
                                    if dn.text and cid not in dn.text:
                                        dn.text = f"{dn.text} [{cid}]"
                                
                                # Search for logo match
                                best_logo = None
                                search_slugs = epg_to_search_slugs.get(cid.lower(), [])
                                for slug in search_slugs:
                                    if not slug: continue
                                    for folder_items in repo_logos.values():
                                        for dl_url, clean_fname in folder_items:
                                            if slug == clean_fname or slug in clean_fname:
                                                best_logo = dl_url
                                                break
                                        if best_logo: break
                                    if best_logo: break

                                # Inject logo into XML
                                if best_logo:
                                    icon_elem = elem.find("icon")
                                    if icon_elem is not None:
                                        icon_elem.set("src", best_logo)
                                    else:
                                        icon_elem = ET.SubElement(elem, "icon")
                                        icon_elem.set("src", best_logo)

                                channels_dict[cid.lower()] = ET.tostring(elem, encoding="unicode")
                        elem.clear()
                    elif elem.tag == "programme":
                        ch_ref = elem.get("channel")
                        start = elem.get("start", "")[:14]
                        if ch_ref and ch_ref.lower() in target_epg_ids and (min_time <= start <= max_time):
                            new_ch = get_new_channel_id(ch_ref.lower())
                            elem.set("channel", new_ch)
                            for desc in elem.findall("desc"):
                                elem.remove(desc)
                            programmes_list.append(ET.tostring(elem, encoding="unicode"))
                            active_channel_ids.add(ch_ref.lower())
                        elem.clear()
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
    time.sleep(0.2)

# Strict Filtering: Only keep channels that registered active programs
valid_channels = [xml for cid, xml in channels_dict.items() if cid in active_channel_ids]

print(f"Matched Channels with Data: {len(valid_channels)} | Programmes: {len(programmes_list)}")

print("Writing strictly filtered EPG file with injected logos...")
with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as gz_out:
    gz_out.write('<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="epg-combiner">\n')
    for ch_xml in valid_channels:
        gz_out.write("  " + ch_xml.strip() + "\n")
    for pr_xml in programmes_list:
        gz_out.write("  " + pr_xml.strip() + "\n")
    gz_out.write("</tv>\n")

print("Finished successfully.")
