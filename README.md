# Top news app
PyCharm as IDE

## Unit test
### From file - benchmark, output printed
#### Windows
pytest test/test_benchmark_models.py -s
#### Bash
pytest test\test_benchmark_models.py -s
### All, except benchmark
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

### Run hugging_face_training_ents_keys.ipynb to use results from GPT-4 to train a model based on bert
if not running this then change all site scrapers from run-notebook-scraper.ipynb to use one of the above

xxx_scraper = SiteScraper(

    # some other stuff

    model=ModelType.CLAUDE / SPACY / GPT
)

### Run-notebook-scraper.ipynb to scrape top four sports news sites for daily articles
results are saved in four csv files that mainly contain summary, entity, and keywords 

summary of each article is obtained with Python beautiful soup 

entities and keywords are yielded by self-trained model with bert, default approach 

to use claude, gpt, or spaCy add custom model as parameter

xxx_scraper = SiteScraper(

    # some other stuff

    model=ModelType.CLAUDE
)

### Extra
#### Run quote_all_csv to surround fields with quotes and save in a different file
#### Run gpt_keys_ents_csv_summary.ipynb to use aggregated summaries to extract entities and keywords with GPT-4
