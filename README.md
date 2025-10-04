# Top news app

## Unit test
### From file - benchmark, output printed
python -m unittest test/test_benchmark_models.py
### All
python -m unittest

## Install
python -m venv venv

## Activate virtual ENV - venv
### Windows
venv\Scripts\activate

python.exe -m pip install --upgrade pip
python -m pip install -r requirements.txt

## Install spacy
python -m spacy download ro_core_news_sm

## Instructions

### run-notebook-scraper.ipynb to scrape top four sports news sites for daily articles
results are saved in four csv files that mainly contain summary, entity, and keywords
summary of each article is obtained with Python beautiful soup
entities and keywords are yielded by bert, claude, gpt, or spaCy

### Run quote_all_csv to surround fields with quotes and save in a different file

### Run gpt_keys_ents_csv_summary.ipynb to use aggregated summaries to extract entities and keywords with GPT-4

### Run hugging_face_training_ents_keys.ipynb to use results from GPT-4 to train a model based on bert