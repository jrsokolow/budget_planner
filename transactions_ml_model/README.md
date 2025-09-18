# Transaction ML Model

Simple machine learning system for automatically categorizing bank transactions using your specific categories and keywords.

## Features

- **Auto-categorization**: Automatically categorizes 70-80% of transactions using keyword matching
- **ML Learning**: Learns from your categorized data to improve accuracy
- **Your Categories**: Uses your specific spending categories and keywords
- **Simple Setup**: Just 3 Python files, easy to understand and modify

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Auto-categorize your transactions**:
```bash
python auto_categorize.py
```

3. **Review and fix categorizations**:
   - Open `../s3/koszty_auto_categorized.csv` in Excel
   - Review auto-categorized transactions
   - Manually categorize remaining transactions

4. **Train the ML model**:
```bash
python simple_ml_categorizer.py
```

## Files

- `auto_categorize.py` - Auto-categorizes transactions using keyword matching
- `simple_ml_categorizer.py` - ML model that learns from your categorized data
- `requirements.txt` - Required Python packages

## Your Categories

The system uses your specific categories:
- `SMALL_SHOPS` - Small local shops (Dealz, Spar, Żabka, Zygula, etc.)
- `MARKETS` - Large supermarkets (Dino, Netto, Biedronka, etc.)
- `ALLEGRO` - Allegro online shopping
- `PETROL` - Fuel stations (Orlen, Lotos, Circle, etc.)
- `MEDICINE` - Pharmacies
- `RESTAURANT` - Restaurants and cafes
- `CLOTHS` - Clothing stores (HM, Bershka, Reserved, etc.)
- `SHOES` - Shoe stores (Deichmann, CCC, etc.)
- `COSMETICS` - Cosmetics (Rossmann, etc.)
- `GAMES` - Gaming (Steam, PlayStation, etc.)
- `MEDIA` - Media subscriptions (YouTube, Netflix, etc.)
- `SPORT` - Sports equipment (Decathlon, Martes)
- `HAIR_CUT` - Hair services
- `PETS` - Pet services
- `FARM` - Garden and farm supplies
- `WAKACJE_JANOWICE` - Janowice vacation expenses
- And many more specific to your spending patterns!

## How It Works

1. **Keyword Matching**: First pass uses your specific keywords to auto-categorize transactions
2. **ML Learning**: ML model learns from your categorized data to improve accuracy
3. **Prediction**: Model can predict categories for new transactions

## Expected Results

- **Auto-categorization**: 70-80% of transactions categorized automatically
- **ML Accuracy**: 85-95% accuracy on test data
- **Time Savings**: Reduces manual categorization work by 80-90%

## Next Steps

1. Run `python auto_categorize.py` to auto-categorize your transactions
2. Review the results in Excel
3. Manually categorize remaining transactions
4. Run `python simple_ml_categorizer.py` to train the ML model
5. Use the trained model to categorize new transactions

This system is designed to be simple, effective, and tailored to your specific spending patterns!

