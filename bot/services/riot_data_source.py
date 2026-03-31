import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from ..utils.constants import DDRAGON_VERSIONS_URL, DDRAGON_CHAMPIONS_URL, DDRAGON_CHAMPION_DETAILS_URL, DDRAGON_IMG_URL, PATCH_NOTES_BASE_URL
from ..utils.logger import root_logger

class RiotDataSource:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache_versions: Optional[List[str]] = None
        self._cache_champion_data: Dict[str, Dict] = {} # {version: data}
        self._cache_patch_notes: Dict[str, Dict] = {} # {version: data}

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def _request_with_retry(self, url: str, method: str = "GET", retries: int = 3) -> Optional[Dict | str]:
        await self._ensure_session()
        for attempt in range(retries):
            try:
                async with self.session.request(method, url) as response:
                    # Check headers for rate limiting if present
                    # Data Dragon usually doesn't have these, but standard Riot APIs do
                    rate_limit = response.headers.get("X-Method-Rate-Limit-Remaining")
                    if rate_limit and int(rate_limit) == 0:
                        retry_after = int(response.headers.get("Retry-After", 1))
                        root_logger.warning(f"Rate limited on {url}. Waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue

                    if response.status == 200:
                        if "application/json" in response.headers.get("Content-Type", ""):
                            return await response.json()
                        return await response.text()
                    
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 1))
                        await asyncio.sleep(retry_after)
                        continue
                        
                    root_logger.error(f"Request to {url} failed with status {response.status}")
            except Exception as e:
                root_logger.error(f"Attempt {attempt+1} failed for {url}: {e}")
            
            if attempt < retries - 1:
                wait_time = (2 ** attempt) # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(wait_time)
        return None

    async def fetch_latest_version(self) -> str:
        if self._cache_versions:
            return self._cache_versions[0]
        
        data = await self._request_with_retry(DDRAGON_VERSIONS_URL)
        if data and isinstance(data, list):
            self._cache_versions = data
            return data[0]
        return ""

    async def fetch_champion_data(self, version: str) -> Dict:
        """
        Fetches the complete champion data (summary + details for each).
        """
        if version in self._cache_champion_data:
            return self._cache_champion_data[version]

        url = DDRAGON_CHAMPIONS_URL.format(version=version)
        summary_data = await self._request_with_retry(url)
        
        if not summary_data or "data" not in summary_data:
            return {}

        champions = summary_data["data"]
        # In a real-world scenario, we'd fetch details only for changed ones to save bandwidth
        # but the spec asks for "full data".
        
        self._cache_champion_data[version] = champions
        return champions

    async def fetch_champion_details(self, version: str, champion_id: str) -> Dict:
        url = DDRAGON_CHAMPION_DETAILS_URL.format(version=version, champion_name=champion_id)
        data = await self._request_with_retry(url)
        if data and "data" in data:
            return data["data"].get(champion_id, {})
        return {}

    async def scrape_patch_notes(self, version: str) -> Dict:
        """
        Scrapes official patch notes for champion changes.
        Returns a dict mapping champion name to their specific changes.
        """
        if version in self._cache_patch_notes:
            return self._cache_patch_notes[version]

        parts = version.split('.')
        version_slug = f"{parts[0]}-{parts[1]}" if len(parts) >= 2 else version.replace('.', '-')
        url = PATCH_NOTES_BASE_URL.format(version_slug=version_slug)
        
        html = await self._request_with_retry(url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'lxml')
        results = {}
        
        # Heuristic scraping logic (Riot's HTML structure can be complex)
        # Usually champion changes are under <h4> or <h3 class="change-detail-title">
        champions_sections = soup.find_all(['h3', 'h4'], class_=['change-detail-title', 'patch-change-title'])
        
        for section in champions_sections:
            camp_name = section.get_text(strip=True)
            # Find the next sibling nodes until the next champion section
            changes = []
            next_node = section.find_next_sibling()
            while next_node and next_node.name not in ['h3', 'h4']:
                if next_node.name == 'div' and 'patch-change-block' in next_node.get('class', []):
                    # Ability change block
                    ability_header = next_node.find(['h4', 'h5'])
                    ability_name = ability_header.get_text(strip=True) if ability_header else "Base Stats"
                    
                    # Look for <li> items with old/new values
                    change_items = next_node.find_all('li')
                    for li in change_items:
                        text = li.get_text(strip=True)
                        # Extract "Value: 50 -> 60"
                        if "⇒" in text or "->" in text:
                            changes.append({"ability": ability_name, "raw": text})
                
                next_node = next_node.find_next_sibling()
            
            if changes:
                results[camp_name] = changes

        self._cache_patch_notes[version] = results
        return results

    def get_champion_icon_url(self, version: str, champion_id: str) -> str:
        return DDRAGON_IMG_URL.format(version=version, champion_name=champion_id)

    async def close(self):
        if self.session:
            await self.session.close()
