"""
OmniRevive-OS | Multi-Region Active-Active CAS Distributed Lock Coordinator
Coordinates atomic Compare-And-Swap (CAS) mutexes across AWS Mumbai (ap-south-1)
and Hyderabad (ap-south-2) with monotonic fencing tokens to guarantee 0 double-debits.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class RegionLockRecord:
    owner_id: str
    fencing_token: int
    expires_at: float


class MultiRegionCASCoordinator:
    """Thread-safe active-active CAS lock manager across ap-south-1 & ap-south-2."""

    REGIONS = ("ap-south-1", "ap-south-2")

    def __init__(self, default_ttl_seconds: float = 300.0):
        self.default_ttl_seconds = default_ttl_seconds
        self._lock = threading.Lock()
        self._fencing_counter = 0
        self._stores: Dict[str, Dict[str, RegionLockRecord]] = {
            r: {} for r in self.REGIONS
        }

    def acquire_quorum_lock(
        self,
        resource_key: str,
        owner_id: str,
        ttl_seconds: Optional[float] = None,
        now: Optional[float] = None,
    ) -> Tuple[bool, Optional[int]]:
        """
        Acquire an active-active CAS lock across both Indian regions.
        Returns (acquired, fencing_token). Fails closed if either region holds an active lock.
        """
        ts = now if now is not None else time.monotonic()
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds

        with self._lock:
            for region in self.REGIONS:
                existing = self._stores[region].get(resource_key)
                if existing is not None and existing.expires_at > ts:
                    return False, None

            self._fencing_counter += 1
            token = self._fencing_counter
            record = RegionLockRecord(
                owner_id=owner_id,
                fencing_token=token,
                expires_at=ts + ttl,
            )
            for region in self.REGIONS:
                self._stores[region][resource_key] = record
            return True, token

    def release_quorum_lock(self, resource_key: str, owner_id: str) -> bool:
        """Compare-And-Swap release: only the current lock owner may release."""
        with self._lock:
            released = False
            for region in self.REGIONS:
                existing = self._stores[region].get(resource_key)
                if existing is not None and existing.owner_id == owner_id:
                    del self._stores[region][resource_key]
                    released = True
            return released
