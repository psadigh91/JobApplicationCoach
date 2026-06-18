"""
Company Crawler - Crawl company websites for culture/values data
Limits to 10 pages, prioritizes about/careers/culture pages
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import asyncio


class CompanyCrawler:
    """Crawl company websites to extract culture and values information"""

    # Priority URL patterns (in order of importance)
    PRIORITY_PATTERNS = [
        r'/(about|about-us|about_us|company|who-we-are)',
        r'/(careers|jobs|work-here|join-us|life-at)',
        r'/(culture|values|mission|purpose)',
        r'/(team|people|leadership)',
        r'/(products?|services?|solutions?)',
        r'/(blog|news|press|media)',
    ]

    def __init__(self, max_pages: int = 10, timeout: int = 30):
        """
        Initialize crawler

        Args:
            max_pages: Maximum number of pages to crawl
            timeout: Request timeout in seconds
        """
        self.max_pages = max_pages
        self.timeout = timeout
        self.visited_urls = set()
        self.domain = None

    async def crawl(self, base_url: str) -> List[Dict]:
        """
        Crawl company website starting from base URL

        Args:
            base_url: Company website homepage URL

        Returns:
            List of crawled pages with content
        """
        # Normalize URL
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url

        # Extract domain for same-domain filtering
        parsed = urlparse(base_url)
        self.domain = parsed.netloc

        # Start with homepage
        urls_to_crawl = [base_url]
        crawled_pages = []

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            while urls_to_crawl and len(crawled_pages) < self.max_pages:
                url = urls_to_crawl.pop(0)

                # Skip if already visited
                if url in self.visited_urls:
                    continue

                # Crawl page
                page_data = await self._crawl_page(client, url)

                if page_data:
                    crawled_pages.append(page_data)
                    self.visited_urls.add(url)

                    # Extract links for further crawling
                    new_urls = self._extract_links(page_data['html'], base_url)

                    # Prioritize URLs
                    prioritized = self._prioritize_urls(new_urls)

                    # Add to queue (avoiding duplicates)
                    for new_url in prioritized:
                        if new_url not in self.visited_urls and new_url not in urls_to_crawl:
                            urls_to_crawl.append(new_url)

                # Brief delay to be respectful
                await asyncio.sleep(0.5)

        return crawled_pages

    async def _crawl_page(self, client: httpx.AsyncClient, url: str) -> Optional[Dict]:
        """
        Crawl a single page

        Args:
            client: HTTP client
            url: URL to crawl

        Returns:
            Dictionary with page data or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return None

            html = response.text

            # Extract content
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style tags
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            # Extract title
            title = soup.title.string if soup.title else url

            # Extract main text content
            content = self._extract_text_content(soup)

            # Extract metadata
            metadata = self._extract_metadata(soup)

            return {
                "url": url,
                "title": str(title).strip() if title else "",
                "content": content,
                "word_count": len(content.split()),
                "crawled_at": datetime.utcnow().isoformat(),
                "metadata": metadata,
                "html": html  # Store for link extraction
            }

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return None

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        # Try to find main content areas
        main_content = None

        # Common content containers
        for selector in ['main', 'article', '[role="main"]', '.content', '#content', '.main']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')

        if not main_content:
            return ""

        # Extract text, preserving some structure
        text_parts = []
        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li']):
            text = element.get_text(strip=True)
            if text and len(text) > 10:  # Filter out very short snippets
                text_parts.append(text)

        return '\n'.join(text_parts)

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from page"""
        metadata = {}

        # Extract meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            metadata['description'] = desc_tag['content']

        # Extract Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            metadata['og_title'] = og_title['content']

        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            metadata['og_description'] = og_desc['content']

        return metadata

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from page"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)

            # Parse URL
            parsed = urlparse(absolute_url)

            # Filter: same domain, http(s) only, no fragments, no file downloads
            if (parsed.netloc == self.domain and
                parsed.scheme in ['http', 'https'] and
                not re.search(r'\.(pdf|jpg|jpeg|png|gif|zip|doc|docx|xls|xlsx)$', parsed.path, re.IGNORECASE)):

                # Remove fragment
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"

                links.append(clean_url)

        return list(set(links))  # Remove duplicates

    def _prioritize_urls(self, urls: List[str]) -> List[str]:
        """
        Sort URLs by priority based on patterns

        Args:
            urls: List of URLs to prioritize

        Returns:
            Sorted list with priority URLs first
        """
        def url_priority(url: str) -> int:
            """Return priority score (lower is better)"""
            url_lower = url.lower()

            # Check each priority pattern
            for i, pattern in enumerate(self.PRIORITY_PATTERNS):
                if re.search(pattern, url_lower):
                    return i

            # Homepage gets high priority
            parsed = urlparse(url)
            if parsed.path in ['', '/']:
                return -1

            # Default priority (last)
            return len(self.PRIORITY_PATTERNS)

        return sorted(urls, key=url_priority)
