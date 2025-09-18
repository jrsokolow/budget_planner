#!/usr/bin/env python3
"""
Simple ML categorizer that learns from your manually categorized data.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import re

class SimpleTransactionCategorizer:
    """Simple ML model for transaction categorization."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
        # Your specific categories and keywords
        self.categories = {
            'SMALL_SHOPS': ['DEALZ', 'bakaliowesmaki', 'SPAR', 'SKLEP RYBNY', 'Konotop PUH JOZEFOW RYSZARD', 'ZABKA', 'ZYGULA', 'Piekarnia', 'WIELOBRANZOWY', 'DELIKATESY MIESNE', 'ROGAL', 'FIVE', 'LEKS', 'ODiDO', 'PROACTIVE ZAJAC', 'MOTYKA', 'EMI S.C', 'CUKIERNIA SNICKERS', 'DANIEL FIJO', 'WEDLINDROBEX'],
            'MARKETS': ['DINO', 'NETTO', 'BIEDRONKA', 'CARREFOUR', 'LIDL'],
            'ALLEGRO': ['Allegro'],
            'OLX': ['olx.pl'],
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
    
    def clean_text(self, text):
        """Clean and prepare text for ML."""
        if pd.isna(text) or text == '':
            return ''
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove special characters but keep Polish characters
        text = re.sub(r'[^a-ząćęłńóśźż\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def suggest_category(self, description, nadawca, odbiorca, product):
        """Suggest category based on keyword matching."""
        combined_text = f"{description} {nadawca} {odbiorca} {product}".lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    return category
        
        return 'OTHER'
    
    def prepare_data(self, df):
        """Prepare data for training."""
        # Clean text fields
        df['description_clean'] = df['Opis'].apply(self.clean_text)
        df['nadawca_clean'] = df['Nadawca'].apply(self.clean_text)
        df['odbiorca_clean'] = df['Odbiorca'].apply(self.clean_text)
        df['product_clean'] = df['Produkt'].apply(self.clean_text)
        
        # Combine all text fields
        df['combined_text'] = (
            df['description_clean'] + ' ' + 
            df['nadawca_clean'] + ' ' + 
            df['odbiorca_clean'] + ' ' + 
            df['product_clean']
        ).str.strip()
        
        return df
    
    def train(self, csv_file):
        """Train the model on categorized data."""
        print(f"📊 Loading data from {csv_file}...")
        
        # Load data
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        
        # Check if Category column exists
        if 'Category' not in df.columns:
            print("❌ No 'Category' column found. Please run auto_categorize.py first.")
            return False
        
        # Filter out empty categories
        df_categorized = df[df['Category'].str.strip() != ''].copy()
        
        if len(df_categorized) == 0:
            print("❌ No categorized transactions found. Please add some categories first.")
            return False
        
        print(f"✅ Found {len(df_categorized)} categorized transactions")
        
        # Prepare data
        df_processed = self.prepare_data(df_categorized)
        
        # Get features and labels
        X = df_processed['combined_text'].values
        y = df_processed['Category'].values
        
        # Vectorize text
        X_vectorized = self.vectorizer.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_vectorized, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        print("🤖 Training model...")
        self.model.fit(X_train, y_train)
        
        # Test model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model trained successfully!")
        print(f"📈 Accuracy: {accuracy:.3f}")
        
        # Show per-category performance
        print(f"\n📊 Per-category performance:")
        report = classification_report(y_test, y_pred, output_dict=True)
        for category, metrics in report.items():
            if isinstance(metrics, dict) and 'precision' in metrics:
                print(f"{category:20}: Precision={metrics['precision']:.3f}, Recall={metrics['recall']:.3f}")
        
        self.is_trained = True
        return True
    
    def predict(self, description, nadawca, odbiorca, product):
        """Predict category for a single transaction."""
        if not self.is_trained:
            print("❌ Model not trained yet. Please train first.")
            return None
        
        # Prepare text
        combined_text = self.clean_text(description) + ' ' + self.clean_text(nadawca) + ' ' + self.clean_text(odbiorca) + ' ' + self.clean_text(product)
        
        # Vectorize
        X = self.vectorizer.transform([combined_text])
        
        # Predict
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Get confidence
        confidence = max(probabilities)
        
        return {
            'category': prediction,
            'confidence': confidence,
            'all_probabilities': dict(zip(self.model.classes_, probabilities))
        }
    
    def predict_csv(self, input_file, output_file):
        """Predict categories for all transactions in a CSV file."""
        if not self.is_trained:
            print("❌ Model not trained yet. Please train first.")
            return
        
        print(f"📊 Predicting categories for {input_file}...")
        
        # Load data
        df = pd.read_csv(input_file, sep=';', encoding='utf-8')
        
        # Prepare data
        df_processed = self.prepare_data(df)
        
        # Predict for each row
        predictions = []
        confidences = []
        
        for _, row in df_processed.iterrows():
            pred = self.predict(row['Opis'], row['Nadawca'], row['Odbiorca'], row['Produkt'])
            if pred:
                predictions.append(pred['category'])
                confidences.append(pred['confidence'])
            else:
                predictions.append('OTHER')
                confidences.append(0.0)
        
        # Add predictions to dataframe
        df['Predicted_Category'] = predictions
        df['Prediction_Confidence'] = confidences
        
        # Save results
        df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
        
        print(f"✅ Predictions saved to {output_file}")
        
        # Show summary
        category_counts = df['Predicted_Category'].value_counts()
        print(f"\n📊 Predicted categories:")
        for category, count in category_counts.items():
            print(f"{category:20}: {count:3} transactions")
    
    def save_model(self, filename='transaction_categorizer.joblib'):
        """Save the trained model."""
        if not self.is_trained:
            print("❌ Model not trained yet. Please train first.")
            return
        
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model
        }
        
        joblib.dump(model_data, filename)
        print(f"💾 Model saved to {filename}")
    
    def load_model(self, filename='transaction_categorizer.joblib'):
        """Load a trained model."""
        try:
            model_data = joblib.load(filename)
            self.vectorizer = model_data['vectorizer']
            self.model = model_data['model']
            self.is_trained = True
            print(f"✅ Model loaded from {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False

def main():
    """Main function to demonstrate the categorizer."""
    categorizer = SimpleTransactionCategorizer()
    
    print("🎯 Simple Transaction Categorizer")
    print("=" * 40)
    
    # Check if we have categorized data
    try:
        df = pd.read_csv('../s3/koszty_auto_categorized.csv', sep=';', encoding='utf-8')
        if 'Category' in df.columns and df['Category'].str.strip().ne('').any():
            print("✅ Found categorized data. Training model...")
            if categorizer.train('../s3/koszty_auto_categorized.csv'):
                categorizer.save_model()
                
                # Test on some examples
                print(f"\n🧪 Testing predictions:")
                test_transactions = [
                    ("KOZUCHOW NETTO 5204 K.3 POL", "557464------1444 URSZULA SOKOLOWSKA", "", "Karta Mastercard"),
                    ("WROCLAW RESTAURACJA RAJSKIE OG POL", "557464------1444 URSZULA SOKOLOWSKA", "", "Karta Mastercard"),
                    ("Uber Amsterdam", "Uber Meester Treublaan 7 Amsterdam NL", "", "Konto Osobiste")
                ]
                
                for desc, nadawca, odbiorca, product in test_transactions:
                    pred = categorizer.predict(desc, nadawca, odbiorca, product)
                    if pred:
                        print(f"  {desc[:30]}... -> {pred['category']} (confidence: {pred['confidence']:.3f})")
        else:
            print("❌ No categorized data found. Please run auto_categorize.py first.")
    except FileNotFoundError:
        print("❌ No categorized data found. Please run auto_categorize.py first.")

if __name__ == "__main__":
    main()
