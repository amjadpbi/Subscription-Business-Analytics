# Subscription Business — Project Audit

## 1. Project Identity

- Exact project path audited: D:\Power BI\Subscription based business Analysis
- Project type: self-built subscription analytics practice project inspired by a freelance business problem
- Business theme: Meal subscription business (Nutre Meals-style model)
- Primary evidence: synthetic dataset generator, SQL schema, SQL EDA script, CSV data files, PBIX file, and project documentation
- Evidence status: VERIFIED FROM FILES for project existence and artifact inventory

### Directly verified project artifacts
- nutre_dataset_generator.py
- nutre_schema.sql
- Meals_EDA.sql
- Nutre_Meals_BI_Case_Study.md
- Questions for SQL Data Analysis.docx
- SubscriptionBI.pbix
- Data/ with CSV files:
  - DimDate.csv
  - DimPlan.csv
  - DimDeliveryChannel.csv
  - DimAcquisitionChannel.csv
  - DimSubscriber.csv
  - FactSubscriptionWeekly.csv
  - FactMarketingSpend.csv

### Scope boundary
This audit is intentionally limited to this exact project folder and does not include any other project in D:\Power BI.

## 2. Creator-Provided Development History

The project documentation states the following, which is treated as CREATOR-PROVIDED HISTORY unless directly supported by files:

- A subscription-based business problem was identified from a freelance platform listing.
- The business problem was discussed with AI to understand the requirements.
- AI-assisted Python code was created for synthetic data generation.
- Python generated CSV datasets.
- The CSV files were uploaded/imported into SQL Server Management Studio.
- Business questions were identified.
- SQL queries were written to answer those business questions.
- The project was not completed through the final serving/reporting layer.
- The creator does not currently remember whether all SQL queries were correct or incorrect.

This history is consistent with the project artifacts, but it does not prove a finished solution or production-ready report.

## 3. Directly Verified Artifacts

### Verified from project files
- The project contains a synthetic data generator in Python.
- The project contains a SQL Server schema script that creates a star-schema database.
- The project contains an SQL analysis file with exploratory queries.
- The project contains a business case study document describing the context and design decisions.
- The project contains a PBIX file named SubscriptionBI.pbix.
- The project contains seven CSV files in the Data folder.

### Observed design intent
The project is clearly positioned as a subscription analytics portfolio exercise using a star schema and weekly revenue/churn analysis.

### Important limitation
The files show a strong experimental and educational structure, but not a finished, validated business intelligence deployment.

## 4. Business Problem

### 4.1 Directly verified business problem
The project is about a subscription meal delivery business modeled on Nutre Meals, a Massachusetts-based meal company.

Verified from the case study:
- The company operates a weekly subscription meal delivery business.
- Delivery channels include hand delivery and national shipping, plus corporate B2B delivery.
- There are multiple plan types and dietary preferences.
- The project is intended to support executive overview, acquisition, retention, and operational analysis.
- The business metrics explicitly named in the job post include:
  - MRR
  - ARR
  - LTV
  - CAC
  - churn rate
  - cohort analysis

### 4.2 Business entities directly identified
- Subscribers
- Plans
- Delivery channels
- Acquisition channels
- Dates
- Subscription weekly fact records
- Marketing spend fact

### 4.3 Business processes directly identified
- Weekly subscription order process
- New subscriber acquisition
- Subscription status tracking: New, Active, Skipped, Churned
- Weekly revenue generation
- Marketing acquisition spend
- Customer retention and churn analysis

### 4.4 Intended analytical objectives
Verified from the documentation:
- executive overview
- marketing and sales analysis
- operations and logistics analysis
- customer success and retention analysis
- cohort and retention analysis
- churn, CAC, LTV, and revenue analysis

### 4.5 Business questions explicitly called out
From the case study and SQL script, the intended questions include:
- How many subscribers exist by channel and acquisition source?
- Which channels acquire the most subscribers?
- What is revenue by month and year?
- What is churn by cohort and retention at month 3/6/12?
- What are revenue and skip patterns by delivery channel?
- Which acquisition channels are most efficient or risky?
- How do plan type and diet preferences relate to churn?

### 4.6 Classification
- VERIFIED FROM FILES: business problem and objectives described in the case study
- CREATOR-PROVIDED HISTORY: the original freelance posting context and portfolio intent
- UNKNOWN: whether the client ever actually hired or accepted the project
- INFERENCE: some business rules are described as simulated but realistic rather than actual operational facts

## 5. Data Generation

### 5.1 What the script generates
The file nutre_dataset_generator.py generates the following datasets:
- DimDate.csv
- DimPlan.csv
- DimDeliveryChannel.csv
- DimAcquisitionChannel.csv
- DimSubscriber.csv
- FactSubscriptionWeekly.csv
- FactMarketingSpend.csv

### 5.2 Scale and row counts
The script is designed to generate:
- 104 weeks from Jan 2023 to Dec 2024
- a total of 2,206 subscribers
- a fact table with one row per subscriber per week, tracked until churn or pause
- marketing spend by week and acquisition channel

The script also states that the dataset is reproducible with a fixed seed (seed 42).

### 5.3 Entities and relationships implied by the generator
The generator clearly builds a star schema:
- DimDate
- DimPlan
- DimDeliveryChannel
- DimAcquisitionChannel
- DimSubscriber
- FactSubscriptionWeekly
- FactMarketingSpend

### 5.4 Important design decisions in the Python
The generator includes explicit business logic for:
- January resolution spike
- summer slowdown
- holiday and gift subscription spikes
- hand delivery vs national shipping retention differences
- B2B retention advantages
- meal preference effects on churn risk
- passive churn after consecutive skips
- first 3 weeks $40 discount logic
- marketing spend growth patterns

This is not random noise. The script embeds business patterns intended to simulate realistic subscription behavior.

### 5.5 Data realism assessment
- VERIFIED FROM FILES: the generator intentionally simulates business patterns and seasonal effects.
- INFERENCE: the generated data is realistic enough for learning and demo work, but not a real client dataset.
- UNKNOWN: whether it closely mirrors a real Nutre Meals dataset from production operations.

### 5.6 What the Python contributes
The Python script is useful for:
- generating a repeatable synthetic dataset
- demonstrating subscription-business logic in a realistic star schema
- supporting SQL learning and Power BI prototyping

It does not prove a completed analytics implementation or a valid end-to-end client solution.

## 6. Dataset and Schema

### 6.1 Important tables and grain
From the generator and schema files:

#### DimDate
- Grain: one row per week
- Key field: WeekID
- Contains weekly business flags such as IsJanuarySpike, IsHolidaySeason, and IsSummer

#### DimPlan
- Grain: one row per plan tier
- Contains MealsPerWeek, WeeklyPrice, PricePerMeal

#### DimDeliveryChannel
- Grain: one row per delivery channel
- Values include Hand Delivery, National Shipping, B2B Corporate

#### DimAcquisitionChannel
- Grain: one row per acquisition source
- Values include Referral, Enthusiast Program, Paid Social, Organic Search, Gift Subscription, B2B Corporate

#### DimSubscriber
- Grain: one row per subscriber
- Contains join date, channel, plan, meal preference, geography, age group, gender, and dietary flags

#### FactSubscriptionWeekly
- Grain: one row per subscriber per week
- Fields include status, revenue, meals ordered, discount amount, first-week flag, churn-week flag
- This is the central fact table

#### FactMarketingSpend
- Grain: one row per week and acquisition channel
- Captures marketing spend used to derive acquisition economics

### 6.2 Data-model pattern
The project uses a star-schema pattern designed for subscription analytics.

### 6.3 Key relationship picture
- DimSubscriber → FactSubscriptionWeekly via SubscriberID
- DimDate → FactSubscriptionWeekly via WeekID
- DimPlan → FactSubscriptionWeekly via PlanID
- DimDeliveryChannel → FactSubscriptionWeekly via DeliveryChannelID
- DimAcquisitionChannel → FactSubscriptionWeekly via AcquisitionChannelID
- DimDate → FactMarketingSpend via WeekID
- DimAcquisitionChannel → FactMarketingSpend via AcquisitionChannelID

### 6.4 Directly observable data quality issues
The project is a synthetic dataset, so perfect production fidelity is not expected. But some issues are apparent from design and schema:
- synthetic data may not match real business variance exactly
- the data model is intentionally simplified for learning
- churn and skip logic is simulated rather than historical
- no evidence of ETL validation or operational data quality controls beyond the learning project design

### 6.5 Schema-to-dataset match quality
- VERIFIED FROM FILES: the schema and CSVs align in structure and field names for the central tables.
- The script and schema are consistent with a designed star schema.
- This supports SQL and Power BI learning scenarios.

## 7. SQL Analysis

### 7.1 Evidence reviewed
The file Meals_EDA.sql contains a series of exploratory SQL queries for data quality, growth, churn, retention, and business pattern discovery.

### 7.2 High-value analytical work present
The SQL script includes analyses for:
- fact-row counts and data completeness
- missing dimension values
- status anomalies
- revenue by month and year
- subscriber counts by delivery channel
- subscriber counts by acquisition channel
- plan popularity
- new subscribers by month
- status share
- revenue per acquisition channel
- churn by month
- skip rate by delivery channel
- January cohort churn analysis
- consecutive skip logic
- monthly revenue changes using LAG()
- weeks active before churn
- cohort retention checks at month 3, 6, and 12

### 7.3 Important SQL techniques used
- JOINs across fact and dimension tables
- aggregate queries with GROUP BY
- CASE expressions
- window functions such as LAG()
- CTEs
- subqueries
- ranking and retention logic

### 7.4 Real value from SQL skill perspective
The script demonstrates that the creator attempted to model actual subscription analysis using SQL methods that matter for business intelligence work:
- churn analysis
- cohort logic
- retention patterns
- business metric construction
- data quality validation queries
- window-function learning

This is educationally valuable, especially for a practice project.

## 8. SQL Correctness Review

### 8.1 Important findings
This review is static only. No runtime validation was performed against a live SQL Server instance, and the project does not provide execution results.

### 8.2 Queries that appear broadly logical
These queries appear structurally sound based on the schema and business logic:
- row-count and missing-dimension checks
- count of subscribers by channel
- new subscriber counts by month
- monthly revenue aggregation
- acquisition channel revenue analysis
- churn month analysis
- month-over-month revenue comparison with LAG()

### 8.3 Potential issues or unreliable logic
The following concerns are important and should be noted honestly:

#### 1. Table name inconsistencies in the script
The SQL file references names like FactSubscription, FactSubscriptionWeekly, and Factsubscription inconsistently. The schema file defines the table as FactSubscriptionWeekly, but the EDA script uses different casing and sometimes different table names.
- Status: POTENTIAL ISSUE
- Why: if the database schema and script are not aligned, execution can fail or give incomplete results.

#### 2. Some queries use wrong grain assumptions
Examples include annual/monthly counts that may be mixing subscriber counts, weekly rows, or rows after churn without proper lifecycle logic.
- Status: POTENTIAL ISSUE
- Why: a fact table with one row per subscriber per week is not automatically equivalent to one row per unique subscriber without careful filtering.

#### 3. Skip-rate logic may be mathematically misleading
The query for skip rate divides skipped rows by non-churned rows but uses a condition that may not represent the intended denominator.
- Status: POTENTIAL ISSUE
- Why: the denominator may not be the population at risk for a skip event.

#### 4. Consecutive skip logic is directionally useful but not complete
The logic identifies repeated skipped statuses with a previous-status comparison, but it does not clearly distinguish a legitimate pause pattern from a churned account or a post-churn edge case.
- Status: POTENTIAL ISSUE
- Why: this is a useful learning query but not a fully robust churn model.

#### 5. Cohort logic may be imprecise without stronger date boundaries
The cohort retention query uses JoinWeekID and counts subscribers still active at 13, 26, and 52 weeks, but the logic is not fully explained and could be sensitive to churn timing and data grain.
- Status: POTENTIAL ISSUE
- Why: this is an approximation, not a validated production retention metric.

#### 6. SQL correctness cannot be proven without runtime execution
The project contains no evidence of successful execution against a SQL Server database.
- Status: UNKNOWN
- Why: no screenshots, output tables, or validation logs were provided in the project files.

### 8.4 Classification summary
- Appears logically correct: several aggregate and join queries
- Potential issue: count logic, skip-rate logic, and retention logic
- Clearly incorrect: cannot determine from static review alone without execution
- Cannot determine without execution/data validation: most of the advanced churn and retention logic

### 8.5 Honest conclusion on SQL quality
The SQL demonstrates solid learning intent and reasonable analytical structure, but the files do not provide evidence that the SQL was fully validated or corrected on execution. This is not enough to claim a production-ready or portfolio-grade SQL implementation.

## 9. Business Question Coverage

### 9.1 Business questions actually addressed
From the SQL EDA file, the following are addressed:
- Which acquisition channels bring the most subscribers?
- Which delivery channels have the most subscribers?
- What are monthly revenue trends?
- Which months have the highest churn?
- Are there skip patterns by delivery channel?
- Which subscribers churn after consecutive skips?
- How does revenue change month over month?
- How long do subscribers remain active before churn?
- What is cohort retention by month 3, 6, 12?

### 9.2 Business questions documented but not clearly fully implemented
The project documentation mentions MRR, ARR, LTV, CAC, churn, and cohort analysis, but the SQL file does not fully demonstrate all formulas in a polished, audited way.

### 9.3 Mapping
| Business Question | SQL coverage | Status | Notes |
|---|---|---|---|
| How many subscribers by channel? | Yes | Appears logically correct | Straightforward grouping query |
| Which acquisition channel is strongest? | Yes | Appears logically correct | Revenue and subscriber counts are used |
| How does revenue trend over time? | Yes | Appears logically correct | Monthly aggregation and LAG() trend |
| Where is churn strongest? | Yes | Potential issue | Depends on churn logic and date assumptions |
| What is skip behavior? | Yes | Potential issue | Denominator precision may be weak |
| What is cohort retention? | Yes | Potential issue | Useful but not proven executed correctly |
| How are MRR and ARR derived? | Not clearly fully implemented | Unknown | The project describes them but the SQL file does not fully show a final metric layer |
| How is LTV calculated? | Not clearly fully implemented | Unknown | Not fully evidenced |
| How is CAC calculated? | Partially supported by marketing spend table | Potential issue | Not presented as a complete, validated metric model |

## 10. Serving Layer Status

### 10.1 Verified status
A file named SubscriptionBI.pbix exists in the project directory.

### 10.2 What can be said from the files
- VERIFIED FROM FILES: a Power BI report file exists.
- UNKNOWN: whether it contains a complete, validated final report or is a partial working file.
- UNKNOWN: whether the file is connected successfully to the dataset or whether it is incomplete.

### 10.3 Honest conclusion
The project history explicitly states that the final serving/reporting layer was incomplete and not completed. This aligns with the artifact evidence and does not support claiming a strong Power BI delivery.

Therefore:
- Serving/reporting layer is incomplete and does not materially contribute to the portfolio story.

## 11. AI-Assisted Development Boundary

### 11.1 Verified from project history
The project explicitly states that AI was used to:
- discuss the business problem
- create the Python data-generation script
- support development work

### 11.2 Honest boundary
This does not justify claiming that the entire project was AI-generated.

The files show real project structure, explicit data modeling decisions, schema work, SQL work, and business-case documentation.

The responsible framing is:
- AI was used as a development aid for brainstorming and script generation.
- The resulting implementation still contains a clear human-structured business problem, schema design, SQL analysis path, and portfolio framing.
- This is not a fully AI-authored analytics project.

## 12. Implemented vs Incomplete

| Area | Status | Assessment |
|---|---|---|
| Business problem framing | IMPLEMENTED | Strongly documented in case study |
| Synthetic data generation | IMPLEMENTED | Good for learning and prototyping |
| Star schema design | IMPLEMENTED | Clearly structured and coherent |
| SQL data quality checks | IMPLEMENTED | Present and useful |
| SQL analytical exploration | IMPLEMENTED | Useful but not validated at runtime |
| Churn and retention logic | PARTIALLY IMPLEMENTED | Good learning exercises, but weak evidence of correctness |
| Final Power BI dashboard | INCOMPLETE | Not supported as a finished reporting layer |
| Client deployment | UNKNOWN | No evidence of production use |
| Portfolio-grade final product | INCOMPLETE | Not enough evidence to call it polished |

## 13. Portfolio-Relevant Capabilities

This project does demonstrate some genuine learning and practice value:
- synthetic star-schema design
- subscription analytics thinking
- SQL data-quality validation
- cohort and churn analysis patterns
- window-function usage
- business pattern simulation
- use of a realistic business problem as a learning case

These are useful capabilities, especially for a learning portfolio, but they are not strong enough to outweigh the incompleteness and SQL uncertainty.

## 14. Claims That Should NOT Be Made

The following claims are not supported by the evidence:
- “This is a completed, production-ready subscription analytics system.”
- “This was delivered to a real client.”
- “This project generated real business impact.”
- “The SQL queries were fully validated.”
- “The PBIX is a complete executive dashboard.”
- “The project is a polished portfolio-ready analytics product.”
- “The entire project was AI-generated.”

## 15. Evidence Gaps and Unknowns

- The database was not actually executed in this audit, so runtime SQL correctness remains unknown.
- No execution output or validation log was inspected.
- No final dashboard screenshots or published report were provided.
- No client acceptance or business outcome evidence was provided.
- The original freelance opportunity may have been a stimulus, not a real accepted engagement.
- No production architecture evidence existed in the project files.

## 16. Portfolio Decision

### Portfolio decision: KEEP AS BACKGROUND EVIDENCE, BUT DO NOT FEATURE

### Reasoning
This project is not weak because it lacks ambition. It is weak because it is incomplete and the most important evidence — the SQL correctness and final serving layer — is not fully validated or completed.

The project does show:
- a realistic business problem
- a star-schema design
- synthetic but structured data generation
- subscription analytics concepts
- serious SQL learning work

But it does not show:
- a finished, validated reporting layer
- a complete, executed SQL analysis package with evidence of correctness
- a polished portfolio-quality product that competes with stronger existing project work

In the context of a portfolio already containing stronger, more complete examples such as real-estate expense automation, bakery analytics, retail BI, and e-commerce analytics, this project does not merit inclusion as a featured artifact.

## 17. Recommended Portfolio Description IF INCLUDED

If the project is to be retained as a background artifact, the honest description should be:

“Self-built subscription analytics prototype based on a Nutre Meals-style meal subscription business. The project includes synthetic data generation, a star-schema SQL design, and exploratory SQL for churn, retention, and acquisition analysis. It demonstrates subscription-business thinking and SQL window-function usage, but it is a learning project and not a finished production dashboard or validated client-delivered solution.”

## 18. Final Recommendation

### Final recommendation: KEEP AS BACKGROUND EVIDENCE, BUT DO NOT FEATURE

This project is worth keeping only as evidence of learning and SQL practice. It should not be presented as a meaningful featured portfolio project because:
- the serving layer is incomplete
- the SQL correctness is not proven
- the data is synthetic and not validated against a real operational system
- the project is not as polished or complete as stronger portfolio artifacts already present

### Best honest portfolio position
This project can serve as a learning artifact for subscription analytics thinking, but it should not compete with the stronger, completed portfolio pieces.

### Short verdict
- Useful for learning: YES
- Strong enough for a featured portfolio case study: NO
- Worth keeping as supporting evidence: YES
- Recommended final status: KEEP AS BACKGROUND EVIDENCE, BUT DO NOT FEATURE
