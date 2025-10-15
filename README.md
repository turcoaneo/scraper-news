# Top news app  
PyCharm as IDE

## Notes

- Requires Python 3.11+ and internet access for model downloads. Please update .env with your keys.   
- Output files are typically saved in `storage/` or `output/` folders  
- For benchmark tests, all paths are dynamically resolved using `os.path.join()` for cross-platform compatibility  
- When terminal-specific commands are required, ticks are omitted to avoid misleading syntax highlighting  
  - **Windows** refers to both Command Prompt and PowerShell  
  - **Bash** refers to GitBash, WSL, or Unix-like shells
- All ```bash``` commands work for Windows terminal as well.

## 1. Install
```bash
python -m venv venv
```

## 2. Activate virtual ENV - venv  
### Windows  
venv\Scripts\activate
### Bash
source venv/bin/activate

```bash
python.exe -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Install spaCy  
```bash
python -m spacy download ro_core_news_sm
```

## 4. Instructions  

### 4.1 Run `notebooks/hugging_face_training_ents_keys.ipynb` to train a BERT model using GPT-4 results  
Check for `dumitrescustefan_token_output` folder.  

If not running this, scrapers will default to BERT. To override, change model type in `run-notebook-scraper.ipynb`:  
```python
xxx_scraper = SiteScraper(
    # other parameters
    model=ModelType.CLAUDE #/ SPACY / GPT
)
```

### 4.2 Run `notebooks/run-notebook-scraper.ipynb` to scrape top four sports news sites  
Results are saved in four CSV files containing summary, entities, and keywords.  

- Summary is extracted via BeautifulSoup  
- Entities and keywords are extracted using the selected model (default: BERT)  

To use Claude, GPT, or spaCy:  
```python
xxx_scraper = SiteScraper(
    # other parameters
    model=ModelType.CLAUDE
)
```

### 4.3 Extra  
- Run `notebooks/quote_all_csv.ipynb` to surround fields with quotes and save to a new file  
- Run `notebooks/gpt_keys_ents_csv_summary.ipynb` to extract entities and keywords from aggregated summaries using GPT-4
- Run `notebooks/t5_declension.ipynb` to train a model for declension (e.g., sportivulului -> sportiv, Stelei -> Steaua)
- Run `notebooks/t5_retrain.ipynb` to re-train / fine-tune the model for declension (not really working as expected)
- Run `notebooks/lora_extractor.ipynb` to improve the model for declension with LoRA (not really working as expected)

## 5. Test  

### 5.1 Benchmark: Compare static BERT vs GPT, Claude, and spaCy  
Tests against `test/storage/prosport_dump.csv` (contains BERT results) using two random samples.  

For a custom test file, you must run both:  
- 4.1 to generate `dumitrescustefan_token_output`  
- 4.2 to generate 1–4 CSV files  

Then replace `test/storage/prosport_dump.csv` with your file or a merge of them.  

#### Windows  
pytest test/test_benchmark_models.py -s

#### Bash  
pytest test\test_benchmark_models.py -s

### 5.2 Run all other tests  
```bash
python -m unittest
```
 