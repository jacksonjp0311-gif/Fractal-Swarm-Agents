"""
safe_scrape.py — Hardened wrapper adapter for Scrapling skill

Contract:
  safe_scrape(url, instructions=None, agent_id=None, proxy=None, **kwargs) -> str

Notes:
- Accepts `instructions=` for swarm callers (ignored or used as optional hint).
- Ignores unknown kwargs for forward compatibility.
- Does NOT attempt to bypass authentication, paywalls, CAPTCHAs, or access controls.
- Uses basic requests GET as a safe baseline adapter.
"""

from __future__ import annotations

from typing import Optional, Any, Dict
import time
import random
import requests


def safe_scrape(
    url: str,
    instructions: Optional[str] = None,
    agent_id: Optional[str] = None,
    proxy: Optional[str] = None,
    timeout_s: float = 20.0,
    min_delay_s: float = 0.2,
    max_delay_s: float = 0.8,
    user_agent: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """
    Safe baseline fetcher.

    Parameters
    ----------
    url : str
    instructions : Optional[str]
        Optional parsing hint. This adapter currently does not execute instructions;
        it only fetches HTML. (Future: selective extraction.)
    agent_id : Optional[str]
        Used for logging/headers if desired.
    proxy : Optional[str]
        HTTP(S) proxy URL (e.g. http://host:port). If None, direct.
    timeout_s : float
    min_delay_s, max_delay_s : float
        Small jitter delay to avoid hammering.
    user_agent : Optional[str]
    kwargs : Any
        Ignored for forward compatibility.

    Returns
    -------
    str : HTML/text content
    """
    # tiny jitter to reduce burstiness (not stealth, just politeness)
    if max_delay_s > 0:
        time.sleep(random.uniform(min_delay_s, max_delay_s))

    headers: Dict[str, str] = {
        "User-Agent": user_agent
        or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FractalSwarmAgents/2.0 (+local)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    if agent_id:
        headers["X-Agent-Id"] = str(agent_id)

    proxies = None
    if proxy:
        proxies = {"http": proxy, "https": proxy}

    r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout_s)
    r.raise_for_status()
    return r.text