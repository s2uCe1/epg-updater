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
# 1. EPG SOURCES (Open-EPG Primary, EPG Share)
# =====================================================================
URLS = [
    # --- MAIN SOURCE: OPEN-EPG ---
    "https://www.open-epg.com/files/albania.xml.gz",
    "https://www.open-epg.com/files/argentina.xml.gz",
    "https://www.open-epg.com/files/australia.xml.gz",
    "https://www.open-epg.com/files/austria.xml.gz",
    "https://www.open-epg.com/files/barbados.xml.gz",
    "https://www.open-epg.com/files/belgium.xml.gz",
    "https://www.open-epg.com/files/bolivia.xml.gz",
    "https://www.open-epg.com/files/bosnia.xml.gz",
    "https://www.open-epg.com/files/brazil.xml.gz",
    "https://www.open-epg.com/files/bulgaria.xml.gz",
    "https://www.open-epg.com/files/canada.xml.gz",
    "https://www.open-epg.com/files/chile.xml.gz",
    "https://www.open-epg.com/files/china.xml.gz",
    "https://www.open-epg.com/files/colombia.xml.gz",
    "https://www.open-epg.com/files/costarica.xml.gz",
    "https://www.open-epg.com/files/croatia.xml.gz",
    "https://www.open-epg.com/files/cyprus.xml.gz",
    "https://www.open-epg.com/files/czech.xml.gz",
    "https://www.open-epg.com/files/denmark.xml.gz",
    "https://www.open-epg.com/files/dominican.xml.gz",
    "https://www.open-epg.com/files/ecuador.xml.gz",
    "https://www.open-epg.com/files/egypt.xml.gz",
    "https://www.open-epg.com/files/elsalvador.xml.gz",
    "https://www.open-epg.com/files/estonia.xml.gz",
    "https://www.open-epg.com/files/finland.xml.gz",
    "https://www.open-epg.com/files/france.xml.gz",
    "https://www.open-epg.com/files/georgia1.xml.gz",
    "https://www.open-epg.com/files/germany.xml.gz",
    "https://www.open-epg.com/files/ghana1.xml.gz",
    "https://www.open-epg.com/files/greece.xml.gz",
    "https://www.open-epg.com/files/guatemala.xml.gz",
    "https://www.open-epg.com/files/honduras.xml.gz",
    "https://www.open-epg.com/files/hungary.xml.gz",
    "https://www.open-epg.com/files/iceland.xml.gz",
    "https://www.open-epg.com/files/india.xml.gz",
    "https://www.open-epg.com/files/indonesia.xml.gz",
    "https://www.open-epg.com/files/ireland.xml.gz",
    "https://www.open-epg.com/files/italy.xml.gz",
    "https://www.open-epg.com/files/ivorycoast.xml.gz",
    "https://www.open-epg.com/files/jamaica.xml.gz",
    "https://www.open-epg.com/files/japan.xml.gz",
    "https://www.open-epg.com/files/korea.xml.gz",
    "https://www.open-epg.com/files/latvia.xml.gz",
    "https://www.open-epg.com/files/lithuania.xml.gz",
    "https://www.open-epg.com/files/macau.xml.gz",
    "https://www.open-epg.com/files/macedonia.xml.gz",
    "https://www.open-epg.com/files/madagascar.xml.gz",
    "https://www.open-epg.com/files/malawi.xml.gz",
    "https://www.open-epg.com/files/malaysia.xml.gz",
    "https://www.open-epg.com/files/malta.xml.gz",
    "https://www.open-epg.com/files/mauritius.xml.gz",
    "https://www.open-epg.com/files/mexico.xml.gz",
    "https://www.open-epg.com/files/moldova.xml.gz",
    "https://www.open-epg.com/files/mongolia.xml.gz",
    "https://www.open-epg.com/files/montenegro.xml.gz",
    "https://www.open-epg.com/files/morocco.xml.gz",
    "https://www.open-epg.com/files/mozambique.xml.gz",
    "https://www.open-epg.com/files/namibia.xml.gz",
    "https://www.open-epg.com/files/netherlands.xml.gz",
    "https://www.open-epg.com/files/newcaledonia.xml.gz",
    "https://www.open-epg.com/files/newzealand.xml.gz",
    "https://www.open-epg.com/files/nigeria.xml.gz",
    "https://www.open-epg.com/files/norway.xml.gz",
    "https://www.open-epg.com/files/pakistan.xml.gz",
    "https://www.open-epg.com/files/palestine.xml.gz",
    "https://www.open-epg.com/files/panama.xml.gz",
    "https://www.open-epg.com/files/paraguay1.xml.gz",
    "https://www.open-epg.com/files/peru.xml.gz",
    "https://www.open-epg.com/files/poland.xml.gz",
    "https://www.open-epg.com/files/portugal.xml.gz",
    "https://www.open-epg.com/files/puertorico.xml.gz",
    "https://www.open-epg.com/files/qatar.xml.gz",
    "https://www.open-epg.com/files/reunion.xml.gz",
    "https://www.open-epg.com/files/romania.xml.gz",
    "https://www.open-epg.com/files/russia.xml.gz",
    "https://www.open-epg.com/files/saudiarabia.xml.gz",
    "https://www.open-epg.com/files/senegal.xml.gz",
    "https://www.open-epg.com/files/serbia.xml.gz",
    "https://www.open-epg.com/files/singapore.xml.gz",
    "https://www.open-epg.com/files/slovakia.xml.gz",
    "https://www.open-epg.com/files/slovenia.xml.gz",
    "https://www.open-epg.com/files/southafrica1.xml.gz",
    "https://www.open-epg.com/files/spain.xml.gz",
    "https://www.open-epg.com/files/sports1.xml.gz",
    "https://www.open-epg.com/files/sports4.xml.gz",
    "https://www.open-epg.com/files/sports5.xml.gz",
    "https://www.open-epg.com/files/sweden.xml.gz",
    "https://www.open-epg.com/files/switzerland.xml.gz",
    "https://www.open-epg.com/files/taiwan.xml.gz",
    "https://www.open-epg.com/files/tanzania.xml.gz",
    "https://www.open-epg.com/files/thailand.xml.gz",
    "https://www.open-epg.com/files/trinidad.xml.gz",
    "https://www.open-epg.com/files/turkey.xml.gz",
    "https://www.open-epg.com/files/uae.xml.gz",
    "https://www.open-epg.com/files/uganda.xml.gz",
    "https://www.open-epg.com/files/ukraine.xml.gz",
    "https://www.open-epg.com/files/unitedkingdom.xml.gz",
    "https://www.open-epg.com/files/unitedstates1.xml.gz",
    "https://www.open-epg.com/files/unitedstates10.xml.gz",
    "https://www.open-epg.com/files/unitedstates2.xml.gz",
    "https://www.open-epg.com/files/unitedstates3.xml.gz",
    "https://www.open-epg.com/files/unitedstates4.xml.gz",
    "https://www.open-epg.com/files/unitedstates5.xml.gz",
    "https://www.open-epg.com/files/unitedstates6.xml.gz",
    "https://www.open-epg.com/files/unitedstates7.xml.gz",
    "https://www.open-epg.com/files/unitedstates8.xml.gz",
    "https://www.open-epg.com/files/unitedstates9.xml.gz",
    "https://www.open-epg.com/files/uruguay.xml.gz",
    "https://www.open-epg.com/files/uzbekistan.xml.gz",
    "https://www.open-epg.com/files/venezuela.xml.gz",
    "https://www.open-epg.com/files/vietnam1.xml.gz",
    "https://www.open-epg.com/files/zambia.xml.gz",
    "https://www.open-epg.com/files/zimbabwe.xml.gz",
    # --- BACKUP 1: EPG SHARE ---
    "https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz",
]

OUTPUT_FILE = "combined_epg.xml.gz"
headers = {"User-Agent": "Mozilla/5.0"}

target_epg_ids = {v.lower() for v in CHANNEL_MAPPING.values()}

# BUG FIX: Use lists to store ALL M3U names mapped to a single EPG ID
epg_to_tvgids = {}
epg_to_search_slugs = {}

for mapped_key, epg_id in CHANNEL_MAPPING.items():
    epg_low = epg_id.lower()
    if epg_low not in epg_to_tvgids:
        epg_to_tvgids[epg_low] = []
    
    # Store every single variation we find
    if mapped_key not in epg_to_tvgids[epg_low]:
        epg_to_tvgids[epg_low].append(mapped_key)
    
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
                                
                                # Clear old display-names
                                for dn in elem.findall("display-name"):
                                    elem.remove(dn)
                                
                                # BUG FIX: Inject a display-name tag for EVERY mapped variation
                                mapped_names = epg_to_tvgids.get(cid.lower(), [])
                                for playlist_name in mapped_names:
                                    dn_exact = ET.SubElement(elem, "display-name")
                                    dn_exact.text = playlist_name
                                
                                # Keep the original ID as a fallback reference
                                dn_fallback = ET.SubElement(elem, "display-name")
                                dn_fallback.text = cid
                                
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
                            for desc in elem.findall("desc"):
                                elem.remove(desc)
                            programmes_list.append(ET.tostring(elem, encoding="unicode"))
                            active_channel_ids.add(ch_ref.lower())
                        elem.clear()
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
    time.sleep(0.2)

valid_channels = list(channels_dict.values())

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
