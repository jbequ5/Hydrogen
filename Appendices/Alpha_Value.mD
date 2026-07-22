# TOKEN_VALUE_ACCRUAL.md

**Carbon PDE Subnet — Alpha Value Accrual Design**

**Version:** 1.0 (July 2026)
**Status:** Draft for team review
**Companion documents:** `TRUSTLESS_VERIFICATION_AND_DATA_GENERATION.md`, `docs/EMISSIONS.md`, GTM / Sponsored Challenge model

This document defines how the Carbon alpha token accrues value from real network activity — usage, revenue, and access — rather than from speculation alone. Under dTAO, emissions follow alpha price; this design is therefore core infrastructure, not tokenomics decoration.

---

## 1. The Accrual Test

Every proposed mechanism must pass one test:

> **Does someone need to acquire or lock alpha because of what the network does, at a rate proportional to how much the network is used?**

If the causal chain routes through "and then the price rises, so people buy" — the mechanism is speculation in costume and is rejected. Mechanisms below are ranked by how strongly they pass.

A second constraint applies throughout: **no mechanism may resemble a profit distribution to passive holders.** All flows are structured as usage payments, access gates, or network-internal incentive routing. See Section 8 (Legal Guardrails).

---

## 2. Mechanism Summary

| # | Mechanism | Demand type | Scales with | Priority |
|---|-----------|-------------|-------------|----------|
| 1 | Revenue-Settled Buybacks | Buy pressure (cash-linked) | Sponsored Challenge revenue | **Phase 0 — designed in** |
| 2 | Verification Gas | Buy pressure (usage-linked) | Model usage everywhere, incl. partner channels | **Phase 1 — designed in** |
| 3 | Staking-for-Access | Supply lock | Miner + enterprise participation | Phase 0 (already partially specified) |
| 4 | Alpha-Vested Data & IP Royalties | Supply lock + aligned holders | Data market + model licensing | Phase 1 |
| 5 | Sponsor Bonds & Escrowed Bounties | Supply lock (visible TVL) | Sponsored Challenge volume | Phase 1 |

Mechanisms 1 and 2 are the primary pair. The design goal is two mechanisms that demonstrably work, not six that exist on paper.

---

## 3. Mechanism 1 — Revenue-Settled Buybacks (Buyback-and-Make)

**Principle:** Enterprises pay the operating company in fiat (they will not procure in alpha). A fixed, published percentage of every Sponsored Challenge fee is used to purchase alpha on the open market, and the purchased alpha funds the bounty pool that pays miners for that challenge.

**Flow:**

```
Customer (USD) ──► OpCo ──► [X]% market buy of alpha ──► Challenge bounty pool ──► Miners
```

**Properties:**
- Every commercial win is mechanical, auditable buy pressure.
- Commercial success and token demand become the same event.
- This is incentive routing (buyback-and-make), not profit distribution — revenue is converted into the network's own reward engine.

**Parameters to fix before launch:**
- Buyback ratio `X` (initial proposal: 20–40% of challenge fees; final number set with the validator-economics model).
- Execution policy (TWAP over N days to avoid manipulation claims; public wallet).
- Public reporting: every buyback posted with challenge ID, amount, and transaction references.

**Test result:** PASS — demand is proportional to revenue, which is proportional to network usefulness.

---

## 4. Mechanism 2 — Verification Gas

**Principle:** The trustless verification registry — the audit trail that every "Carbon Verified" claim resolves against (seeds, gate results, model provenance) — is Carbon-owned infrastructure. Alpha is the metering unit for programmatic access to it.

**Metered events (examples):**
- Badge resolution: a partner platform (e.g., a tooling marketplace) displays "Carbon Verified" and resolves the claim against the registry.
- Model card retrieval and validity-domain queries via API.
- Re-verification events (new generator version, updated gates) for models in the field.
- Third-party audit queries against historical evaluations.

**Properties:**
- Demand scales with **usage of Carbon models everywhere**, not only with sales. A model distributed free through a partner channel still generates verification lookups for its entire deployed life.
- Deepens the distribution strategy: partners integrate the registry once; gas is paid at the integration layer (invisible to end users; partners may bulk-purchase).
- This is the pattern of a token metering a trust primitive. Carbon's differentiator *is* a trust primitive, so the mechanism is native rather than bolted on.

**Parameters to fix:**
- Per-event pricing (denominated small; target: invisible at the single-lookup level, material at platform scale).
- Bulk/prepaid tiers for partners.
- Free tier for public, human, non-programmatic verification (the public trust page must never be paywalled — credibility outranks revenue here).

**Test result:** PASS — demand is proportional to real-world model usage.

---

## 5. Mechanism 3 — Staking-for-Access

**Principle:** Extend the staking hooks already present in the diagnostic-tier design (rich diagnostics gated by "additional rate-limiting/staking") into a coherent access system.

**Miner side:**
- Stake for rich diagnostic tier access.
- Stake for priority evaluation slots during congestion.

**Enterprise / partner side:**
- Stake for early access to frontier-tier (Graphene) models.
- Stake for priority Sponsored Challenge scheduling.
- Stake for SLA-backed registry query capacity (interacts with Mechanism 2).

**Properties:** Locks supply and defers sell pressure rather than creating demand; weakest of the primary mechanisms but cheapest to implement and already half-specified.

**Test result:** PARTIAL PASS — locks are proportional to participation, but do not create new demand on their own. Deploy as a complement, never as the headline.

---

## 6. Mechanism 4 — Alpha-Vested Data & IP Royalties

**Principle:** The network's most defensible asset flows (proprietary data contributions; miner-originated model IP) are compensated in alpha with vesting, converting the people who build the moat into structurally aligned long-term holders.

**Data market (Phase 1):**
- Data royalties (impact-proportional, per the data market design) are paid in alpha, streamed or time-locked rather than lump-sum.

**Miner IP (Sponsored Challenges):**
- Participation terms assign commercial model rights to the challenge sponsor / OpCo (resolving the IP-chain gap identified in the repo review).
- In exchange, the winning miner receives an ongoing alpha-denominated royalty on commercial licensing of that model, funded by OpCo market buys (a usage-linked extension of Mechanism 1).
- Every license renewal becomes recurring buy pressure; miners accept assignment because they keep upside.

**Test result:** PASS (secondary) — aligns supply-side incentives and recycles licensing revenue into demand.

---

## 7. Mechanism 5 — Sponsor Bonds & Escrowed Bounties

**Principle:** Tier 3/4 challenge sponsors post a refundable alpha bond for challenge integrity; breakthrough bounties sit in on-chain escrow until won.

**Properties:**
- Modest supply lock, but produces a legible public metric: **open bounty TVL** — "$X of live, funded physics problems on Carbon." This number is a narrative asset for the staking audience and grows with commercial traction.
- Refundable structure keeps sponsor friction low.

**Test result:** PARTIAL PASS — small direct effect; high visibility value.

---

## 8. Sell-Side Management

Buy pressure is half the equation. Miner emissions are constant structural sell pressure and are treated as COGS (per the GTM model). Mitigations:

- **Vested emission schedules** where subnet mechanics permit — reward streams over epochs rather than lump payouts.
- **Decaying stipend + minimum-improvement rules** (already implemented in `emission/mechanics.py`) — emissions concentrate on genuine progress, reducing farm-and-dump flow.
- **Reputation weighting** (future): held-stake history modestly improves diagnostic tier or priority access (interacts with Mechanism 3), rewarding miners who hold without promising financial return.

Halving sell pressure is mathematically equivalent to doubling buy pressure and is usually cheaper to engineer.

---

## 9. Sequencing Honesty

In Phase 0, alpha price will be driven predominantly by narrative regardless of this design: verification gas at zero deployed models produces zero demand; buybacks at zero revenue produce zero buys.

The failure mode is not "relying on narrative early" — that is unavoidable. The failure mode is narrative without a credible machine behind it. Therefore:

- The buyback ratio and verification-gas specification are **published before launch**, with live public counters starting at zero.
- The story told to stakers is: *"here is the machine; watch the numbers turn on"* — not *"trust us, utility is coming."*
- No mechanism is announced that is not specified to the parameter level in this document.

---

## 10. Legal Guardrails

- Nothing in this design entitles passive holders to a share of revenue or profit. All flows are usage payments, access gates, or incentive routing.
- Buybacks fund miner rewards (network operation), and are executed on a published schedule to avoid market-manipulation exposure.
- Enterprise payment rails are fiat-first through the OpCo; alpha-denominated payment is an option for crypto-native sponsors only.
- **This entire design requires review by specialist counsel before any public commitment**, particularly regarding securities treatment in the US and the jurisdictions of likely investors. This document is a mechanism specification, not legal or financial advice.

---

## 11. Anti-Patterns (Explicitly Rejected)

- **Revenue-share / dividend framing** — securities exposure; rejected.
- **Burn theatrics** — burns without usage linkage are speculation dressed as scarcity; rejected.
- **Alpha-only enterprise pricing** — procurement reality; rejected.
- **Paywalled public verification** — the trust page stays free forever; only programmatic/platform access is metered.
- **Announcing unbuilt mechanisms** — see Section 9.

---

## 12. Relationship to Other Systems

- **Trustless Verification System:** the registry it produces is the asset Mechanism 2 meters.
- **ChallengeWinnerTracker / emission mechanics:** the routing target for Mechanism 1 buybacks; implements the sell-side rules in Section 8.
- **Sponsored Challenge GTM:** the revenue source for Mechanism 1 and the context for Mechanisms 4–5; the miner IP terms in Section 6 resolve the participation-agreement gap.
- **Distribution partnerships:** Mechanism 2 is the monetization layer of the ingredient-brand strategy — partners carry the models; the registry (and its gas) stays home.

---

## 13. Public Metrics Dashboard (Launch Requirement)

The following go live with the subnet, starting at zero:

| Metric | Source |
|--------|--------|
| Cumulative buyback volume (alpha + USD) | Mechanism 1 |
| Registry queries / badge resolutions (30d) | Mechanism 2 |
| Total alpha staked for access | Mechanism 3 |
| Open bounty TVL | Mechanism 5 |
| Emissions paid vs. revenue recycled | Sections 3 + 8 |

Zeros on a public dashboard are a statement of intent. Rising numbers are the end of the speculation argument.

---

*This document follows the accrual test strictly: if a mechanism's value chain routes through price appreciation rather than network usage, it does not ship.*
