# Top news app

## Unit test
### All
python -m unittest
### From file
python -m unittest test/test_article_scraper.py

## Install
python -m venv venv

## Activate virtual ENV - venv
### Windows
venv\Scripts\activate

python.exe -m pip install --upgrade pip
python -m pip install -r requirements.txt

## Install spacy
python -m spacy download ro_core_news_sm
