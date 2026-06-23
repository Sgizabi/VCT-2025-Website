#!/usr/bin/env python3
"""
setup_data.py — Run this once to set up your VCT data folder.

Usage:
    python setup_data.py

This will look for your VCT_2025_data zip or extracted folder and
organize everything so app.py can find it.
"""
import os, shutil, zipfile, glob

print("🎯 VCT 2025 Intel Hub — Data Setup")
print("=" * 45)

# 1. Find the zip or extracted folder
zip_candidates = glob.glob("*.zip") + glob.glob("**/*.zip", recursive=False)
folder_candidates = ["VCT_2025_data", "VCT 2025 data", "vct_data", "data"]

source_dir = None

# Check for already-extracted folder
for candidate in folder_candidates:
    if os.path.isdir(candidate):
        # Verify it has event subfolders
        subdirs = [d for d in os.listdir(candidate) if os.path.isdir(os.path.join(candidate, d))]
        if any('VCT' in d or 'Valorant' in d for d in subdirs):
            source_dir = candidate
            print(f"✅ Found extracted data folder: {candidate}/")
            break

# Try extracting zip if no folder found
if source_dir is None:
    for zp in zip_candidates:
        if 'vct' in zp.lower() or 'valorant' in zp.lower():
            print(f"📦 Found zip: {zp}")
            print("   Extracting...")
            with zipfile.ZipFile(zp, 'r') as z:
                z.extractall("VCT_data_extracted")
            # Find the actual data root inside extracted
            for root, dirs, files in os.walk("VCT_data_extracted"):
                if any('VCT' in d or 'Valorant' in d for d in dirs):
                    source_dir = root
                    print(f"✅ Extracted to: {source_dir}/")
                    break
            if source_dir:
                break

if source_dir is None:
    print("\n❌ Could not find VCT data.")
    print("   Please place the VCT_2025_data zip file or extracted folder")
    print("   in the same directory as app.py and re-run this script.")
    exit(1)

# 2. Create target VCT_data folder
target = "VCT_data"
if os.path.exists(target):
    print(f"⚠️  {target}/ already exists — skipping copy.")
else:
    print(f"\n📁 Creating {target}/ ...")
    shutil.copytree(source_dir, target)
    print(f"✅ Data copied to {target}/")

# 3. Verify
events_found = [d for d in os.listdir(target) if os.path.isdir(os.path.join(target, d))]
events_found = [d for d in events_found if 'VCT' in d or 'Valorant' in d]
print(f"\n✅ Found {len(events_found)} event folders:")
for ev in sorted(events_found):
    print(f"   • {ev}")

print("\n" + "=" * 45)
print("✅ Setup complete! Now run:")
print("   streamlit run app.py")
print("=" * 45)
