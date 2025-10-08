import os

from flask import Blueprint, jsonify

from app.config.loader import load_sites_from_config
from service.story_clusterer import StoryClusterer

cluster_bp = Blueprint("cluster", __name__)


@cluster_bp.route("/cluster", methods=["GET"])
def cluster_news():
    # Get absolute path to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "sites_config.json")

    sites = load_sites_from_config(config_path)
    total_traffic = sum(site.traffic for site in sites)
    for site in sites:
        site.compute_weight(total_traffic)
    clusterer = StoryClusterer(sites, 360, 0.3, 0.2)
    clusterer.cluster_stories()
    return jsonify(clusterer.get_matched_clusters())
