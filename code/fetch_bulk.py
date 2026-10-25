"""Download the Gaia SSO epoch-photometry bulk files of a release (resumable).

Usage: fetch_bulk.py <release prefix, e.g. Gaia/gdr3/Solar_system/sso_observation/> <out dir>
The file list comes from the CDN77 S3 listing; files are fetched from cdn.gea.esac.esa.int with curl -C -.
For DR4 the prefix may differ: list https://gaia.eu-1.cdn77-storage.com/?prefix=Gaia/gdr4/&delimiter=/ first.
"""
import os, re, subprocess, sys, urllib.request

prefix, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
keys, marker = [], ""
while True:
    url = f"https://gaia.eu-1.cdn77-storage.com/?prefix={prefix}&delimiter=/" + (f"&marker={marker}" if marker else "")
    xml = urllib.request.urlopen(url, timeout=120).read().decode()
    page = re.findall(r"<Key>([^<]+\.csv\.gz)</Key>", xml)
    keys += page
    if "<IsTruncated>true</IsTruncated>" not in xml or not page:
        break
    marker = page[-1]
print(f"{len(keys)} files under {prefix}", flush=True)
for k in keys:
    dst = os.path.join(out, os.path.basename(k))
    subprocess.run(["curl", "-sf", "-C", "-", "--retry", "5", "-o", dst, f"https://cdn.gea.esac.esa.int/{k}"], check=True)
    print("ok", os.path.basename(k), os.path.getsize(dst), flush=True)
