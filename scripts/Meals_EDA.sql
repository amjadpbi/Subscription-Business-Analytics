/* ============================================================
   PORTFOLIO PROJECT : Subscription Analytics BI
   DATASET           : Simulated subscription meal delivery data
   PURPOSE           : EDA and SQL Analysis
   BUILT BY          : Muhammad Amjad
   CREATED           : May 2026
   DATABASE          : SubscriptionBI
   Tool              :  SQL Server Management Studio
   ============================================================ */

USE SubscriptionBI
GO
/* ============================================================
   SECTION 1 - DATA QUALITY
   Verify data arrived correctly before analysis begins
   ============================================================ */
  
 --Q1: How many rows are in FactSubscriptionWeekly and how many unique subscribers are in DimSubscriber?
 
SELECT
(SELECT COUNT(*) FROM FactSubscription) AS total_fact_rows,
(SELECT COUNT(DISTINCT SubscriberID) FROM DimSubscriber) AS total_subscriber;

 --Q2:	Do all SubscriberIDs in the fact table exist in DimSubscriber? Find any that do not.

 SELECT DISTINCT fs.SubscriberID
 FROM FactSubscription AS fs
 LEFT JOIN DimSubscriber AS	ds
 ON fs.SubscriberID = ds.SubscriberID
 WHERE ds.SubscriberID IS NULL;
 
 --Q3:  Do all WeekIDs in the fact table exist in DimDate? Find any that do not.

 SELECT DISTINCT fs.WeekID
 FROM Factsubscription AS fs
 LEFT JOIN DimDate AS dd
 ON fs.WeeKID = dd.WeekID
 WHERE dd.WeekID IS NULL;

 --Q4:  Are there any rows where Status is Skipped or Churned but WeeklyRevenue is greater than zero?

 SELECT fs.SubscriberID,
       fs.Status,
       fs.WeeklyRevenue
 FROM factSubscription AS fs
 WHERE fs.status IN ('Skipped','Churned')
 AND WeeklyRevenue > 0;

 --Q5:  Does any subscriber appear with Status New more than once?

SELECT fs.SubscriberID,
COUNT(*) AS NewStatusCount
FROM FactSubscription AS fs
WHERE fs.Status = 'New'
GROUP BY fs.SubscriberID
HAVING COUNT(*) > 1;

--Q6:  How many customers churned?

SELECT COUNT(*) AS TotalChurnedSubscribers
FROM FactSubscription AS fs
WHERE fs.IsChurnWeek = 1;

--Q7 	Does any subscriber have rows recorded after their churn week?

SELECT fs1.SubscriberID,
       fs1.WeekID AS ChurnWeek,
       fs2.WeekID AS LaterWeek
FROM FactSubscription AS fs1
JOIN FactSubscription AS fs2
ON fs1.SubscriberID = fs2.SubscriberID
WHERE fs1.IsChurnWeek = 1
    AND fs2.WeekID > fs1.WeekID;

--Q8   Are there any NULL values in WeeklyRevenue, Status, or SubscriberID columns?

SELECT
fs.WeeklyRevenue,
fs.Status,
fs.SubscriberID
FROM FactSubscription AS fs
WHERE fs.WeeklyRevenue IS NULL
OR fs.Status IS NULL
OR fs.SubscriberID IS NULL;

/* ============================================================
   SECTION 2 — Data Understanding
   Explore the shape and distribution of the business
   ============================================================ */

--Q9   Subscribers by delivery channel

SELECT dc.channelname,
COUNT(DISTINCT fs.SubscriberID) AS total_subscriber
FROM FactSubscription AS fs
JOIN DimDeliveryChannel AS dc
ON fs.DeliveryChannelID = dc.DeliveryChannelID
GROUP BY dc.channelname
ORDER BY total_subscriber ASC;

--Q10  Subscribers by acquisition channel Order by highest to lowest.

SELECT ac.ChannelName,
COUNT(DISTINCT fs.SubscriberID) AS total_subscriber
FROM FactSubscription fs
JOIN DimAcquisitionChannel ac
ON fs.AcquisitionChannelID = ac.AcquisitionChannelID
GROUP BY ac.ChannelName
ORDER BY total_subscriber DESC;

--Q11  Subscribers by meal preference

SELECT MealPreference, 
Count(Distinct SubscriberID) AS total_subscriber
FROM DimSubscriber
GROUP BY MealPreference
ORDER BY total_subscriber DESC;

--Q12  Most and least popular plan

SELECT dp.PlanName,
COUNT(DISTINCT fs.SubscriberID) AS totalsubscriber
FROM FactSubscription AS fs
JOIN DimPlan AS dp
ON fs.PlanID = dp.PlanID
GROUP BY dp.PlanName
ORDER BY totalsubscriber DESC;

--Q13  New subscribers per month both years

SELECT 
   dd.Year,
   dd.Month,
   dd.MonthName,
COUNT(DISTINCT fs.SubscriberID) AS TotalSubscribers
FROM FactSubscription AS fs
JOIN DimDate AS dd
ON fs.WeekID = dd.WeekID
WHERE fs.Status = 'New'
GROUP BY dd.Year,
         dd.Month,
         dd.MonthName
ORDER BY dd.Year,
         dd.Month;

--Q14  Total revenue per month per year

SELECT
dd.Year,
dd.Month,
dd.MonthName,
SUM(fs.WeeklyRevenue) AS TotalRevenue
FROM FactSubscription AS fs
JOIN DimDate AS dd
ON fs.WeekID = dd.WeekID
GROUP BY 
dd.Year,
dd.Month,
dd.MonthName
ORDER BY 
dd.Year,
dd.Month,
dd.MonthName;

--Q15  Average weekly revenue per plan

SELECT
    dp.PlanName,
    AVG(fs.WeeklyRevenue) AS AvgWeeklyRevenue
FROM FactSubscription AS fs
JOIN DimPlan AS dp
    ON fs.PlanID = dp.PlanID
GROUP BY dp.PlanName
ORDER BY AvgWeeklyRevenue DESC;

--Q16  What is the share of each subscription status across all non-new weekly records?

SELECT
    fs.Status,
    COUNT(*) AS TotalWeeklyRows,
    CAST(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*)
         FROM FactSubscription
         WHERE Status <> 'New')
        AS DECIMAL(10,2)
    ) AS StatusSharePercent
FROM FactSubscription AS fs
WHERE fs.Status <> 'New'
GROUP BY fs.Status
ORDER BY StatusSharePercent DESC;

/* ============================================================
   SECTION 3 — PATTERN DISCOVERY
   Find the story hidden in the data
   ============================================================ */

   --Q17 Revenue per subscriber by acquisition channel

  SELECT
  ac.ChannelName,
  SUM(fs.weeklyrevenue) AS TotalRevenue,
  COUNT(DISTINCT fs.SubscriberID) TotalSubscribers,
  CAST(
      SUM(fs.weeklyrevenue) * 1.0 / COUNT(DISTINCT fs.subscriberID)
      AS decimal(10,2)
      ) AS RevenuePerSubscriber
  FROM FactSubscription AS fs
  JOIN DimAcquisitionChannel AS ac
  ON fs.AcquisitionChannelID = ac.AcquisitionChannelID
  GROUP BY ac.ChannelName
  ORDER BY TotalRevenue DESC;

  --Q18  Highest churn month across both years

  SELECT TOP 10
  dd.Year,
  dd.Month,
  dd.MonthName,
  COUNT(DISTINCT fs.SubscriberID) AS ChurnedSubsciber
  FROM FactSubscription AS fs
  JOIN DimDate AS dd
  ON fs.WeekID = dd.WeekID
  WHERE fs.IsChurnWeek = 1
  GROUP BY 
  dd.Year,
  dd.Month,
  dd.MonthName
  ORDER BY 
  ChurnedSubsciber DESC;

  --Q19  Skip rate by delivery channel

  SELECT
  dc.ChannelName,
  COUNT(CASE WHEN fs.Status = 'Skipped' THEN 1 END) AS Skippedrows,
  COUNT(CASE WHEN fs.Status <> 'Churned' THEN 1 END) AS NonChurnedRows,
  CAST(
        COUNT(CASE WHEN fs.Status = 'Skipped' THEN 1 END) * 100.0
        / COUNT(CASE WHEN fs.Status <> 'Churned' THEN 1 END)
        AS DECIMAL(10,2)
    ) AS SkipRate
  FROM FactSubscription AS fs
  JOIN DimDeliveryChannel AS dc
  ON fs.DeliveryChannelID = dc.DeliveryChannelID
  GROUP BY dc.ChannelName
  ORDER BY SkipRate DESC;

  --20  January cohort churn vs other months
  
  SELECT 
  dd.Month,
  dd.MonthName,
  COUNT(DISTINCT ds.SubscriberID) AS TotalSubscriber,
  COUNT(DISTINCT CASE 
        WHEN IsChurnWeek = 1 THEN ds.SubscriberID
        END) AS ChurnSubscriber,
        CAST(
            COUNT(DISTINCT CASE 
            WHEN IsChurnWeek = 1 THEN ds.SubscriberID
        END) * 100.0 / COUNT(DISTINCT ds.SubscriberID)
        AS DECIMAL (10,2)
        ) AS ChurnRatePercent
  FROM DimSubscriber AS ds
  JOIN DimDate AS dd
  ON ds.JoinWeekID = dd.WeekID
  LEFT JOIN FactSubscription AS fs
  ON fs.SubscriberID = ds.SubscriberID 
  GROUP BY 
  dd.Month,
  dd.MonthName
  ORDER BY 
  dd.Month;

  --21  Subscribers with 2 or more consecutive skips

 WITH SubscriberWeeks AS (
      SELECT 
      fs.SubscriberID,
      fs.WeekID,
      fs.Status,
      LAG(fs.status) OVER ( 
      PARTITION BY fs.SubscriberID
      ORDER BY fs.WeekID
      ) AS PreviousStatus
      FROM FactSubscription AS fs
      )
      SELECT 
      SubscriberID,
      COUNT(*) AS ConsecutiveSkipCount
      FROM SubscriberWeeks
      WHERE Status = 'Skipped'
      AND PreviousStatus = 'Skipped'
      GROUP BY SubscriberID
      HAVING COUNT(*) >= 1
      ORDER BY ConsecutiveSkipCount DESC;

  --22  Month over month revenue comparison

 WITH MonthlyRevenue AS (
 SELECT
  dd.Year,
  dd.Month,
  dd.MonthName,
  SUM(fs.WeeklyRevenue) AS MonthlyRevenue
  FROM FactSubscription AS fs
  JOIN DimDate AS dd
  ON fs.WeekID = dd.WeekID
  GROUP BY 
  dd.Year,
  dd.Month,
  dd.MonthName
  )
 SELECT
 Year,
 Month, 
 MonthName,
 CAST(MonthlyRevenue AS DECIMAL (12,2)) AS MonthlyRevenue,
 CAST(
    LAG(MonthlyRevenue) OVER (
    ORDER BY Year, MONTH 
    ) AS DECIMAL(12,2)
    ) AS PreviousMonthRevenue,
    CAST(
         MonthlyRevenue - LAG(MonthlyRevenue) OVER (
            ORDER BY Year, Month
        ) AS DECIMAL(12,2)
    ) AS RevenueChange
 FROM MonthlyRevenue
 ORDER BY
    Year,
    Month;

 --23  Weeks active before churn per subscriber

 WITH SubscriberChurn AS (
    SELECT 
    SubscriberID,
    MIN(WEEKID) AS FirstWeekID,
    MAX(CASE WHEN IsChurnWeek = 1 THEN WeeKID END) AS ChurnWeekID
    FROM FactSubscription 
    GROUP BY SubscriberID
    )
    SELECT
    SubscriberID,
    FirstWeekID,
    ChurnWeekID,
    ChurnweekID - FirstWeekID AS ActivWeeksBeforeChurn
    FROM SubscriberChurn
    WHERE ChurnWeekID IS NOT NULL
    ORDER BY ActivWeeksBeforeChurn;

    --Q24  Cohort retention at month 3, 6, and 12

    WITH SubscriberLifecycle AS (
        SELECT
        ds.SubscriberID,
        ds.JoinWeekID,
        dd.Year AS JoinYear,
        dd.Month As JoinMonth,
        dd.MonthName AS JoinMonthName,
        MAX(CASE 
            WHEN fs.IsChurnWeek = 1 THEN fs.WeekID END
            ) AS ChurnWeeKID
        FROM DimSubscriber AS ds
        JOIN DimDate AS dd
        ON ds.JoinWeekID = dd.WeekID
        LEFT JOIN FactSubscription AS fs
        ON ds.SubscriberID = fs.SubscriberID
        GROUP BY
        ds.SubscriberID,
        ds.JoinWeekID,
        dd.Year,
        dd.Month,
        dd.MonthName
        )
        SELECT
        JoinYear,
        JoinMonth,
        JoinMonthName,
        COUNT(DISTINCT SubscriberID) AS CohortSize,
        COUNT(DISTINCT CASE 
        WHEN ChurnWeekID IS NULL 
             OR ChurnWeekID >= JoinWeekID + 13
             THEN SubscriberID 
             END) AS ActiveMonth3,
        COUNT(DISTINCT CASE 
        WHEN ChurnWeekID IS NULL 
             OR ChurnWeekID >= JoinWeekID + 26
             THEN SubscriberID 
             END) AS ActiveMonth6,
        COUNT(DISTINCT CASE 
        WHEN ChurnWeekID IS NULL 
             OR ChurnWeekID >= JoinWeekID + 52
             THEN SubscriberID 
             END) AS ActiveMonth12

        FROM SubscriberLifecycle
        GROUP BY 
        JoinYear,
        JoinMonth,
        JoinMonthName
        ORDER BY 
        JoinYear,
        JoinMonth;
