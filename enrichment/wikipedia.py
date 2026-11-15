"""Polite, restartable collection of unmodified Wikidata/Wikipedia responses.

No text is generated here. Data transformations belong in the Spark notebook.
API references: https://www.mediawiki.org/wiki/API:Etiquette and
https://www.mediawiki.org/wiki/Extension:TextExtracts (20 extracts per request).
"""
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

USER_AGENT = "ECE-IMDb-Enrichment/1.0 (https://github.com/oscarico92/Big-Data-Project-IMDB)"


class Collector:
    def __init__(self, directory, pause=1.5, attempts=5):
        self.directory = Path(directory)
        self.pause = max(1.0, pause)
        self.attempts = attempts
        self.last_call = 0.0
        self.requests = 0
        self.cache_hits = 0

    def request(self, service, endpoint, params):
        query = urllib.parse.urlencode(sorted(params.items()))
        url = endpoint + "?" + query
        key = hashlib.sha256(url.encode()).hexdigest()
        folder = self.directory / service
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / (key + ".json")
        if target.exists():
            self.cache_hits += 1
            return target
        for attempt in range(self.attempts):
            time.sleep(max(0, self.pause - (time.monotonic() - self.last_call)))
            retry_after = 0
            try:
                self.last_call = time.monotonic()
                self.requests += 1
                req = urllib.request.Request(url, headers={
                    "User-Agent": USER_AGENT, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=90) as response:
                    payload = json.load(response)
                if "error" in payload:
                    error = payload["error"]
                    if error.get("code") not in {"maxlag", "ratelimited", "readonly"}:
                        raise ValueError(f"API error: {error}")
                    raise RuntimeError(str(error))
                envelope = {"retrieved_at": datetime.now(timezone.utc).isoformat(),
                            "request_url": url, "response": payload}
                temporary = target.with_suffix(".tmp")
                temporary.write_text(json.dumps(envelope, ensure_ascii=False), encoding="utf-8")
                temporary.replace(target)
                return target
            except urllib.error.HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504}:
                    raise
                value = exc.headers.get("Retry-After", "0")
                try:
                    retry_after = float(value)
                except ValueError:
                    retry_after = max(0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
                error = exc
            except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
                error = exc
            if attempt + 1 == self.attempts:
                raise RuntimeError(f"Collection stopped after {self.attempts} attempts: {url}") from error
            time.sleep(max(retry_after, min(60, 5 * 2 ** attempt)))

    def identities(self, ids, batch_size=100):
        """IDs must be a bounded Spark-selected cohort, never the whole IMDb table."""
        if not 1 <= batch_size <= 200:
            raise ValueError("Wikidata batch size must be between 1 and 200")
        paths = []
        for start in range(0, len(ids), batch_size):
            batch = ids[start:start + batch_size]
            if any(not re.fullmatch(r"(?:tt|nm)\d+", x) for x in batch):
                raise ValueError("Invalid IMDb identifier")
            values = " ".join(json.dumps(x) for x in batch)
            query = f'''SELECT DISTINCT ?imdb_id ?item ?article WHERE {{
              VALUES ?imdb_id {{ {values} }}
              ?item <http://www.wikidata.org/prop/direct/P345> ?imdb_id .
              OPTIONAL {{ ?article <http://schema.org/about> ?item ;
                <http://schema.org/isPartOf> <https://en.wikipedia.org/> . }}
            }}'''
            paths.append(str(self.request("wikidata", "https://query.wikidata.org/sparql",
                                          {"query": query, "format": "json"})))
            print(f"Wikidata: {min(start + batch_size, len(ids))}/{len(ids)} IDs", flush=True)
        return paths

    def extracts(self, titles, batch_size=20):
        if not 1 <= batch_size <= 20:
            raise ValueError("TextExtracts permits at most 20 extracts per request")
        paths = []
        for start in range(0, len(titles), batch_size):
            params = {"action": "query", "format": "json", "formatversion": 2,
                      "prop": "extracts|info|pageprops", "titles": "|".join(titles[start:start + batch_size]),
                      "exintro": 1, "explaintext": 1, "exlimit": 20,
                      "inprop": "url", "redirects": 1, "maxlag": 5}
            paths.append(str(self.request("wikipedia", "https://en.wikipedia.org/w/api.php", params)))
            print(f"Wikipedia: {min(start + batch_size, len(titles))}/{len(titles)} pages", flush=True)
        return paths
