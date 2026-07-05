"""MESIE market commerce — 4K catalog, checkout, sovereign access vault."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.version_info import MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]
MARKET_DIR = ROOT / "deliverables" / "market"
CATALOG_PATH = MARKET_DIR / "MARKET_PRICING_CATALOG.json"
CHECKOUT_DIR = MARKET_DIR / "checkouts"
ACCESS_VAULT = MARKET_DIR / "ACCESS_VAULT.json"
ACCESS_FEED = MARKET_DIR / "ACCESS_FEED.jsonl"
PROTOCOL = "MESIE-MARKET-COMMERCE/1.0"
BRAND = "ItsnotAILabs"

PRICING_TIERS: Dict[str, Dict[str, Any]] = {
    "starter": {
        "tier_id": "starter",
        "label": "Starter",
        "period": "month",
        "description": "Single product · dev sandbox · community support",
    },
    "pro": {
        "tier_id": "pro",
        "label": "Pro",
        "period": "month",
        "description": "Production SLA · MCP federation · priority support",
    },
    "sovereign": {
        "tier_id": "sovereign",
        "label": "Sovereign",
        "period": "year",
        "description": "Airgap deploy · dual-chain receipts · dedicated onboarding",
    },
}

# USD list prices per business SKU × tier
SKU_PRICES: Dict[str, Dict[str, int]] = {
    "MESIE-VP-ENT": {"starter": 149, "pro": 799, "sovereign": 8999},
    "MESIE-UAI-MCP": {"starter": 99, "pro": 499, "sovereign": 5999},
    "MESIE-CAREER-1K": {"starter": 79, "pro": 399, "sovereign": 4999},
    "NOVA-RT-70": {"starter": 199, "pro": 999, "sovereign": 11999},
    "CC-SOV-ICP": {"starter": 249, "pro": 1299, "sovereign": 14999},
    "MESIE-SUITE": {"starter": 499, "pro": 2499, "sovereign": 24999},
}

ACCESS_SURFACES: Dict[str, List[str]] = {
    "MESIE-VP-ENT": [
        "websites/platform-hub/index.html",
        "websites/computing-family/index.html",
        "websites/virtual-silicon/index.html",
    ],
    "MESIE-UAI-MCP": ["websites/hermes-fleet/index.html", "websites/market-hub/index.html"],
    "MESIE-CAREER-1K": ["websites/career-portal/index.html"],
    "NOVA-RT-70": ["websites/producer-lab/index.html", "websites/model-hub/index.html"],
    "CC-SOV-ICP": ["sovereign-os/dashboard/index.html", "websites/enterprise-4k/index.html"],
    "MESIE-SUITE": [
        "websites/platform-hub/index.html",
        "websites/enterprise-4k/index.html",
        "websites/market-hub/index.html",
        "websites/career-portal/index.html",
        "websites/hermes-fleet/index.html",
        "websites/producer-lab/index.html",
    ],
}


@dataclass
class CheckoutSession:
    checkout_id: str
    sku: str
    tier: str
    email: str
    amount_usd: int
    currency: str = "usd"
    status: str = "pending"
    payment_method: str = "sovereign"
    stripe_session_id: Optional[str] = None
    stripe_checkout_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    completed_at: Optional[str] = None
    access_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_businesses() -> List[Dict[str, Any]]:
    path = MARKET_DIR / "FIVE_BUSINESSES.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("businesses", []))


def _suite_product() -> Dict[str, Any]:
    return {
        "id": "biz-suite",
        "name": "MESIE Sovereign Suite",
        "sku": "MESIE-SUITE",
        "tagline": "All five businesses — processor, MCP, careers, NOVA, sovereign cloud",
        "category": "Full Stack / Sovereign AI Platform",
        "website": "websites/market-4k/",
        "proof": {"businesses": 5, "version": MESIE_VERSION},
    }


def build_pricing_catalog(*, write: bool = False) -> Dict[str, Any]:
    businesses = _load_businesses()
    products: List[Dict[str, Any]] = []
    for biz in businesses:
        sku = biz["sku"]
        prices = SKU_PRICES.get(sku, {})
        plans = []
        for tier_id, meta in PRICING_TIERS.items():
            if tier_id not in prices:
                continue
            plans.append({
                **meta,
                "price_usd": prices[tier_id],
                "sku": sku,
                "access_surfaces": ACCESS_SURFACES.get(sku, []),
            })
        products.append({
            "sku": sku,
            "name": biz["name"],
            "tagline": biz.get("tagline", ""),
            "category": biz.get("category", ""),
            "proof": biz.get("proof", {}),
            "website": biz.get("website", ""),
            "plans": plans,
        })

    suite = _suite_product()
    suite_prices = SKU_PRICES["MESIE-SUITE"]
    suite_plans = [
        {**PRICING_TIERS[tier_id], "price_usd": suite_prices[tier_id], "sku": "MESIE-SUITE",
         "access_surfaces": ACCESS_SURFACES["MESIE-SUITE"]}
        for tier_id in PRICING_TIERS if tier_id in suite_prices
    ]
    products.append({**suite, "plans": suite_plans})

    catalog = {
        "protocol": PROTOCOL,
        "version": MESIE_VERSION,
        "brand": BRAND,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "currency": "usd",
        "pricing_tiers": list(PRICING_TIERS.values()),
        "products": products,
        "payment_methods": _payment_methods(),
        "access_flow": {
            "checkout": "POST /processor/market/checkout",
            "complete": "POST /processor/market/checkout/complete",
            "verify": "POST /processor/market/access",
            "catalog": "GET /processor/market/catalog",
        },
        "websites": {
            "marketing_4k": "websites/market-4k/index.html",
            "access_portal": "websites/market-access/index.html",
            "serve_script": "scripts/serve_market_sites.ps1",
            "local_port": 8780,
        },
    }
    if write:
        MARKET_DIR.mkdir(parents=True, exist_ok=True)
        CATALOG_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog


def _payment_methods() -> List[Dict[str, Any]]:
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    return [
        {
            "id": "sovereign",
            "label": "Sovereign Checkout",
            "description": "Local receipt + access key mint (demo/production-local)",
            "available": True,
        },
        {
            "id": "stripe",
            "label": "Stripe",
            "description": "Card checkout via Stripe Checkout Sessions",
            "available": bool(stripe_key),
            "env": "STRIPE_SECRET_KEY",
        },
    ]


def _checkout_path(checkout_id: str) -> Path:
    CHECKOUT_DIR.mkdir(parents=True, exist_ok=True)
    return CHECKOUT_DIR / f"{checkout_id}.json"


def _save_checkout(session: CheckoutSession) -> None:
    _checkout_path(session.checkout_id).write_text(
        json.dumps(session.to_dict(), indent=2) + "\n", encoding="utf-8"
    )


def _load_checkout(checkout_id: str) -> Optional[CheckoutSession]:
    path = _checkout_path(checkout_id)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return CheckoutSession(**{k: v for k, v in data.items() if k in CheckoutSession.__dataclass_fields__})


def _mint_access_key(*, sku: str, tier: str, email: str) -> str:
    seed = f"{sku}:{tier}:{email}:{secrets.token_hex(8)}"
    digest = hashlib.sha256(seed.encode()).hexdigest()[:20].upper()
    return f"MESIE-{digest}"


def _stripe_create_session(
    *,
    checkout_id: str,
    sku: str,
    tier: str,
    email: str,
    amount_usd: int,
    success_url: str,
    cancel_url: str,
) -> Dict[str, Any]:
    secret = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not secret:
        return {"ok": False, "error": "STRIPE_SECRET_KEY not configured"}

    payload = urllib.parse.urlencode({
        "mode": "payment",
        "customer_email": email,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": checkout_id,
        "line_items[0][price_data][currency]": "usd",
        "line_items[0][price_data][unit_amount]": str(amount_usd * 100),
        "line_items[0][price_data][product_data][name]": f"{sku} — {tier}",
        "line_items[0][price_data][product_data][description]": f"MESIE {tier} plan · {BRAND}",
        "line_items[0][quantity]": "1",
        "metadata[checkout_id]": checkout_id,
        "metadata[sku]": sku,
        "metadata[tier]": tier,
    }).encode()

    req = urllib.request.Request(
        "https://api.stripe.com/v1/checkout/sessions",
        data=payload,
        headers={
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode())
        return {
            "ok": True,
            "session_id": body.get("id"),
            "checkout_url": body.get("url"),
        }
    except urllib.error.HTTPError as exc:
        err = exc.read().decode()[:400]
        return {"ok": False, "error": f"stripe_http_{exc.code}", "detail": err}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def create_checkout(
    *,
    sku: str,
    tier: str,
    email: str,
    payment_method: str = "sovereign",
    success_url: str = "http://127.0.0.1:8780/market-access/?paid=1",
    cancel_url: str = "http://127.0.0.1:8780/market-4k/?cancelled=1",
) -> Dict[str, Any]:
    prices = SKU_PRICES.get(sku)
    if not prices or tier not in prices:
        known = ", ".join(sorted(SKU_PRICES))
        return {"ok": False, "error": f"unknown sku/tier: {sku}/{tier}", "known_skus": known}

    amount = prices[tier]
    checkout_id = f"chk_{secrets.token_hex(8)}"
    session = CheckoutSession(
        checkout_id=checkout_id,
        sku=sku,
        tier=tier,
        email=email.strip().lower(),
        amount_usd=amount,
        payment_method=payment_method,
    )

    stripe_url: Optional[str] = None
    if payment_method == "stripe":
        stripe = _stripe_create_session(
            checkout_id=checkout_id,
            sku=sku,
            tier=tier,
            email=email,
            amount_usd=amount,
            success_url=f"{success_url}&checkout_id={checkout_id}",
            cancel_url=cancel_url,
        )
        if not stripe.get("ok"):
            return {"ok": False, "error": stripe.get("error", "stripe_failed"), "detail": stripe.get("detail")}
        session.stripe_session_id = stripe.get("session_id")
        session.stripe_checkout_url = stripe.get("checkout_url")
        stripe_url = session.stripe_checkout_url

    _save_checkout(session)
    return {
        "ok": True,
        "checkout_id": checkout_id,
        "sku": sku,
        "tier": tier,
        "amount_usd": amount,
        "currency": "usd",
        "payment_method": payment_method,
        "status": "pending",
        "stripe_checkout_url": stripe_url,
        "complete_endpoint": "POST /processor/market/checkout/complete",
        "message": "Complete checkout to receive your access key.",
    }


def complete_checkout(
    *,
    checkout_id: str,
    payment_ref: Optional[str] = None,
) -> Dict[str, Any]:
    session = _load_checkout(checkout_id)
    if not session:
        return {"ok": False, "error": "checkout_not_found"}
    if session.status == "completed" and session.access_key:
        ent = verify_access(access_key=session.access_key, email=session.email)
        return {
            "ok": True,
            "already_completed": True,
            "checkout_id": checkout_id,
            "access_key": session.access_key,
            "entitlements": ent.get("entitlements", []),
        }

    access_key = _mint_access_key(sku=session.sku, tier=session.tier, email=session.email)
    session.status = "completed"
    session.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    session.access_key = access_key
    _save_checkout(session)

    entitlement = _grant_access(
        access_key=access_key,
        sku=session.sku,
        tier=session.tier,
        email=session.email,
        amount_usd=session.amount_usd,
        payment_ref=payment_ref or f"sovereign:{checkout_id}",
    )

    try:
        from mesie.tokens.dual_bridge import DualTokenBridge

        DualTokenBridge().mint_internal(
            "MESIE-LRC",
            float(session.amount_usd),
            {"type": "market_checkout", "checkout_id": checkout_id, "sku": session.sku, "tier": session.tier},
        )
    except Exception:
        pass

    return {
        "ok": True,
        "checkout_id": checkout_id,
        "access_key": access_key,
        "entitlements": [entitlement],
        "access_portal": "websites/market-access/index.html",
        "surfaces": ACCESS_SURFACES.get(session.sku, []),
    }


def _load_vault() -> Dict[str, Any]:
    if ACCESS_VAULT.is_file():
        try:
            return json.loads(ACCESS_VAULT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"protocol": PROTOCOL, "grants": []}


def _save_vault(vault: Dict[str, Any]) -> None:
    MARKET_DIR.mkdir(parents=True, exist_ok=True)
    vault["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ACCESS_VAULT.write_text(json.dumps(vault, indent=2) + "\n", encoding="utf-8")


def _grant_access(
    *,
    access_key: str,
    sku: str,
    tier: str,
    email: str,
    amount_usd: int,
    payment_ref: str,
) -> Dict[str, Any]:
    vault = _load_vault()
    period = PRICING_TIERS.get(tier, {}).get("period", "month")
    days = 365 if period == "year" else 30
    expires = time.time() + days * 86400
    grant = {
        "access_key": access_key,
        "sku": sku,
        "tier": tier,
        "email": email,
        "amount_usd": amount_usd,
        "payment_ref": payment_ref,
        "surfaces": ACCESS_SURFACES.get(sku, []),
        "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expires)),
        "active": True,
    }
    vault.setdefault("grants", []).append(grant)
    _save_vault(vault)
    ACCESS_FEED.parent.mkdir(parents=True, exist_ok=True)
    with ACCESS_FEED.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"event": "grant", **grant}, separators=(",", ":")) + "\n")
    return grant


def verify_access(*, access_key: str, email: Optional[str] = None) -> Dict[str, Any]:
    vault = _load_vault()
    key = access_key.strip().upper()
    matches = [g for g in vault.get("grants", []) if g.get("access_key") == key and g.get("active")]
    if not matches:
        return {"ok": False, "valid": False, "error": "access_key_not_found"}
    grant = matches[-1]
    if email and grant.get("email") != email.strip().lower():
        return {"ok": False, "valid": False, "error": "email_mismatch"}
    exp = grant.get("expires_at", "")
    return {
        "ok": True,
        "valid": True,
        "entitlements": [grant],
        "sku": grant.get("sku"),
        "tier": grant.get("tier"),
        "surfaces": grant.get("surfaces", []),
        "expires_at": exp,
        "brand": BRAND,
    }


def commerce_snapshot() -> Dict[str, Any]:
    vault = _load_vault()
    pending = 0
    if CHECKOUT_DIR.is_dir():
        for p in CHECKOUT_DIR.glob("chk_*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("status") == "pending":
                    pending += 1
            except json.JSONDecodeError:
                pass
    return {
        "protocol": PROTOCOL,
        "brand": BRAND,
        "catalog_path": str(CATALOG_PATH.relative_to(ROOT)),
        "active_grants": sum(1 for g in vault.get("grants", []) if g.get("active")),
        "pending_checkouts": pending,
        "stripe_configured": bool(os.environ.get("STRIPE_SECRET_KEY", "").strip()),
        "websites": {
            "marketing_4k": "http://127.0.0.1:8780/market-4k/",
            "access_portal": "http://127.0.0.1:8780/market-access/",
        },
    }