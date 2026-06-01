import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
import os

# Configuration
MEMBER_ID = "1972108"
README_PATH = "README.md"
START_TAG = "<!-- GAMEBANANA-START -->"
END_TAG = "<!-- GAMEBANANA-END -->"

API_URL = f"https://api.gamebanana.com/Rss/New?itemtype=Mod&userid={MEMBER_ID}"

def fetch_mods():
    print(f"Fetching latest mods for Member ID: {MEMBER_ID} via RSS...")
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'GitHub-Readme-Bot'})
    try:
        with urllib.request.urlopen(req) as response:
            raw_data = response.read().decode('utf-8', errors='ignore')
            start_idx = raw_data.find('<rss')
            end_idx = raw_data.rfind('</rss>')
            
            if start_idx != -1 and end_idx != -1:
                clean_xml = raw_data[start_idx:end_idx + 6]
                return ET.fromstring(clean_xml)
            return None
    except Exception as e:
        print(f"Error fetching GameBanana data: {e}")
        return None

def generate_markdown(root):
    if root is None:
        return "\n*No recent mods found or API unreachable.*\n"

    items = root.findall('.//item')
    if not items:
        return "\n*No recent mods found.*\n"

    md_content = "\n<div align=\"center\">\n\n"
    
    for item in items[:3]:
        title_elem = item.find('title')
        link_elem = item.find('link')
        image_elem = item.find('image')
        
        if title_elem is not None and link_elem is not None:
            name = title_elem.text
            url = link_elem.text
            
            if image_elem is not None and image_elem.text:
                img_url = image_elem.text
            else:
                img_url = "https://gamebanana.com/static/img/objects/embed_default.png"

            md_content += f'  <a href="{url}"><img src="{img_url}" alt="{name}" height="120" style="border-radius: 8px; margin: 5px; object-fit: cover;"/></a>\n'
            
    md_content += "\n</div>\n"
    return md_content
    return md_content

def update_readme(new_content):
    if not os.path.exists(README_PATH):
        print(f"{README_PATH} not found.")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = re.compile(rf"({START_TAG}).*?({END_TAG})", re.DOTALL)
    
    if not pattern.search(readme):
        print(f"Could not find tags {START_TAG} and {END_TAG} in {README_PATH}")
        return

    updated_readme = pattern.sub(rf"\1{new_content}\2", readme)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_readme)
    print("README.md updated successfully!")

if __name__ == "__main__":
    mod_data = fetch_mods()
    new_markdown = generate_markdown(mod_data)
    update_readme(new_markdown)
