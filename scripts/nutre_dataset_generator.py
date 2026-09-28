# ============================================================
# BRIGHTBOWL MEALS — SUBSCRIPTION BI DATASET GENERATOR
# Google Colab | Python 3
# Portfolio Project: Power BI Subscription Analytics
# Dataset: Jan 2023 to Dec 2024 | 104 Weeks
# Schema: Star Schema | 1 Fact + 5 Dimensions + 1 Fact (Marketing)
# ============================================================
# WHAT THIS SCRIPT GENERATES:
#   DimDate.csv                — 104 weekly periods with business flags
#   DimPlan.csv                — Meal plan tiers with pricing
#   DimDeliveryChannel.csv     — Hand Delivery, Shipping, B2B
#   DimAcquisitionChannel.csv  — How subscribers found BrightBowl
#   DimSubscriber.csv          — All subscribers with attributes
#   FactSubscriptionWeekly.csv — One row per subscriber per week
#   FactMarketingSpend.csv     — Weekly spend by acquisition channel
#
# UPDATES IN THIS VERSION:
#   Passive churn logic        — 8 consecutive skips forces churn
#                                Real world: accounts go dormant, not
#                                just paused indefinitely
#   FactMarketingSpend added   — Weekly marketing spend per channel
#                                Replaces static EstimatedCAC in dim
#                                Makes CAC a real calculation in SQL
#
# BUSINESS PATTERNS EMBEDDED:
#   January resolution spike   — High acquisition, high early churn
#   Summer slowdown            — Lower new subscribers June-August
#   Holiday gift spike         — November-December gift subscriptions
#   B2B corporate channel      — Higher LTV, lower churn
#   Hand delivery retention    — Personal service = stickier customers
#   Meal preference retention  — Plant Based/Diabetic stay longer
#   Passive churn              — 8 consecutive skips = account closed
#   First 3 weeks discount     — $40 off promo (real BrightBowl offer)
#   Marketing spend growth     — Higher spend in 2024 vs 2023
#
# IMPORT ORDER INTO SQL SERVER:
#   1. DimDate
#   2. DimPlan
#   3. DimDeliveryChannel
#   4. DimAcquisitionChannel
#   5. DimSubscriber
#   6. FactSubscriptionWeekly
#   7. FactMarketingSpend
# ============================================================


# ============================================================
# SECTION 1: SETUP
# ============================================================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Fixed seed ensures same dataset every run
np.random.seed(42)
random.seed(42)

DATASET_START = datetime(2023, 1, 1)
TOTAL_WEEKS   = 104

print("=" * 55)
print("  BRIGHTBOWL MEALS — SUBSCRIPTION DATASET GENERATOR")
print("=" * 55)


# ============================================================
# SECTION 2: DIM DATE
# Weekly grain — BrightBowl operates on weekly subscription cycle
# Wednesday 11:59 PM is the weekly order cutoff
# ============================================================
def generate_dim_date():
    weeks = []
    for i in range(TOTAL_WEEKS):
        week_start = DATASET_START + timedelta(weeks=i)
        week_end   = week_start + timedelta(days=6)
        month      = week_start.month
        year       = week_start.year
        quarter    = (month - 1) // 3 + 1

        # January spike: first 3 weeks of January
        # New Year resolution buyers flood in these weeks
        is_jan_spike = 1 if (month == 1 and week_start.day <= 21) else 0

        # Holiday season: mid-November through December
        # Gift subscriptions spike here — different LTV profile
        is_holiday = 1 if (month == 11 and week_start.day >= 15) or month == 12 else 0

        # Summer slowdown: June, July, August
        # People travel, routines break, fewer new subscribers
        is_summer = 1 if month in [6, 7, 8] else 0

        weeks.append({
            'WeekID'        : i + 1,
            'WeekStartDate' : week_start.strftime('%Y-%m-%d'),
            'WeekEndDate'   : week_end.strftime('%Y-%m-%d'),
            'Month'         : month,
            'MonthName'     : week_start.strftime('%B'),
            'Quarter'       : f'Q{quarter}',
            'Year'          : year,
            'WeekOfYear'    : week_start.isocalendar()[1],
            'IsJanuarySpike': is_jan_spike,
            'IsHolidaySeason': is_holiday,
            'IsSummer'      : is_summer,
        })

    df = pd.DataFrame(weeks)
    print(f"  DimDate            — {len(df)} rows | Jan 2023 to Dec 2024")
    return df


# ============================================================
# SECTION 3: DIM PLAN
# Based on BrightBowl's actual plan range: 5 to 20 meals per week
# Volume discount: more meals = lower price per meal
# B2B corporate is a separate tier — office delivery accounts
# ============================================================
def generate_dim_plan():
    plans = [
        # PlanID | Name              | Meals | Weekly Price | Per Meal
        (1, '5 Meals / Week',        5,   80.00,  16.00),
        (2, '8 Meals / Week',        8,  112.00,  14.00),
        (3, '10 Meals / Week',      10,  130.00,  13.00),
        (4, '12 Meals / Week',      12,  150.00,  12.50),
        (5, '15 Meals / Week',      15,  180.00,  12.00),
        (6, '20 Meals / Week',      20,  220.00,  11.00),
        (7, 'B2B Corporate',        40,  400.00,  10.00),
    ]

    df = pd.DataFrame(plans, columns=[
        'PlanID', 'PlanName', 'MealsPerWeek', 'WeeklyPrice', 'PricePerMeal'
    ])
    print(f"  DimPlan            — {len(df)} rows | 5 to 20 meals + B2B tier")
    return df


# ============================================================
# SECTION 4: DIM DELIVERY CHANNEL
# Based on BrightBowl's actual operations confirmed from website
# Hand delivery: personal drivers in Northeast
# National shipping: FedEx / OnTrac across US
# B2B: corporate office accounts
# ============================================================
def generate_dim_delivery_channel():
    channels = [
        (1, 'Hand Delivery',    'Personal',  'Northeast US'),
        (2, 'National Shipping','Carrier',   'United States'),
        (3, 'B2B Corporate',    'Corporate', 'Mixed'),
    ]

    df = pd.DataFrame(channels, columns=[
        'DeliveryChannelID', 'ChannelName', 'DeliveryType', 'Region'
    ])
    print(f"  DimDeliveryChannel — {len(df)} rows | Hand / Shipping / B2B")
    return df


# ============================================================
# SECTION 5: DIM ACQUISITION CHANNEL
# How subscribers found BrightBowl
# EstimatedCAC: cost to acquire one subscriber (USD)
# LTVMultiplier: relative LTV vs average subscriber
#
# WHY THIS MATTERS FOR THE DASHBOARD:
#   Referral has lowest CAC and highest LTV = best channel
#   Paid Social has highest CAC and lowest LTV = worst ROI
#   B2B has highest CAC but highest LTV by far = worth investing
#   Gift subscriptions = low LTV, different retention curve
#
# Enthusiast Program = gym owners / personal trainers in
# Boston area who refer clients (real BrightBowl program)
# ============================================================
def generate_dim_acquisition_channel():
    channels = [
        # ID | Name                  | CAC  | LTV Multiplier
        (1, 'Referral',              15,   1.4),
        (2, 'Enthusiast Program',    20,   1.5),
        (3, 'Paid Social',           85,   0.9),
        (4, 'Organic Search',        35,   1.2),
        (5, 'Gift Subscription',      0,   0.6),
        (6, 'B2B Corporate',        150,   2.5),
    ]

    df = pd.DataFrame(channels, columns=[
        'AcquisitionChannelID', 'ChannelName', 'EstimatedCAC', 'LTVMultiplier'
    ])
    print(f"  DimAcquisitionChannel — {len(df)} rows | 6 acquisition channels")
    return df


# ============================================================
# SECTION 6: DIM SUBSCRIBER
# ============================================================

# States by delivery type (based on BrightBowl's Northeast focus)
HAND_DELIVERY_STATES   = ['MA', 'CT', 'RI', 'NH', 'NY', 'NJ']
NATIONAL_SHIP_STATES   = ['CA', 'TX', 'FL', 'IL', 'PA', 'OH',
                           'GA', 'NC', 'MI', 'AZ', 'WA', 'CO',
                           'TN', 'MN', 'OR', 'VA', 'MD', 'NV']
B2B_STATES             = ['MA', 'NY', 'CT']

# Three primary plan types from BrightBowl website
# Dietary filters are separate flags on the subscriber
MEAL_PREFERENCES       = ['Balance', 'Weight Loss', 'Plant Based', 'Diabetic Friendly']
MEAL_PREF_WEIGHTS      = [0.40, 0.35, 0.15, 0.10]

# Health meal delivery demographic skews 25-54, female majority
AGE_GROUPS             = ['18-24', '25-34', '35-44', '45-54', '55-64']
AGE_WEIGHTS            = [0.08, 0.30, 0.35, 0.20, 0.07]

GENDERS                = ['Female', 'Male', 'Not Specified']
GENDER_WEIGHTS         = [0.58, 0.36, 0.06]


def build_subscriber(sub_id, join_week_id, is_existing=False, date_lookup=None):
    """
    Generate one subscriber with realistic attributes.

    is_existing = True means this subscriber joined before Jan 2023.
    BrightBowl was founded 2017. By Jan 2023 they have 450 active subscribers.
    We back-date their join date but start tracking them from week 1.

    TenureWeeksAtStart tells the fact generator how experienced
    this subscriber already is when our dataset begins.
    This affects churn probability — long-term subscribers are stickier.
    """

    # Delivery channel distribution
    # Hand delivery dominant (Northeast base), B2B growing
    roll = random.random()
    if roll < 0.55:
        delivery_id = 1
        state = random.choice(HAND_DELIVERY_STATES)
    elif roll < 0.85:
        delivery_id = 2
        state = random.choice(NATIONAL_SHIP_STATES)
    else:
        delivery_id = 3
        state = random.choice(B2B_STATES)

    # B2B accounts always use B2B acquisition channel and B2B plan
    if delivery_id == 3:
        acq_id  = 6
        plan_id = 7
    else:
        if delivery_id == 1:
            # Northeast hand delivery: Enthusiast Program is common
            acq_weights = [0.25, 0.20, 0.25, 0.20, 0.10, 0.00]
        else:
            # National shipping: Paid Social and Organic dominant
            acq_weights = [0.20, 0.05, 0.40, 0.25, 0.10, 0.00]

        acq_id = random.choices([1, 2, 3, 4, 5, 6], weights=acq_weights)[0]

        # Plan selection: 5 and 8 meal plans are most popular entry points
        plan_id = random.choices(
            [1, 2, 3, 4, 5, 6],
            weights=[0.30, 0.25, 0.20, 0.12, 0.08, 0.05]
        )[0]

    meal_pref = random.choices(MEAL_PREFERENCES, weights=MEAL_PREF_WEIGHTS)[0]
    age_group = random.choices(AGE_GROUPS, weights=AGE_WEIGHTS)[0]
    gender    = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]

    # Back-date join for existing subscribers (3 months to 5 years before 2023)
    if is_existing:
        months_back = random.randint(3, 60)
        join_date   = (DATASET_START - timedelta(days=months_back * 30)).strftime('%Y-%m-%d')
        tenure_weeks_at_start = months_back * 4
    else:
        if date_lookup and join_week_id in date_lookup:
            join_date = date_lookup[join_week_id]['WeekStartDate']
        else:
            join_date = DATASET_START.strftime('%Y-%m-%d')
        tenure_weeks_at_start = 0

    return {
        'SubscriberID'          : sub_id,
        'JoinDate'              : join_date,
        'JoinWeekID'            : join_week_id,
        'DeliveryChannelID'     : delivery_id,
        'AcquisitionChannelID'  : acq_id,
        'PlanID'                : plan_id,
        'MealPreference'        : meal_pref,
        'State'                 : state,
        'AgeGroup'              : age_group,
        'Gender'                : gender,
        'IsGlutenFree'          : 1 if random.random() < 0.12 else 0,
        'IsDairyFree'           : 1 if random.random() < 0.10 else 0,
        'IsLowSodium'           : 1 if random.random() < 0.08 else 0,
        'TenureWeeksAtStart'    : tenure_weeks_at_start,
    }


def new_subscribers_this_week(week_row, year_offset):
    """
    How many new subscribers join each week.
    Driven by real BrightBowl business patterns.
    Year 2 (2024) has more subscribers as brand grows.
    year_offset: 1.0 for 2023, 1.3 for 2024
    """
    month    = week_row['Month']
    jan_flag = week_row['IsJanuarySpike']
    hol_flag = week_row['IsHolidaySeason']
    sum_flag = week_row['IsSummer']

    if jan_flag:
        base = random.randint(65, 90)   # Resolution spike
    elif hol_flag:
        base = random.randint(18, 28)   # Gift subscriptions
    elif sum_flag:
        base = random.randint(4, 8)     # Summer slowdown
    else:
        base = random.randint(7, 14)    # Normal week

    return int(base * year_offset)


# ============================================================
# SECTION 7: FACT SUBSCRIPTION WEEKLY
#
# This is the core of the dataset.
# One row per subscriber per week.
# Status drives everything: revenue, churn rate, MRR calculation.
#
# STATUS VALUES:
#   New     — subscriber's first week in dataset
#   Active  — normal week, order placed
#   Skipped — subscriber paused this week (no revenue)
#   Churned — subscriber cancelled (no more rows after this)
#
# IMPORTANT FOR SQL LEARNING:
#   ConsecutiveSkips and WeeksActive are NOT included here.
#   You will calculate these in SQL using LAG() and ROW_NUMBER().
#   This is intentional — these are key SQL practice exercises.
# ============================================================

def churn_probability(subscriber, weeks_active, date_row, consecutive_skips):
    """
    Weekly churn probability for one subscriber.
    Multiple realistic factors compound to create the final probability.

    This complexity is what makes cohort analysis meaningful.
    Flat churn rates produce boring dashboards.
    """
    # Base: 2.5% per week = roughly 10% monthly
    p = 0.025

    # New subscribers are at higher risk
    if weeks_active <= 2:
        p = 0.045
    elif weeks_active <= 8:
        p = 0.032
    elif weeks_active > 52:
        p = 0.008   # Long-term subscribers are very sticky

    # January resolution cohort churns fast after week 4
    join_month = pd.to_datetime(subscriber['JoinDate']).month
    if join_month == 1 and weeks_active <= 10:
        p *= 1.8

    # Meal preference affects long-term commitment
    pref = subscriber['MealPreference']
    if pref in ['Plant Based', 'Diabetic Friendly']:
        p *= 0.70   # Health-committed, stay longer
    elif pref == 'Weight Loss' and weeks_active > 12:
        p *= 1.30   # Goal achieved or abandoned after 3 months

    # Delivery channel affects retention
    d = subscriber['DeliveryChannelID']
    if d == 1:   # Hand delivery — personal service = loyal customers
        p *= 0.75
    elif d == 3: # B2B — corporate routine = very sticky
        p *= 0.40

    # Gift subscriptions: high churn after week 8
    if subscriber['AcquisitionChannelID'] == 5 and weeks_active > 8:
        p *= 2.20

    # Consecutive skips are the strongest churn predictor
    # This is why skip rate is on the Executive Overview dashboard
    if consecutive_skips >= 3:
        p *= 3.00
    elif consecutive_skips == 2:
        p *= 1.80
    elif consecutive_skips == 1:
        p *= 1.20

    # Summer: slightly elevated churn
    if date_row['IsSummer']:
        p *= 1.10

    return min(p, 0.40)  # Cap at 40%


def skip_probability(subscriber, weeks_active, date_row, consecutive_skips):
    """
    Weekly skip probability.
    Skip = subscriber pauses one week, stays subscribed.
    Higher skip rate is a leading indicator of future churn.
    """
    p = 0.16  # 16% base skip rate

    if weeks_active <= 4:
        p = 0.08    # New subscribers skip less (motivated)

    if date_row['IsSummer']:
        p *= 1.30   # Travel disrupts routines

    if date_row['IsHolidaySeason']:
        p *= 1.20   # Holidays disrupt routines

    if consecutive_skips >= 1:
        p *= 1.35   # Skipping becomes a habit

    if subscriber['DeliveryChannelID'] == 3:
        p = 0.05    # B2B corporate accounts rarely skip

    return min(p, 0.50)


def generate_fact_table(dim_subscribers, dim_date, dim_plan):
    """
    Build FactSubscriptionWeekly.
    Core loop: for each subscriber, generate one row per active week.
    Stops when subscriber churns or dataset ends (week 104).
    """
    fact_rows    = []
    plan_lookup  = dim_plan.set_index('PlanID').to_dict('index')
    date_lookup  = dim_date.set_index('WeekID').to_dict('index')
    total_subs   = len(dim_subscribers)

    print(f"\n  Generating fact rows for {total_subs} subscribers...")

    for idx, sub in dim_subscribers.iterrows():

        if idx % 300 == 0:
            print(f"    Progress: {idx}/{total_subs} subscribers processed...")

        sub_id      = sub['SubscriberID']
        join_week   = sub['JoinWeekID']
        plan_id     = sub['PlanID']
        plan        = plan_lookup.get(plan_id, plan_lookup[1])
        weekly_price= plan['WeeklyPrice']
        meals_count = plan['MealsPerWeek']

        # Existing subscribers start with their real tenure already accumulated
        # This makes their churn probability realistic from week 1
        tenure_offset    = sub['TenureWeeksAtStart']
        consecutive_skips = 0
        churned          = False

        for week_id in range(join_week, TOTAL_WEEKS + 1):
            if churned:
                break

            date_row = date_lookup.get(week_id)
            if date_row is None:
                break

            # Real weeks active = dataset weeks + pre-2023 tenure
            weeks_in_dataset = week_id - join_week + 1
            weeks_active     = weeks_in_dataset + tenure_offset

            # Determine status for this week
            if weeks_in_dataset == 1:
                # First appearance in our dataset
                status = 'New'
                consecutive_skips = 0

            else:
                # PASSIVE CHURN RULE
                # 8 consecutive skips = account forced to churn
                # Real world: subscribers go dormant, not paused forever
                # This is different from voluntary churn (explicit cancel)
                # In SQL analysis: you can find these by joining
                # consecutive skip count to churn week
                if consecutive_skips >= 8:
                    status = 'Churned'
                    churned = True
                    consecutive_skips = 0

                else:
                    churn_p = churn_probability(sub, weeks_active, date_row, consecutive_skips)
                    if random.random() < churn_p:
                        status = 'Churned'
                        churned = True
                        consecutive_skips = 0
                    else:
                        skip_p = skip_probability(sub, weeks_active, date_row, consecutive_skips)
                        if random.random() < skip_p:
                            status = 'Skipped'
                            consecutive_skips += 1
                        else:
                            status = 'Active'
                            consecutive_skips = 0

            # Revenue: zero if skipped or churned
            # First 3 weeks get $40 discount (real BrightBowl promo)
            if status in ['New', 'Active']:
                discount = 40.00 if weeks_in_dataset <= 3 else 0.00
                revenue  = round(weekly_price - discount, 2)
                meals    = meals_count
            else:
                discount = 0.00
                revenue  = 0.00
                meals    = 0

            fact_rows.append({
                'FactID'             : len(fact_rows) + 1,
                'SubscriberID'       : sub_id,
                'WeekID'             : week_id,
                'PlanID'             : plan_id,
                'DeliveryChannelID'  : sub['DeliveryChannelID'],
                'AcquisitionChannelID': sub['AcquisitionChannelID'],
                'Status'             : status,
                'WeeklyRevenue'      : revenue,
                'MealsOrdered'       : meals,
                'DiscountAmount'     : discount,
                'IsFirstWeek'        : 1 if weeks_in_dataset == 1 else 0,
                'IsChurnWeek'        : 1 if status == 'Churned' else 0,
            })

    return pd.DataFrame(fact_rows)


# ============================================================
# SECTION 8: FACT MARKETING SPEND
# Weekly marketing spend by acquisition channel
# This replaces EstimatedCAC as a static number in the dimension
# CAC is now a real calculation: spend / new subscribers that week
#
# WHY THIS EXISTS:
#   Without real spend data, CAC is just a hardcoded estimate
#   With spend data: CAC = WeeklySpend / NewSubscribersFromChannel
#   This makes Marketing and Sales dashboard calculations honest
#
# SPEND LOGIC PER CHANNEL:
#   Referral         — Small weekly incentive cost. Grows slowly.
#   Enthusiast Program— Free meals + commission. Tied to Northeast activity.
#   Paid Social      — Largest budget. Spikes in January. Grows in 2024.
#   Organic Search   — SEO/content cost. Steady, slow growth.
#   Gift Subscription — Zero direct spend. Revenue from gift buyer.
#   B2B Corporate    — Sales team cost. Slow burn, high return.
# ============================================================
def generate_fact_marketing_spend(dim_date):
    # Base weekly spend by channel (USD) — 2023 baseline
    # Channel ID : (min_spend, max_spend, jan_multiplier, year2_multiplier)
    channel_spend = {
        1: (200,  400,  1.0, 1.1),   # Referral
        2: (300,  600,  1.0, 1.2),   # Enthusiast Program
        3: (1500, 3500, 2.5, 1.5),   # Paid Social — big Jan push, grows fast
        4: (400,  800,  1.2, 1.2),   # Organic Search
        5: (0,    0,    1.0, 1.0),   # Gift Subscription — no spend
        6: (500,  1500, 1.0, 1.3),   # B2B Corporate
    }

    rows = []
    spend_id = 1

    for _, week_row in dim_date.iterrows():
        week_id  = week_row['WeekID']
        year     = week_row['Year']
        jan_flag = week_row['IsJanuarySpike']
        sum_flag = week_row['IsSummer']

        for channel_id, (min_s, max_s, jan_mult, yr2_mult) in channel_spend.items():
            if min_s == 0:
                spend = 0.00
            else:
                base  = random.uniform(min_s, max_s)
                # Year 2 growth
                if year == 2024:
                    base *= yr2_mult
                # January marketing push
                if jan_flag:
                    base *= jan_mult
                # Summer pullback — lower spend when acquisition is slow
                if sum_flag:
                    base *= 0.75

                spend = round(base, 2)

            rows.append({
                'MarketingSpendID'    : spend_id,
                'WeekID'              : week_id,
                'AcquisitionChannelID': channel_id,
                'WeeklySpend'         : spend,
            })
            spend_id += 1

    df = pd.DataFrame(rows)
    print(f"  FactMarketingSpend — {len(df)} rows | 6 channels x 104 weeks")
    return df


# ============================================================
# SECTION 9: MAIN EXECUTION
# ============================================================

print("\nStep 1: Building dimension tables...")
dim_date         = generate_dim_date()
dim_plan         = generate_dim_plan()
dim_delivery     = generate_dim_delivery_channel()
dim_acquisition  = generate_dim_acquisition_channel()

print("\nStep 2: Building subscriber base...")

subscribers = []
sub_id      = 1

# EXISTING BASE: 450 subscribers already active when 2023 begins
# BrightBowl founded 2017 — by Jan 2023 they have an established customer base
# These subscribers have varied tenures: some 6 months, some 5 years
print("  Creating existing subscriber base (450 subscribers)...")
for _ in range(450):
    s = build_subscriber(sub_id, join_week_id=1, is_existing=True, date_lookup=date_lookup_dict)
    subscribers.append(s)
    sub_id += 1

# NEW SUBSCRIBERS: Join week by week over 104 weeks
# Volume varies by seasonality and year-over-year growth
print("  Creating new subscribers (Jan 2023 — Dec 2024)...")
for _, week_row in dim_date.iterrows():
    week_id     = week_row['WeekID']
    year_offset = 1.30 if week_row['Year'] == 2024 else 1.00
    n_new       = new_subscribers_this_week(week_row, year_offset)

    for _ in range(n_new):
        s = build_subscriber(sub_id, join_week_id=week_id, is_existing=False, date_lookup=date_lookup_dict)
        subscribers.append(s)
        sub_id += 1

dim_subscribers = pd.DataFrame(subscribers)
print(f"  Total subscribers: {len(dim_subscribers)}")

# FACT TABLE
print("\nStep 3: Building fact table (this takes 1-3 minutes)...")
fact_subscription = generate_fact_table(dim_subscribers, dim_date, dim_plan)

# ============================================================
# SECTION 9: EXPORT TO CSV
# ============================================================
print("\nStep 4: Exporting CSV files...")

# Drop internal column before export
dim_subscribers_export = dim_subscribers.drop(columns=['TenureWeeksAtStart'])

dim_date.to_csv('DimDate.csv', index=False)
dim_plan.to_csv('DimPlan.csv', index=False)
dim_delivery.to_csv('DimDeliveryChannel.csv', index=False)
dim_acquisition.to_csv('DimAcquisitionChannel.csv', index=False)
dim_subscribers_export.to_csv('DimSubscriber.csv', index=False)
fact_subscription.to_csv('FactSubscriptionWeekly.csv', index=False)

# ============================================================
# SECTION 10: DATASET SUMMARY
# Verify the numbers tell a realistic story before importing
# ============================================================
print("\n" + "=" * 55)
print("  DATASET SUMMARY")
print("=" * 55)

total_subscribers = len(dim_subscribers)
total_fact_rows   = len(fact_subscription)

# Active subscribers at end of Dec 2024 (last week = 104)
last_week = fact_subscription[fact_subscription['WeekID'] == TOTAL_WEEKS]
active_end = last_week[last_week['Status'].isin(['Active', 'New'])].shape[0]

# Total churned subscribers
total_churned = fact_subscription[fact_subscription['IsChurnWeek'] == 1]['SubscriberID'].nunique()

# Total revenue over 2 years
total_revenue = fact_subscription['WeeklyRevenue'].sum()

# Average MRR (monthly recurring revenue estimate)
monthly_rev = (
    fact_subscription
    .merge(dim_date[['WeekID', 'Month', 'Year']], on='WeekID')
    .groupby(['Year', 'Month'])['WeeklyRevenue']
    .sum()
    .mean()
)

# Skip rate across all active weeks
active_or_skipped = fact_subscription[fact_subscription['Status'].isin(['Active', 'New', 'Skipped'])]
skip_rate = (
    active_or_skipped[active_or_skipped['Status'] == 'Skipped'].shape[0]
    / active_or_skipped.shape[0]
    * 100
)

# Churn rate (monthly estimate)
total_active_weeks   = fact_subscription[fact_subscription['Status'].isin(['Active', 'New'])].shape[0]
total_weeks_all      = fact_subscription.shape[0]
avg_weekly_churn     = total_churned / total_subscribers * 100

print(f"  Date range          : Jan 2023 — Dec 2024")
print(f"  Total weeks         : {TOTAL_WEEKS}")
print(f"  Total subscribers   : {total_subscribers:,}")
print(f"  Active end Dec 2024 : {active_end:,}")
print(f"  Total churned       : {total_churned:,}")
print(f"  Total fact rows     : {total_fact_rows:,}")
print(f"  Total revenue (2yr) : ${total_revenue:,.0f}")
print(f"  Avg monthly revenue : ${monthly_rev:,.0f}")
print(f"  Overall skip rate   : {skip_rate:.1f}%")
print(f"  Subscriber churn%   : {avg_weekly_churn:.1f}% of all subscribers churned")

print("\n  Files created:")
print(f"    DimDate.csv              — {len(dim_date)} rows")
print(f"    DimPlan.csv              — {len(dim_plan)} rows")
print(f"    DimDeliveryChannel.csv   — {len(dim_delivery)} rows")
print(f"    DimAcquisitionChannel.csv— {len(dim_acquisition)} rows")
print(f"    DimSubscriber.csv        — {len(dim_subscribers_export)} rows")
print(f"    FactSubscriptionWeekly.csv — {len(fact_subscription)} rows")

print("\n  NEXT STEPS:")
print("  1. Download all 6 CSV files from Colab (Files panel on left)")
print("  2. Create database BrightBowlMealsBI in SQL Server")
print("  3. Import CSVs in the order listed at top of this script")
print("  4. Write SQL queries to validate patterns before opening Power BI")
print("  5. Key SQL exercises: cohort analysis, MRR, churn rate, LTV")
print("\n" + "=" * 55)
print("  Dataset generation complete.")
print("=" * 55)
