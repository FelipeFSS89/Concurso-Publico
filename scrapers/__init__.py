"""
Módulo de Scrapers de Concursos
"""
from scrapers.coordinator import ScraperCoordinator
from scrapers.base_scraper import BaseScraper
from scrapers.degrau_scraper import DegrauScraper
from scrapers.folha_scraper import FolhaQCScraper

__all__ = ["ScraperCoordinator", "BaseScraper", "DegrauScraper", "FolhaQCScraper"]
