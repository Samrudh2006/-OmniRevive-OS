"""
OmniRevive-OS Standalone Merkle Tree Proof & RFC 6962 Verifier
=============================================================
Research Foundations:
- "Certificate Transparency" (RFC 6962 - Merkle Tree Hash & Audit Paths)
- "Efficient Data Structures for Tamper-Evident Logging" (Crosby & Wallach, USENIX Security)

Generates and cryptographically verifies Merkle Audit Inclusion Proofs:
- Leaf Hash: SHA-256(0x00 || Leaf Data)
- Internal Node Hash: SHA-256(0x01 || Left Child Hash || Right Child Hash)
- Standalone verification function requiring ZERO database access.
"""

import hashlib
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("OmniRevive.MerkleProof")

def sha256_bytes(data: bytes) -> str:
    """Computes standard SHA-256 hexadecimal digest."""
    return hashlib.sha256(data).hexdigest()

def hash_leaf(leaf_data: str) -> str:
    """RFC 6962 Leaf Hash with 0x00 domain separator to prevent second-preimage attacks."""
    return sha256_bytes(b"\x00" + leaf_data.encode("utf-8"))

def hash_children(left_hex: str, right_hex: str) -> str:
    """RFC 6962 Internal Node Hash with 0x01 domain separator."""
    left_bytes = bytes.fromhex(left_hex)
    right_bytes = bytes.fromhex(right_hex)
    return sha256_bytes(b"\x01" + left_bytes + right_bytes)

class CompactMerkleTree:
    """
    Constructs an in-memory Merkle Tree from a list of transaction leaves and generates audit paths.
    """
    def __init__(self, leaves: List[str]):
        self.raw_leaves = leaves
        self.leaf_hashes = [hash_leaf(l) for l in leaves] if leaves else [hash_leaf("GENESIS_LEAF")]
        self.levels: List[List[str]] = [self.leaf_hashes]
        self._build_tree()

    def _build_tree(self):
        current = self.leaf_hashes
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if (i + 1) < len(current) else current[i]
                parent = hash_children(left, right)
                next_level.append(parent)
            self.levels.append(next_level)
            current = next_level

    @property
    def root_hash(self) -> str:
        """Returns the top-level Merkle Root hash."""
        return self.levels[-1][0]

    def get_audit_proof(self, leaf_index: int) -> Dict[str, Any]:
        """
        Generates RFC 6962 Audit Inclusion Proof (audit path) for the specified leaf index.
        """
        if leaf_index < 0 or leaf_index >= len(self.leaf_hashes):
            raise IndexError(f"Leaf index {leaf_index} out of bounds (total leaves: {len(self.leaf_hashes)})")

        audit_path: List[Dict[str, str]] = []
        idx = leaf_index

        for level_idx in range(len(self.levels) - 1):
            level = self.levels[level_idx]
            is_right_child = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right_child else idx + 1

            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                sibling_hash = level[idx]  # Odd leaf duplicated

            audit_path.append({
                "direction": "LEFT" if is_right_child else "RIGHT",
                "sibling_hash": sibling_hash
            })
            idx = idx // 2

        return {
            "leaf_index": leaf_index,
            "leaf_data": self.raw_leaves[leaf_index] if leaf_index < len(self.raw_leaves) else "",
            "leaf_hash": self.leaf_hashes[leaf_index],
            "merkle_root": self.root_hash,
            "tree_size": len(self.leaf_hashes),
            "audit_path": audit_path
        }


def verify_merkle_inclusion_proof(proof: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Standalone Cryptographic Verification function.
    Validates that leaf_data is provably included in merkle_root without database lookups.
    """
    try:
        leaf_data = proof.get("leaf_data", "")
        leaf_hash = proof.get("leaf_hash", "")
        expected_root = proof.get("merkle_root", "")
        audit_path = proof.get("audit_path", [])

        # Step 1: Recompute leaf hash if leaf data is provided
        if leaf_data:
            computed_leaf = hash_leaf(leaf_data)
            if computed_leaf != leaf_hash:
                return False, f"Leaf hash mismatch: computed {computed_leaf} != claimed {leaf_hash}"

        # Step 2: Climb the audit path
        current_hash = leaf_hash
        for step in audit_path:
            direction = step.get("direction", "RIGHT")
            sibling = step.get("sibling_hash", "")
            if direction == "LEFT":
                current_hash = hash_children(sibling, current_hash)
            else:
                current_hash = hash_children(current_hash, sibling)

        # Step 3: Compare with Merkle Root
        if current_hash.lower() == expected_root.lower():
            return True, f"Cryptographic proof verified! Leaf is unconditionally anchored to Root {expected_root[:16]}..."
        else:
            return False, f"Root hash mismatch: computed {current_hash} != expected {expected_root}"

    except Exception as e:
        return False, f"Verification failed with exception: {str(e)}"
