# service/util/scrape_runner_merge_util.py

from service.util.logger_util import get_logger
from service.util.scrape_runner_util import ScrapeRunnerUtil

logger = get_logger()


class ScrapeRunnerMergeUtil:

    @staticmethod
    def process_merge_phase(sites, site_deltas):
        for site in sites:
            site_name = site.name
            site_delta_tuple_result = site_deltas[site_name]
            deltas = site_delta_tuple_result[1]
            raw_previous = site_delta_tuple_result[0] or {}

            previous_articles = {
                url: ScrapeRunnerUtil.dict_to_article(row, site_name)
                for url, row in raw_previous.items()
            }

            merged_articles = ScrapeRunnerUtil.merge_articles(deltas, previous_articles, site_name)
            site.articles = set(merged_articles)
            logger.info(f"{site_name} - {len(site.articles)} articles")
