# service/util/scrape_runner_declension_util.py

from model.model_type import ModelType
from service.util.buffer_util import update_delta_timestamp
from service.util.declension_util import DeclensionUtil
from service.util.delta_checker import DeltaChecker
from service.util.logger_util import get_logger
from service.util.scrape_runner_util import ScrapeRunnerUtil
from service.util.timing_util import elapsed_time

logger = get_logger()


class ScrapeRunnerDeclensionUtil:

    @staticmethod
    def process_declension_phase(sites):
        site_deltas = DeltaChecker.get_all_deltas(sites)

        is_skipped_for_all: bool = True
        for site_name, prev_and_curr_tuple in site_deltas.items():
            curr_articles = prev_and_curr_tuple[1]
            if len(curr_articles["new"]) + len(curr_articles["updated"]) != 0:
                logger.info(f"[Scraper] Deltas already detected: {site_name}. Break loop and continue with next phase.")
                is_skipped_for_all = False
                break
        if is_skipped_for_all:
            logger.info("[Scraper] No deltas detected. Skipping declension, saving, and clustering.")
            update_delta_timestamp()
            return None

        tokenizer, model = ScrapeRunnerUtil.get_model_and_tokenizer()

        for site in sites:
            deltas = site_deltas[site.name][1]
            articles_to_declension = deltas["new"] + deltas["updated"]
            logger.info(f"[Articles to Declension] {site.name}: {len(articles_to_declension)}")

            if len(articles_to_declension) == 0:
                logger.info(f"No declensions detected. Skipping declension for {site.name}")
                continue

            if site.model_type == ModelType.BERT:
                @elapsed_time(f"Declension for {site.name}")
                def process_declension(articles):
                    try:
                        for article in articles:
                            article.entities = [
                                DeclensionUtil.normalize(ent, (tokenizer, model)) for ent in article.entities
                            ]
                            article.keywords = [
                                DeclensionUtil.normalize(kw, (tokenizer, model)) for kw in article.keywords
                            ]
                    except Exception as e:
                        logger.info(f"[Declension Error] {site.name}: {e}")

                process_declension(articles_to_declension)

        return site_deltas
