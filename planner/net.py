# planner/net.py  (new tiny helper)
import time, requests
from requests.exceptions import HTTPError

def get_with_backoff(url: str,
                     max_retries: int = 5,
                     backoff: float = 1.5) -> dict:
    """
    GET `url` with exponential back-off for 429 / 5xx answers.
    Returns response.json().
    """
    for attempt in range(max_retries):
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            return resp.json()

        # 429 or 5xx → sleep & retry
        if resp.status_code in (429, 502, 503, 504):
            sleep = backoff ** attempt          # 1.5, 2.25, 3.37, …
            print(f"[OSRM] {resp.status_code} – retrying in {sleep:,.1f}s")
            time.sleep(sleep)
            continue
        resp.raise_for_status()                # other errors → raise
    raise HTTPError(f"OSRM failed after {max_retries} retries")
