#!/usr/bin/env python3
"""Public stub for verifying the engine's signed pharma provenance bundle.

The signed Sigstore bundle and its offline verification logic live in the
private engine repository. This public module returns only a stable hint that
describes how a consumer can verify the bundle once the operator publishes it.
"""

from __future__ import annotations

import sys

VERIFICATION_HINT = (
    "The public repository does not ship a signed provenance bundle. "
    "To verify the engine's NPRA pharma graph, request the signed Sigstore "
    "bundle from the operator and run: cosign verify-blob --bundle "
    "<bundle.sigstore.json> --certificate-identity <expected-identity> "
    "--certificate-oidc-issuer <expected-issuer> <graph.json>"
)


def verification_hint() -> str:
    """Return the stable public verification hint."""
    return VERIFICATION_HINT


def main() -> int:
    print(verification_hint())
    return 0


if __name__ == "__main__":
    sys.exit(main())
