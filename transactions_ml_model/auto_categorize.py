#!/usr/bin/env python3
"""
Auto-categorize transactions based on your keyword rules.
This will pre-fill many categories automatically, making manual work much easier.
"""

import pandas as pd
import re
import csv

def clean_csv_newlines(input_file, cleaned_file):
    """
    Clean CSV file by removing newlines within fields that cause rows to split.
    This fixes the issue where single transactions are split across multiple lines.
    """
    print(f"🧹 Cleaning CSV file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        content = infile.read()
    
    # Split by lines but be careful with quoted fields
    lines = content.split('\n')
    cleaned_lines = []
    current_line = ""
    in_quoted_field = False
    quote_char = None
    
    for line in lines:
        # Check if we're starting a new line or continuing a previous one
        if not current_line:
            current_line = line
        else:
            current_line += " " + line  # Join with space instead of newline
        
        # Count quotes to determine if we're in a quoted field
        quote_count = current_line.count('"')
        if quote_count % 2 == 1:
            # Odd number of quotes means we're still in a quoted field
            continue
        else:
            # Even number of quotes means we've completed a quoted field
            # Check if this looks like a complete CSV row
            if current_line.count(';') >= 12:  # Expected number of semicolons for a complete row
                cleaned_lines.append(current_line)
                current_line = ""
    
    # Add any remaining line
    if current_line.strip():
        cleaned_lines.append(current_line)
    
    # Write cleaned content
    with open(cleaned_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(cleaned_lines))
    
    print(f"✅ Cleaned CSV saved to: {cleaned_file}")
    return cleaned_file

def auto_categorize_transactions(input_file, output_file):
    """Auto-categorize transactions based on keyword matching."""
    
    print(f"📊 Loading {input_file}...")
    df = pd.read_csv(input_file, sep=';', encoding='utf-8')
    
    print(f"✅ Found {len(df)} transactions")
    
    # Your categories and keywords
    categories = {
        'SMALL_SHOPS': ['DEALZ', 'bakaliowesmaki', 'SPAR', 'SKLEP RYBNY', 'Konotop PUH JOZEFOW RYSZARD', 'ZABKA', 'ZYGULA', 'Piekarnia', 'WIELOBRANZOWY', 'DELIKATESY MIESNE', 'ROGAL', 'FIVE', 'LEKS', 'ODiDO', 'PROACTIVE ZAJAC', 'MOTYKA', 'EMI S.C', 'CUKIERNIA SNICKERS', 'DANIEL FIJO', 'WEDLINDROBEX'],
        'MARKETS': ['DINO', 'NETTO', 'BIEDRONKA', 'CARREFOUR', 'LIDL'],
        'ALLEGRO': ['Allegro'],
        'OLX': ['olx.pl'],
        'VINTED': ['VINTED'],
        'PEPCO': ['PEPCO'],
        'PETROL': ['STACJA PALIW', 'LOTOS', 'ORLEN', 'CIRCLE', 'NOWA SOL MOL'],
        'MEDICINE': ['APTEKA'],
        'DOCTORS': ['MEDICUS', 'ALDEMED', 'PERINATEA'],
        'DENTISTRY': ['STOMATOLOGIA'],
        'DIABETIC': ['diabetyk24', 'HEROKU', 'Aero-Medika', 'sugarcubes', 'equil'],
        'TOOLS_SHOPS': ['MROWKA', 'GRANAT'],
        'GAMES': ['GOGcomECOM', 'Steam', 'STEAM', 'PlayStation'],
        'MEDIA': ['YouTubePremium', 'rp.pl', 'Netflix', 'NETFLIX', 'Google Play', 'help.max.com', 'YouTube', 'NBA League Pass', 'SKYSHOWTIME'],
        'ORANGE': ['FLEX'],
        'CLOTHS': ['HM', 'BERSHKA', 'STRADIVARIUS', 'zalando', 'miluba.pl', 'smyk', 'SECRET', 'SINSAY', 'kappahl', 'MEDICINE', 'HOUSE', 'RESERVED', 'HM POL', 'GALANTERIA ODZIEZOWA', 'HEBE', 'CROPP', 'vinted'],
        'CAR_SHOWER': ['WIKON', 'Myjnia'],
        'SHOES': ['Deichmann', 'nbsklep', 'CCC', 'e-cizemka', 'ccc.eu', 'eobuwie', 'zapato'],
        'COSMETICS': ['ROSSMANN', 'SZALATA CHLEBOWSKA'],
        'EMPIK': ['EMPIK'],
        'RESTAURANT': ['DA GRASSO', 'BON BON', 'DOLCE VITA', 'PIZZERIA LUCA', 'STACJA CAFE', 'CAFE SAN-REMO', 'GRYCAN LODY OD POKOLEN', 'TOMASZ KUROS', 'ZIELONA GORA BW SPOLKA Z O.O.', 'MOCCA', 'KARMEL', 'SLOW FOOD', 'Verde', 'EWA DA', 'STARA PIEKARNIA', 'MCDONALDS', 'TCHIBO', 'PIJALNIA KAWY I CZEKO', 'KUCHNIE SWIATA', 'HEBAN', 'Ohy', 'KRATKA', 'Wafelek i Kulka', 'CIACHOO', 'PIERINO', 'CAFFETTERIA GELATERIA'],
        'MIEDZYZDROJE': ['MIEDZYZDROJE'],
        'CINEMA': ['DOM KULTURY', 'cinema-city'],
        'SPORT': ['www.decathlon.pl', 'MARTES'],
        'HAIR_CUT': ['FRYZJERSKI', 'FRYZJERSKA'],
        'PETS': ['PATIVET', 'KAKADU'],
        'ENGLISH': ['edoo'],
        'CASH_MACHINE': ['PLANET CASH', 'KOZUCHOW FILIA', 'NOWA SOL BS NOWA SOL'],
        'CARD_SERVICE': ['OBSLUGE KARTY'],
        'CAR_MECHANIC': ['EXPORT IMPORT LESZEK'],
        'SALETNIK': ['Opłata za terapię', 'Opłata za psychoterapię'],
        'PSYCHOTERAPIA': ['koleo', 'Wroclaw', 'WROCLAW', 'UBER', 'SWIETEJ DOM PIELGRZYMA'],
        'METLIFE': ['21754947'],
        'FARM': ['ZIELONY ZAKATEK', 'OGRODNICZO', 'CENTRUM OGRODNICZE', 'ATO'],
        'WAKACJE_JANOWICE': ['KOWARY', 'Kowary', 'Janowice', 'Mala Upa', 'Jelenia Gora', 'SZRENICA', 'szrenica', 'SZKLARSKA', 'KARPNIKI', ' STARA STAJNIA']
    }
    
    # Add Category column if it doesn't exist
    if 'Category' not in df.columns:
        df['Category'] = ''
    
    # Auto-categorize based on keywords
    print("🤖 Auto-categorizing transactions...")
    
    auto_categorized = 0
    for idx, row in df.iterrows():
        if pd.isna(row['Category']) or row['Category'].strip() == '':
            # Combine all text fields - use correct column names
            nadawca = row.get('Nadawca', '')
            odbiorca = row.get('Odbiorca', '')
            combined_text = f"{row['Opis']} {nadawca} {odbiorca} {row['Produkt']}".lower()
            
            # Check each category
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword.lower() in combined_text:
                        df.at[idx, 'Category'] = category
                        auto_categorized += 1
                        break
                if df.at[idx, 'Category'] != '':
                    break
    
    # Save results
    df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
    
    print(f"✅ Auto-categorized {auto_categorized} transactions")
    print(f"📝 Saved to {output_file}")
    
    # Show statistics
    category_counts = df[df['Category'] != '']['Category'].value_counts()
    print(f"\n📊 Auto-categorized by category:")
    for category, count in category_counts.items():
        print(f"  {category:20}: {count:3} transactions")
    
    uncategorized = len(df[df['Category'] == ''])
    print(f"\n❓ Still need manual categorization: {uncategorized} transactions")
    
    if uncategorized > 0:
        print(f"\n💡 Next steps:")
        print(f"1. Open {output_file} in Excel or text editor")
        print(f"2. Review the auto-categorized transactions")
        print(f"3. Manually categorize the remaining {uncategorized} transactions")
        print(f"4. Use the category names from the list above")
    
    return df

def main():
    """Main function."""
    print("🎯 Auto-Categorize Transactions")
    print("=" * 40)
    
    input_file = '../s3/koszty.csv'
    cleaned_file = '../s3/koszty_cleaned.csv'
    output_file = '../s3/koszty_auto_categorized.csv'
    
    try:
        # First clean the CSV to fix newline issues
        clean_csv_newlines(input_file, cleaned_file)
        
        # Then auto-categorize using the cleaned file
        df = auto_categorize_transactions(cleaned_file, output_file)
        
        print(f"\n🎉 Done! Check {output_file} for results.")
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}")
        print("Please make sure the CSV file exists in the s3 directory.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
