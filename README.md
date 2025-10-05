# Top news app
PyCharm as IDE

## 1. Install
python -m venv venv

## 2. Activate virtual ENV - venv
### Windows
venv\Scripts\activate

python.exe -m pip install --upgrade pip

python -m pip install -r requirements.txt

## 3. Install spacy
python -m spacy download ro_core_news_sm

## 4. Instructions

### 4.1 Run hugging_face_training_ents_keys.ipynb to use results from GPT-4 to train a model based on bert
check for dumitrescustefan_token_output folder

if not running this then change all site scrapers from run-notebook-scraper.ipynb to use one of the above

xxx_scraper = SiteScraper(

    # some other stuff

    model=ModelType.CLAUDE / SPACY / GPT
)

### 4.2 Run-notebook-scraper.ipynb to scrape top four sports news sites for daily articles
results are saved in four csv files that mainly contain summary, entity, and keywords 

summary of each article is obtained with Python beautiful soup 

entities and keywords are yielded by self-trained model with ModelType.BERT, default approach 

to use claude, gpt, or spaCy add custom model as parameter

xxx_scraper = SiteScraper(

    # some other stuff

    model=ModelType.CLAUDE
)

### 4.3 Extra
#### Run quote_all_csv to surround fields with quotes and save in a different file
#### Run gpt_keys_ents_csv_summary.ipynb to use aggregated summaries to extract entities and keywords with GPT-4

## 5. Test
### 5.1 From file - benchmark of statical BERT vs GPT, CLAUDE, and SPACY, output printed, no metrics
It tests against test/storage/prosport_dump.csv (statical BERT results) by randomly choosing two samples

For custom test file it needs BOTH 4.1 - dumitrescustefan_token_output folder - AND to generate 1-4 file(s) with 4.2!!
Then replace test/storage/prosport_dump.csv with your file(s) or a merge of them

#### Windows
pytest test/test_benchmark_models.py -s
#### Bash
pytest test\test_benchmark_models.py -s
### 5.2 All, except benchmark
python -m unittest
