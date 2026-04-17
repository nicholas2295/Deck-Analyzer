# Domain Knowledge — Shopee Cross-Border Operating Models

This file explains how key programs work so you can generate Ian Ho's operating-model questions. Ian always probes HOW things work, WHO owns the risk, and WHETHER it's similar to something Shopee already does.

---

## SIP (Shopee International Platform) — How It Works

### The 2-Order System
SIP acts as a purchase agent for import-market buyers. The flow:
1. Buyer in import market (e.g., MY) places an order on the SIP import shop
2. SIP uses a dummy buyer account to place a matching order on the seller's export shop (e.g., CN)
3. Seller ships to SIP; SIP handles cross-border logistics and delivers to buyer

This "2-order" design creates constraints:
- Seller vouchers: the dummy account can only collect 1 voucher per shop (legal/compliance constraint)
- Pricing: SIP sets the import listing price based on export settlement price + markup
- Returns: SIP handles CS and returns on behalf of the buyer

### SIP Standalone P&L
- Seller standalone P&L = revenue from SIP margin minus logistics, marketing, ops costs
- MP PC2 = marketplace profit from ads + commissions on SIP orders
- Total P&L = Seller standalone + MP PC2 + SLS contribution

Ian often asks: "how do we reconcile standalone P&L (negative) with total P&L (positive)?" because MP PC2 can mask seller-level losses.

### Direct Selling (vs SIP)
- In Direct model, sellers sell directly to import-market buyers via Global Seller Center
- Seller owns the shop, sets prices, manages listings
- SIP provides logistics (SLS) but doesn't act as intermediary
- Take rate: Direct sellers pay commission + ads + fees (like local MP sellers)
- Ian compares Direct take rate to local MP take rate: "can we split up TR further? into mandatory comms, optional comms, transaction fees and paid ads? and compare it with local MP?"

### SIP x LFF (Consignment Model)
- New model: SIP sources SKUs from SEA sellers, holds inventory in local FBS warehouses
- Seller retains ownership until sale; unsold = returned to seller (RTS)
- Similar to SCS LFF model (Ian always draws this comparison)
- Risk: "black stock" — unsold consigned inventory that SIP bears return/disposal cost for
- Ian asks: "who takes ownership?" / "this is probably similar to SCS LFF model?" / "how are we accounting for black stock P&L?"
- "Choice shops" — SIP LFF would run a separate shop; Ian pushes to consolidate: "should not have so many choice shops in 1 market"

---

## Swarm — How It Works

### Model
- ERP-integrated seller incubation program (JST, WDT, and other ERP partners)
- Swarm manages pricing, marketing, fulfillment for CN sellers via ERP integrations
- Sellers set settlement prices; Swarm controls listing prices via markup

### Key Metrics Ian Tracks
- Active sellers (not just leads or onboarded — must have active listings)
- SKU efficiency = ADO per active SKU
- UE (Unit Economics) = per-order profit/loss
- Ian distinguishes incubation SKUs (new, losing money) from mature SKUs (should be profitable)

### Seller Funnel
Leads (expressed interest) → Onboarded (opened shop) → Active (selling with listings)
Ian always pushes: "it is more important to understand how many sellers we are onboarding" vs counting leads

### ERP Partners
- JST: largest; ~300 sellers by Dec 2025, ~50/month growth
- WDT: smaller partner
- OF (Old Fulfillment): legacy; Ian doubts long-term value: "not sure they will be a big contributor"

---

## SCS / Lovito — How It Works

### SCS (Shopee Choice)
- Curated selection program; SCS sources and manages inventory
- LFF model: SCS holds stock in local warehouses
- P&L includes marketing, logistics, blackstock risk

### Lovito
- Fashion brand operated by SCS team
- Key concern: breakeven timing and growth pace
- Ian pushes for higher ABS (~$8-10), more Malay-focused for MY market
- IP collaborations (Disney, Barbie): Ian insists on new designs, not name-on-existing

---

## Pricing Mechanics (How SIP/Swarm Price)

### SIP Pricing
- Listing price: what the import-market buyer sees
- Settlement price: what the export-market seller receives (estimated from seller's other markets)
- The gap = SIP margin, used for marketing + logistics
- Ian's concern: "are we getting listing price (before/after discount from sellers) right now?"

### Incubation vs Mature
- Incubation SKUs: new, SIP invests in marketing to grow them; UE is negative
- Mature SKUs: established, should be UE-positive or near breakeven
- Ian asks: "why we need to lose up to 4 usd per order right now just to sell" / "Can show me how we price for incu SKUs right now (the UE breakdown)"
- Investment discipline: max 3-month incubation window

### Admin Fees / Seller Charges
- Currently SIP sellers pay little or no fees (Ian's frustration)
- Ian's direction: "we should start charging sellers for services, especially those who have used it for a while"
- Comparison: Swarm has flexible settlement price control; SIP does not

---

## Logistics Models

### SLS (Shopee Logistics Service)
- Shopee-managed cross-border shipping
- Handles first-mile pickup, cross-border transit, customs clearance, last-mile delivery
- Key metrics: CPO, BWT (Buyer Wait Time), EDT (Estimated Delivery Time)

### LFF (Last-mile Local Fulfillment)
- Stock held in import-market local warehouses
- Faster delivery, better buyer experience, but higher inventory risk
- Ian always asks about LFF % by market: "If LFF for VN can > 50%, what is stopping us from doing other markets?"

### FBS (Fulfilled by Shopee)
- Seller sends stock to Shopee warehouse; Shopee fulfills
- FBS tag on SKU improves visibility
- Ian tracks: FBS penetration vs TT/competitors; FBS tag availability for CB sellers

### 3PF (Third-Party Fulfillment)
- External fulfillment providers
- Used in markets without Shopee warehouse presence

### Key Warehouses
- NNWH (Nanning Warehouse): main CN cross-border hub
- Anbo: alternative WH; Ian compares CPO and BWT vs NNWH

---

## Cross-Program Comparisons Ian Always Draws

When Ian sees a new initiative, he ALWAYS compares it to something he knows:

| New thing | He compares to | His question |
|-----------|---------------|--------------|
| SIP LFF | SCS LFF | "this is probably similar to SCS LFF model?" |
| Swarm UE | CNSIP UE | "can help me compare with existing CNSIP?" |
| Direct take rate | Local MP take rate | "how does it compare with shops in the local market?" |
| CB FBS penetration | TT FBS penetration | "where do we stand vs TT?" |
| SIP seller fees | Local seller fees | "do they pay import or export country fees?" |
| New warehouse CPO | NNWH CPO | "CPO of Anbo is so much higher than NNWH?" |
| KR performance | JP performance | "how does the situation in JP look like?" (always asks about the other market) |

---

## Ian's Standard Questions on New Proposals

When a deck contains a new initiative or "For Discussion" item, Ian follows a predictable sequence:

1. **How does it work?** — end-to-end operating model ("who takes ownership?")
2. **Is this similar to something we already do?** — cross-program comparison
3. **Who owns the risk?** — inventory, returns, black stock, P&L responsibility
4. **Is the upside worth the complexity?** — ROI skepticism ("3K ADO does not feel very high")
5. **Has this been aligned with other teams?** — cross-team coordination
6. **What are the assumptions?** — "what oil prices are we modelling for here?"
