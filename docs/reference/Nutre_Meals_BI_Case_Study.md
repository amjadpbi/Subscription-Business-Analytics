# Nutre Meals — Subscription BI Case Study
## Project Context for Claude

**Built by:** Muhammad Amjad — Power BI Specialist  
**Project type:** Portfolio project targeting subscription business sector  
**Primary target:** Nutre Meals (gonutre.com) — open Upwork project, posted 3 months ago, no hire shown  
**Secondary value:** Reusable for any subscription business client going forward  
**Stack:** Python (Google Colab) → SQL Server (SSMS) → Power BI Desktop  
**Status:** Dataset generated. SQL schema and import next. Executive Overview page first.

---

## Why This Project Exists

An Upwork job post from Nutre Meals (a subscription meal delivery company in Massachusetts, USA) has been open for three months with no hire. Client stats are strong: 5.0 rating, 17 reviews, 100% hire rate, $26K spent, $41/hr average paid. The job requires a BI developer to build four dashboards from scratch, starting with an Executive Overview as a paid proof of concept.

The strategy: build a working Executive Overview demo using simulated Nutre data before submitting a proposal. A working demo breaks through where proposals do not. If Nutre responds, good. If not, the project stands as a portfolio piece for the subscription business sector — a large and growing market beyond the original franchise and retail niche.

This project also deliberately expands the positioning from "franchise and retail BI" to problem-based framing: "I help businesses replace manual reporting with automated BI solutions." Subscription businesses, franchise operations, and retail all share the same core pain. The industry is secondary. The problem is the positioning.

---

## About Nutre Meals

**Website:** gonutre.com  
**Founded:** 2017 by the Perrina Brothers in Peabody, Massachusetts  
**Origin story:** Founded after their father's diabetes diagnosis. Clean eating transformed his health. They built Nutre to share that with others.  
**Model:** Weekly subscription meal delivery. Fresh, never frozen. Chef-prepared, dietician-approved.  
**Menu:** 50+ rotating meals and snacks per week  
**Delivery:** Two channels. Hand delivery in the Northeast (personal drivers). National shipping via FedEx and OnTrac for the rest of the US.  
**B2B:** Corporate office meal delivery. Hospitals, senior care, and office teams. Growing channel.  
**Cancellation:** No hidden fees. Cancel anytime. Weekly skip option available.  
**Order deadline:** Wednesday 11:59 PM each week  
**Shelf life:** 7 to 12 days refrigerated. Can be frozen.

**Primary meal plan categories:**
- Balance — general healthy eating
- Weight Loss — under 500 calories per meal
- Plant Based — vegan and dairy-free friendly

**Dietary filters (applied on top of plan category):**
- Gluten Friendly, Dairy Free, Low Sodium, Diabetic Friendly, Carb Conscious, Calorie Smart, Seafood Cautious, Soy Cautious, Nut Cautious, Egg Cautious

**Enthusiast Program:** Gym owners and personal trainers in the Boston area refer clients. They receive free meals plus 10% commission on sales generated. This is a real acquisition channel embedded in the dataset.

**Promo:** First 3 weeks get $40 off per week. This is in the dataset as DiscountAmount.

---

## The Upwork Job Post — What Was Asked For

**Budget:** $8,000 to $15,000 full project. $30 to $50 per hour for the right candidate.  
**Timeline:** 8 to 12 weeks.  
**Hidden filter phrase:** Proposals must start with "The secret ingredient is data." Most applicants miss this.

**Four dashboards required:**
1. Executive Overview — Phase 1 proof of concept (paid milestone)
2. Marketing and Sales
3. Operations and Logistics
4. Customer Success and Retention

**Metrics explicitly named in the post:**
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue)
- LTV (Lifetime Value)
- CAC (Customer Acquisition Cost)
- Churn rate
- Cohort analysis

**Required skills:** Expert Power BI (or Tableau or Looker), strong SQL, ETL experience, proven subscription business experience, English communication, independent work.

**Long-term potential:** They want an ongoing partner, not a one-off hire.

**Building in Power BI.** Power BI is the tool of choice.

---

## Dataset Design Decisions

### Why 2023 to 2024 (not 9 years)

Nutre was founded 2017. Using 9 years of data would require simulating an early-stage startup with 30 subscribers and no national shipping. That era has fundamentally different business characteristics. The dashboard answers current operational questions, not historical archaeology.

By January 2023, Nutre is an established regional business. The dataset starts with 450 existing active subscribers, reflecting 6 years of real-world growth. Their tenure is back-dated realistically (3 months to 5 years before 2023).

Two full years (104 weeks) gives two complete January spikes, two full seasonal cycles, and enough cohort history to show 12-month retention curves. That is sufficient for every metric the job post requires.

### Why weekly time grain (not daily or monthly)

Nutre operates on a weekly cycle. Every subscriber has a status every week: new, active, skipped, or churned. Daily grain adds no analytical value because nothing meaningful happens at the daily level for subscriptions. Monthly grain loses the skip signal — the most important leading indicator of churn. Weekly grain captures everything.

MRR is a monthly metric but is calculated from weekly data in Power BI using DAX. One measure, not a separate table.

### Why one central fact table

FactSubscriptionWeekly is the heartbeat of the entire dataset. One row per subscriber per week. Every metric required by the job post can be answered from this single table joined to the five dimensions. Complexity is not depth. This was a deliberate choice over building multiple fact tables.

### Why ConsecutiveSkips and WeeksActive are NOT in the fact table

These fields are intentionally excluded from the dataset. They must be calculated using SQL before connecting to Power BI. This is the SQL learning objective for this project. Window functions (LAG, ROW_NUMBER) are required. Learning these on a real business problem is faster than learning from tutorials.

---

## Data Model — Star Schema

### FactSubscriptionWeekly

One row per subscriber per week. Stops when subscriber churns.

| Column | Type | Description |
|--------|------|-------------|
| FactID | INT | Surrogate primary key |
| SubscriberID | INT | FK to DimSubscriber |
| WeekID | INT | FK to DimDate |
| PlanID | INT | FK to DimPlan |
| DeliveryChannelID | INT | FK to DimDeliveryChannel |
| AcquisitionChannelID | INT | FK to DimAcquisitionChannel |
| Status | VARCHAR | New, Active, Skipped, Churned |
| WeeklyRevenue | DECIMAL | 0 if Skipped or Churned |
| MealsOrdered | INT | 0 if Skipped or Churned |
| DiscountAmount | DECIMAL | $40 discount for first 3 weeks |
| IsFirstWeek | BIT | 1 on subscriber's first week in dataset |
| IsChurnWeek | BIT | 1 on the week subscriber cancels |

**Status values explained:**
- New — subscriber's first week in the dataset
- Active — normal week, order placed, revenue generated
- Skipped — subscriber paused this week, no revenue, still subscribed
- Churned — subscriber cancelled, no further rows

### DimSubscriber

| Column | Type | Description |
|--------|------|-------------|
| SubscriberID | INT | Primary key |
| JoinDate | DATE | Actual join date (pre-2023 for existing base) |
| JoinWeekID | INT | Week they first appear in our dataset |
| DeliveryChannelID | INT | FK to DimDeliveryChannel |
| AcquisitionChannelID | INT | FK to DimAcquisitionChannel |
| PlanID | INT | FK to DimPlan |
| MealPreference | VARCHAR | Balance, Weight Loss, Plant Based, Diabetic Friendly |
| State | VARCHAR | US state abbreviation |
| AgeGroup | VARCHAR | 18-24, 25-34, 35-44, 45-54, 55-64 |
| Gender | VARCHAR | Female, Male, Not Specified |
| IsGlutenFree | BIT | Dietary filter flag |
| IsDairyFree | BIT | Dietary filter flag |
| IsLowSodium | BIT | Dietary filter flag |

### DimDate

| Column | Type | Description |
|--------|------|-------------|
| WeekID | INT | Primary key (1 to 104) |
| WeekStartDate | DATE | Monday of the week |
| WeekEndDate | DATE | Sunday of the week |
| Month | INT | Month number 1-12 |
| MonthName | VARCHAR | January, February, etc. |
| Quarter | VARCHAR | Q1, Q2, Q3, Q4 |
| Year | INT | 2023 or 2024 |
| WeekOfYear | INT | ISO week number |
| IsJanuarySpike | BIT | 1 for first 3 weeks of January |
| IsHolidaySeason | BIT | 1 for mid-November through December |
| IsSummer | BIT | 1 for June, July, August |

### DimPlan

| Column | Type | Description |
|--------|------|-------------|
| PlanID | INT | Primary key |
| PlanName | VARCHAR | e.g. 5 Meals / Week |
| MealsPerWeek | INT | 5, 8, 10, 12, 15, 20, 40 (B2B) |
| WeeklyPrice | DECIMAL | Full weekly price before discount |
| PricePerMeal | DECIMAL | Per-meal rate (volume discount applied) |

**Plan pricing:**

| Plan | Meals/Week | Weekly Price | Per Meal |
|------|-----------|--------------|----------|
| 1 | 5 | $80 | $16.00 |
| 2 | 8 | $112 | $14.00 |
| 3 | 10 | $130 | $13.00 |
| 4 | 12 | $150 | $12.50 |
| 5 | 15 | $180 | $12.00 |
| 6 | 20 | $220 | $11.00 |
| 7 (B2B) | 40 | $400 | $10.00 |

### DimDeliveryChannel

| ChannelID | ChannelName | DeliveryType | Region |
|-----------|-------------|--------------|--------|
| 1 | Hand Delivery | Personal | Northeast US |
| 2 | National Shipping | Carrier (FedEx/OnTrac) | United States |
| 3 | B2B Corporate | Corporate | Mixed |

### DimAcquisitionChannel

| ChannelID | ChannelName | Estimated CAC | LTV Multiplier |
|-----------|-------------|---------------|----------------|
| 1 | Referral | $15 | 1.4x |
| 2 | Enthusiast Program | $20 | 1.5x |
| 3 | Paid Social | $85 | 0.9x |
| 4 | Organic Search | $35 | 1.2x |
| 5 | Gift Subscription | $0 | 0.6x |
| 6 | B2B Corporate | $150 | 2.5x |

---

## Business Patterns Embedded in the Dataset

These patterns are what make the dashboard tell a real story. Flat random data produces useless dashboards.

**January resolution spike**
First 3 weeks of January see 65 to 90 new subscribers per week (vs 7 to 14 on normal weeks). These subscribers are high-risk. January cohort churn probability is multiplied by 1.8x for the first 10 weeks. By week 8, roughly 40% of January joiners have churned. This is a documented real-world subscription pattern. In the dashboard it appears as a cohort retention curve that drops sharply vs cohorts from other months.

**Summer slowdown**
June, July, and August see only 4 to 8 new subscribers per week. Existing subscriber skip rates increase by 30%. People travel, routines break.

**Holiday gift spike**
Mid-November through December sees 18 to 28 new subscribers per week via the Gift Subscription channel. These subscribers have 0.6x LTV multiplier and 2.2x churn multiplier after week 8. They look good in acquisition numbers but disappear fast. The dashboard should surface this.

**Year-over-year growth**
2024 new subscriber counts are multiplied by 1.3x vs 2023. The business is growing. MRR roughly 45% higher year over year.

**Meal preference and retention**
- Plant Based and Diabetic Friendly: 0.7x churn multiplier. Health-committed customers stay longer.
- Weight Loss: 1.3x churn multiplier after week 12. Goals achieved or abandoned.
- Balance: baseline churn rate.

**Delivery channel and retention**
- Hand Delivery: 0.75x churn multiplier. Personal service creates loyalty.
- B2B Corporate: 0.4x churn multiplier. Corporate routine is very sticky.
- National Shipping: baseline churn rate.

**Consecutive skips predict churn**
- 1 consecutive skip: 1.2x churn multiplier that week
- 2 consecutive skips: 1.8x churn multiplier
- 3+ consecutive skips: 3.0x churn multiplier

This is why skip rate belongs on the Executive Overview. It is not just a service metric. It is a leading indicator of revenue loss. In SQL, this requires the LAG() window function — intentional SQL learning exercise.

**Subscriber tenure and churn**
- Weeks 1 to 2: 4.5% churn probability per week
- Weeks 3 to 8: 3.2% per week
- Week 8 onward: 2.5% per week (base)
- Week 52 onward: 0.8% per week (loyal core)

**First 3 weeks discount**
DiscountAmount = $40 for the first 3 active weeks. This is Nutre's real promo offer. In CAC calculation, the discount is part of the cost of acquiring that subscriber.

---

## Dataset Output Numbers

These are the actual numbers produced by the generator (seed 42, reproducible):

| Metric | Value |
|--------|-------|
| Date range | Jan 2023 to Dec 2024 |
| Total weeks | 104 |
| Total subscribers | 2,206 |
| Active at end Dec 2024 | 766 |
| Total churned | 1,299 |
| Total fact rows | 81,070 |
| Total 2-year revenue | $11,996,544 |
| Average monthly revenue | $499,856 |
| Overall skip rate | 15.1% |

**Churn rate by meal preference (of all subscribers who ever joined):**
- Weight Loss: 67.5% churned
- Balance: 55.9% churned
- Plant Based: 53.6% churned
- Diabetic Friendly: 48.8% churned

**Average LTV by acquisition channel:**
- Gift Subscription: $2,095
- Organic Search: $3,289
- Enthusiast Program: $3,385
- Referral: $3,392
- Paid Social: $3,500
- B2B Corporate: $17,539

**MRR growth (sample):**
- Jan 2023: $374,428
- Jan 2024: $543,196
- Jun 2024: $679,718

---

## SQL Learning Objectives

The dataset was designed to require the following SQL skills before Power BI is connected. Writing these queries in SSMS is the SQL practice track running alongside the BI development.

**Level 1 — Validation queries (basic SQL)**
- Count subscribers by delivery channel
- Total revenue by month
- Count new vs churned by quarter
- Average weekly revenue by plan tier

**Level 2 — Subscription metrics (intermediate SQL)**
- MRR calculation: sum of WeeklyRevenue grouped by Year and Month
- Churn rate: churned subscribers divided by active subscribers at period start
- Skip rate: count of Skipped rows divided by total active + skipped rows
- LTV per subscriber: sum of WeeklyRevenue grouped by SubscriberID

**Level 3 — Advanced SQL (window functions required)**

*Cohort analysis:* Identify each subscriber's join month, then track what percentage survive to month 3, 6, and 12. Requires ROW_NUMBER() OVER (PARTITION BY SubscriberID ORDER BY WeekID).

*Consecutive skip calculation:* For each subscriber-week row, count how many consecutive Skipped weeks preceded it. Requires LAG() OVER (PARTITION BY SubscriberID ORDER BY WeekID).

*Running MRR:* Cumulative revenue per subscriber over their active life. Requires SUM() OVER (PARTITION BY SubscriberID ORDER BY WeekID ROWS UNBOUNDED PRECEDING).

*Month-over-month growth:* Compare MRR this month vs last month. Requires LAG() OVER (ORDER BY Year, Month).

These are not optional exercises. They are the SQL that makes the Power BI dashboard accurate. DAX can calculate some of these but understanding the SQL logic first makes the DAX logic clear.

---

## Power BI — Page Structure

### Phase 1: Executive Overview (build first)

Answers four business questions at the highest level:

1. **Where is the business today?** — MRR trend, active subscriber count, ARR projection
2. **Is it growing or contracting?** — Net new subscribers (new minus churned), MRR growth rate month over month
3. **Where is revenue coming from?** — Revenue by delivery channel (Hand vs Shipped vs B2B), revenue by acquisition channel
4. **Which subscribers are staying and which are leaving?** — Churn rate by month, skip rate trend, cohort retention table or curve

**Key visuals planned:**
- MRR trend line (monthly, 2 years, showing seasonality)
- KPI cards: Active Subscribers, MRR, Churn Rate, Skip Rate
- Waterfall or bar: New vs Churned vs Net each month
- Revenue by channel (stacked bar or donut)
- Cohort retention heatmap (month of join vs months retained)
- LTV by acquisition channel (horizontal bar)

### Phase 2: Marketing and Sales
CAC by channel, new subscriber acquisition trend, promo discount impact, MRR from each acquisition source vs cost of that source.

### Phase 3: Operations and Logistics
Delivery channel performance, skip patterns by region and season, order volume by plan tier, meal preference distribution.

### Phase 4: Customer Success and Retention
Cohort deep dive, skip to churn funnel, LTV by meal preference, survival curves by join cohort.

---

## Import Order into SQL Server

Run in this exact sequence to avoid foreign key conflicts:

1. DimDate
2. DimPlan
3. DimDeliveryChannel
4. DimAcquisitionChannel
5. DimSubscriber
6. FactSubscriptionWeekly

---

## Files in This Project

| File | Purpose |
|------|---------|
| nutre_dataset_generator.py | Run in Google Colab to generate all 6 CSV files |
| DimDate.csv | 104 weekly periods with business flags |
| DimPlan.csv | Meal plan tiers and pricing |
| DimDeliveryChannel.csv | 3 delivery types |
| DimAcquisitionChannel.csv | 6 acquisition channels with CAC and LTV data |
| DimSubscriber.csv | 2,206 subscribers with attributes |
| FactSubscriptionWeekly.csv | 81,070 rows of weekly subscriber events |
| Nutre_Meals_BI_Case_Study.md | This document |

---

## Positioning Context

This project was built as part of an intentional expansion beyond franchise and retail BI. The core positioning has shifted from industry-specific to problem-specific:

**Previous:** "I help franchise and retail businesses replace manual reporting with automated Power BI solutions."

**Expanded:** "I help businesses replace manual reporting with automated Power BI solutions, so decisions get made on accurate data instead of last week's spreadsheet."

This project adds subscription business analytics to the portfolio alongside the franchise bakery pipeline and the retail multi-category star schema. Three different industries. Same core problem solved each time. That pattern is the real positioning.

**Portfolio projects:**
1. Franchise bakery pipeline — messy legacy CSV, automated Power Query, operational reporting
2. Retail multi-category BI — SQL Server star schema, supplier intelligence, inventory alerts
3. Nutre Meals subscription BI — MRR, churn, LTV, CAC, cohort analysis

**Target with this project:**
- Primary: Nutre Meals Upwork proposal (start with "The secret ingredient is data")
- Secondary: Any subscription business on Upwork or LinkedIn — SaaS, subscription boxes, membership services, food delivery

---

## What Comes Next

1. SQL CREATE TABLE scripts for SQL Server
2. Import CSVs into SSMS
3. Write validation queries (Level 1 SQL)
4. Write MRR and churn queries (Level 2 SQL)
5. Write cohort and consecutive skip queries (Level 3 SQL — window functions)
6. Connect Power BI to SQL Server
7. Build Executive Overview page
8. Write case study narrative in own voice
9. Share with Nutre via LinkedIn DM or Upwork proposal
