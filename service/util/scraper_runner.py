# service/util/scraper_runner.py

import threading

from app.config.loader import load_sites_from_config
from service.cluster_service import ClusterService
from service.util.buffer_util import delete_delta_file_if_exists
from service.util.cooldown_util import load_cooldowns
from service.util.logger_util import get_logger
from service.util.scrape_runner_declension_util import ScrapeRunnerDeclensionUtil
from service.util.scrape_runner_merge_util import ScrapeRunnerMergeUtil
from service.util.scrape_runner_util import ScrapeRunnerUtil
from service.util.timing_util import elapsed_time, log_thread_id

logger = get_logger()


@elapsed_time("run_scraper")
def run_scraper(minutes=1440):
    load_cooldowns()

    logger.info("*" * 100)
    logger.info(f"Running {log_thread_id(threading.get_ident(), 'scraper')}")
    sites = load_sites_from_config()

    # Compute weights
    ScrapeRunnerUtil.compute_weights(sites)

    # Phase 1: Scraping
    threads = [threading.Thread(target=ScrapeRunnerUtil.process_site, args=(site, minutes)) for site in sites]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Phase 2: Declension
    site_deltas = ScrapeRunnerDeclensionUtil.process_declension_phase(sites)
    if site_deltas is None:
        return

    # Phase 3: Merging
    ScrapeRunnerMergeUtil.process_merge_phase(sites, site_deltas)

    # Phase 4: Saving (parallel)
    threads = [threading.Thread(target=ScrapeRunnerUtil.save_site, args=(site,)) for site in sites]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Phase 5: Clustering
    ClusterService.save_cluster_buffer(sites, minutes)

    # Phase 6: Cleanup
    delete_delta_file_if_exists()
