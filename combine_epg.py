import gzip
import io
import time
import datetime
import xml.etree.ElementTree as ET
import requests
from channel_map import CHANNEL_MAPPING  # Imports your channel map

URLS = [
    # Master EPGShare01 All-In-One Feed (Contains all global & regional rippers)
    "https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz",
    # Complete Open-EPG Country & Category Feeds
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
headers = {"User-Agent": "Mozilla/5.0"}

channels_list = []
programmes_list = []
seen_channels = set()

# Window: 24h past to 24h future
now = datetime.datetime.now(datetime.timezone.utc)
min_time = (now - datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")
max_time = (now + datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")

for idx, url in enumerate(URLS, 1):
    feed_name = url.split('/')[-1]
    print(f"[{idx}/{len(URLS)}] Fetching {feed_name}...")
    try:
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as gz:
                tree = ET.parse(gz)
                root = tree.getroot()
                
                for elem in root:
                    if elem.tag == "channel":
                        cid = elem.get("id")
                        # Read and apply mapped ID from channel_map.py
                        mapped_cid = CHANNEL_MAPPING.get(cid, cid)
                        if mapped_cid:
                            elem.set("id", mapped_cid)
                            if mapped_cid not in seen_channels:
                                seen_channels.add(mapped_cid)
                                channels_list.append(elem)
                    elif elem.tag == "programme":
                        start = elem.get("start", "")[:14]
                        if min_time <= start <= max_time:
                            ch_ref = elem.get("channel")
                            # Apply mapped ID to programme channel reference
                            mapped_ch_ref = CHANNEL_MAPPING.get(ch_ref, ch_ref)
                            if mapped_ch_ref:
                                elem.set("channel", mapped_ch_ref)

                            for desc in elem.findall("desc"):
                                elem.remove(desc)
                            programmes_list.append(elem)
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
    time.sleep(0.3)

print(f"Channels: {len(channels_list)} | Programmes: {len(programmes_list)}")

# Build standard XMLTV tree (all channels first, then programmes)
combined_root = ET.Element("tv")

for ch in channels_list:
    combined_root.append(ch)

for pr in programmes_list:
    combined_root.append(pr)

print("Writing file...")
with gzip.open(OUTPUT_FILE, "wb", compresslevel=9) as f_out:
    ET.ElementTree(combined_root).write(f_out, encoding="utf-8", xml_declaration=True)

print("Finished successfully.")
OUTPUT_FILE = "combined_epg.xml.gz"
headers = {"User-Agent": "Mozilla/5.0"}

channels_list = []
programmes_list = []
seen_channels = set()

# Window: 24h past to 24h future
now = datetime.datetime.now(datetime.timezone.utc)
min_time = (now - datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")
max_time = (now + datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")

for idx, url in enumerate(URLS, 1):
    feed_name = url.split('/')[-1]
    print(f"[{idx}/{len(URLS)}] Fetching {feed_name}...")
    try:
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as gz:
                tree = ET.parse(gz)
                root = tree.getroot()
                
                for elem in root:
                    if elem.tag == "channel":
                        cid = elem.get("id")
                        # Read and apply mapped ID from channel_map.py
                        mapped_cid = CHANNEL_MAPPING.get(cid, cid)
                        if mapped_cid:
                            elem.set("id", mapped_cid)
                            if mapped_cid not in seen_channels:
                                seen_channels.add(mapped_cid)
                                channels_list.append(elem)
                    elif elem.tag == "programme":
                        start = elem.get("start", "")[:14]
                        if min_time <= start <= max_time:
                            ch_ref = elem.get("channel")
                            # Apply mapped ID to programme channel reference
                            mapped_ch_ref = CHANNEL_MAPPING.get(ch_ref, ch_ref)
                            if mapped_ch_ref:
                                elem.set("channel", mapped_ch_ref)

                            for desc in elem.findall("desc"):
                                elem.remove(desc)
                            programmes_list.append(elem)
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
    time.sleep(0.3)

print(f"Channels: {len(channels_list)} | Programmes: {len(programmes_list)}")

# Build standard XMLTV tree (all channels first, then programmes)
combined_root = ET.Element("tv")

for ch in channels_list:
    combined_root.append(ch)

for pr in programmes_list:
    combined_root.append(pr)

print("Writing file...")
with gzip.open(OUTPUT_FILE, "wb", compresslevel=9) as f_out:
    ET.ElementTree(combined_root).write(f_out, encoding="utf-8", xml_declaration=True)

print("Finished successfully.")
