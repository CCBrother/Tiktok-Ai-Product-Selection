from __future__ import annotations


class CrawlerError(Exception):
    """Base crawler error."""


class CrawlerTimeoutError(CrawlerError):
    """Raised when a page or network wait times out."""


class LoginRequiredError(CrawlerError):
    """Raised when TikTok Shop requires a reusable login session."""
