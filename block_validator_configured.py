"""
IPB Block Validation Helper - Configured for J:\LIB\BR
========================================================

This script validates blocks against your block library with preset paths.

PRESET CONFIGURATION:
- Default CSV: J:\LIB\BR\xxBLOCKS\IPB-DescriptionKeys.csv
- Block Library: J:\LIB\BR (scans ALL subfolders)

Usage Options:

1. SIMPLE - Use preset paths (recommended):
   python block_validator.py

2. CUSTOM CSV - Use different CSV file:
   python block_validator.py <csv_file>

3. CUSTOM PATHS - Override both:
   python block_validator.py <csv_file> <block_folder>

Examples:
   python block_validator.py
   python block_validator.py "C:\Temp\test.csv"
   python block_validator.py "C:\Temp\test.csv" "C:\CAD\Blocks"
"""

import csv
import os
import sys
from pathlib import Path
from collections import defaultdict

# ========================================
# PRESET CONFIGURATION
# ========================================
PRESET_CSV = r"J:\LIB\BR\xxBLOCKS\IPB-DescriptionKeys.csv"
PRESET_BLOCK_FOLDER = r"J:\LIB\BR"


def find_block_files(block_folder):
    """
    Scan block folder RECURSIVELY for all .dwg files
    Returns a set of block names (without extension)
    """
    block_names = set()
    block_folder = Path(block_folder)
    
    if not block_folder.exists():
        print(f"⚠️  Error: Block folder not found: {block_folder}")
        return block_names
    
    print(f"🔍 Scanning recursively: {block_folder}")
    print(f"   (This may take a moment for large libraries...)")
    
    # Search RECURSIVELY for .dwg files using rglob
    dwg_count = 0
    subfolder_count = 0
    subfolders_with_blocks = set()
    
    for dwg_file in block_folder.rglob("*.dwg"):
        block_name = dwg_file.stem.upper()
        block_names.add(block_name)
        dwg_count += 1
        
        # Track which subfolders have blocks
        relative_path = dwg_file.parent.relative_to(block_folder)
        if relative_path != Path('.'):
            subfolders_with_blocks.add(str(relative_path))
    
    print(f"✅ Found {dwg_count} block files")
    if subfolders_with_blocks:
        print(f"📁 Scanned {len(subfolders_with_blocks)} subfolders containing blocks:")
        for subfolder in sorted(subfolders_with_blocks)[:10]:  # Show first 10
            print(f"   - {subfolder}")
        if len(subfolders_with_blocks) > 10:
            print(f"   ... and {len(subfolders_with_blocks) - 10} more")
    
    return block_names


def validate_csv(csv_file, block_names):
    """
    Read CSV and validate each blockname against available blocks
    """
    results = {
        'valid': [],
        'missing': [],
        'duplicates': defaultdict(list),
        'empty_blockname': [],
        'total': 0
    }
    
    if not os.path.exists(csv_file):
        print(f"⚠️  Error: CSV file not found: {csv_file}")
        return results
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            results['total'] += 1
            
            code = row.get('Code', '').strip()
            blockname = row.get('Blockname', '').strip().upper()
            
            # Check for duplicates
            results['duplicates'][code].append(row_num)
            
            # Check for empty blockname
            if not blockname or blockname in ['NULL', 'UNDEFINED', 'N/A']:
                results['empty_blockname'].append({
                    'row': row_num,
                    'code': code,
                    'blockname': blockname or '(empty)',
                    'status': 'EMPTY'
                })
                continue
            
            # Validate block exists
            if blockname in block_names:
                results['valid'].append({
                    'row': row_num,
                    'code': code,
                    'blockname': blockname,
                    'status': 'OK'
                })
            else:
                results['missing'].append({
                    'row': row_num,
                    'code': code,
                    'blockname': blockname,
                    'status': 'MISSING'
                })
    
    # Clean up duplicates (keep only actual duplicates)
    results['duplicates'] = {
        code: rows for code, rows in results['duplicates'].items() 
        if len(rows) > 1
    }
    
    return results


def generate_report(results, output_file='validation_report.txt', csv_file='', block_folder=''):
    """
    Generate a detailed validation report
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("IPB BLOCK VALIDATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Configuration info
        f.write("CONFIGURATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"CSV File:       {csv_file}\n")
        f.write(f"Block Library:  {block_folder}\n")
        f.write("\n")
        
        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Entries:       {results['total']}\n")
        f.write(f"Valid Blocks:        {len(results['valid'])}\n")
        f.write(f"Missing Blocks:      {len(results['missing'])}\n")
        f.write(f"Empty Block Names:   {len(results['empty_blockname'])}\n")
        f.write(f"Duplicate Codes:     {len(results['duplicates'])}\n")
        f.write("\n")
        
        # Empty blocknames
        if results['empty_blockname']:
            f.write("EMPTY BLOCK NAMES\n")
            f.write("-" * 80 + "\n")
            for item in results['empty_blockname']:
                f.write(f"Row {item['row']:4d}: {item['code']:20s} → {item['blockname']}\n")
            f.write("\n")
        
        # Missing blocks
        if results['missing']:
            f.write("MISSING BLOCKS\n")
            f.write("-" * 80 + "\n")
            f.write("These blocks are referenced in the CSV but not found in the library:\n\n")
            for item in results['missing']:
                f.write(f"Row {item['row']:4d}: {item['code']:20s} → {item['blockname']}\n")
            f.write("\n")
        
        # Duplicates
        if results['duplicates']:
            f.write("DUPLICATE CODES\n")
            f.write("-" * 80 + "\n")
            f.write("These codes appear multiple times (may be intentional):\n\n")
            for code, rows in sorted(results['duplicates'].items()):
                f.write(f"{code:20s}: Found on rows {', '.join(map(str, rows))}\n")
            f.write("\n")
        
        # Recommendations
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 80 + "\n")
        if results['empty_blockname']:
            f.write("• Fix empty block names - assign proper block references\n")
        if results['missing']:
            f.write("• Create missing blocks in AutoCAD or update CSV to use existing blocks\n")
        if results['duplicates']:
            f.write("• Review duplicate codes - consolidate if unintentional\n")
        if not (results['empty_blockname'] or results['missing'] or results['duplicates']):
            f.write("✅ No issues found! Your IPB configuration looks great.\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("Report complete!\n")
    
    print(f"📄 Report saved: {output_file}")


def generate_validated_csv(csv_file, results, output_file='IPB-DescriptionKeys-Validated.csv'):
    """
    Generate new CSV with validation status column
    """
    if not os.path.exists(csv_file):
        return
    
    # Read original CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Add validation column header
    if rows:
        rows[0].append('ValidationStatus')
    
    # Create lookup for validation status
    status_lookup = {}
    for item in results['valid']:
        status_lookup[item['row']] = 'OK'
    for item in results['missing']:
        status_lookup[item['row']] = 'MISSING'
    for item in results['empty_blockname']:
        status_lookup[item['row']] = 'EMPTY'
    
    # Add validation status to each row
    for i in range(1, len(rows)):
        row_num = i + 1
        status = status_lookup.get(row_num, 'UNKNOWN')
        rows[i].append(status)
    
    # Write validated CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"💾 Validated CSV saved: {output_file}")


def main():
    # Determine which paths to use
    if len(sys.argv) == 1:
        # Use preset paths
        csv_file = PRESET_CSV
        block_folder = PRESET_BLOCK_FOLDER
        print("📌 Using preset configuration")
    elif len(sys.argv) == 2:
        # Custom CSV, preset block folder
        csv_file = sys.argv[1]
        block_folder = PRESET_BLOCK_FOLDER
        print("📌 Using custom CSV with preset block folder")
    elif len(sys.argv) >= 3:
        # Custom both
        csv_file = sys.argv[1]
        block_folder = sys.argv[2]
        print("📌 Using custom paths")
    else:
        print("Usage: python block_validator.py [csv_file] [block_folder]")
        print(f"\nDefault CSV: {PRESET_CSV}")
        print(f"Default Block Folder: {PRESET_BLOCK_FOLDER}")
        sys.exit(1)
    
    # Verify CSV exists
    if not os.path.exists(csv_file):
        print(f"⚠️  Error: CSV file not found: {csv_file}")
        print("\nUsage: python block_validator.py [csv_file] [block_folder]")
        print(f"Default CSV: {PRESET_CSV}")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("IPB BLOCK VALIDATION")
    print("=" * 80 + "\n")
    
    print(f"CSV File:      {csv_file}")
    print(f"Block Folder:  {block_folder}")
    print()
    
    # Step 1: Find all block files
    print("Step 1: Scanning block library (including all subfolders)...")
    block_names = find_block_files(block_folder)
    
    if not block_names:
        print("⚠️  No blocks found. Check folder path.")
        sys.exit(1)
    
    print()
    
    # Step 2: Validate CSV
    print("Step 2: Validating CSV entries...")
    results = validate_csv(csv_file, block_names)
    
    print(f"✅ Validated {results['total']} entries")
    print()
    
    # Step 3: Generate reports
    print("Step 3: Generating reports...")
    generate_report(results, csv_file=csv_file, block_folder=block_folder)
    generate_validated_csv(csv_file, results)
    
    print()
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"✅ Valid:          {len(results['valid'])}")
    print(f"❌ Missing:        {len(results['missing'])}")
    print(f"⚠️  Empty Names:    {len(results['empty_blockname'])}")
    print(f"⚠️  Duplicates:     {len(results['duplicates'])}")
    print()
    
    # Show sample missing blocks
    if results['missing']:
        print("Sample missing blocks:")
        for item in results['missing'][:5]:
            print(f"  - {item['blockname']}")
        if len(results['missing']) > 5:
            print(f"  ... and {len(results['missing']) - 5} more (see report)")
    
    # Show sample empty blocknames
    if results['empty_blockname']:
        print("\nEntries with empty block names:")
        for item in results['empty_blockname'][:5]:
            print(f"  - Row {item['row']}: Code {item['code']}")
        if len(results['empty_blockname']) > 5:
            print(f"  ... and {len(results['empty_blockname']) - 5} more (see report)")
    
    print("\n📄 Review 'validation_report.txt' for complete details")


if __name__ == '__main__':
    main()
