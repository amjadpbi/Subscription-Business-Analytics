-- ============================================================
-- BRIGHTBOWL MEALS BI — DATABASE SCHEMA
-- SQL Server (SSMS)
-- Run this entire script before importing any CSV file
-- ============================================================
-- EXECUTION ORDER:
--   Step 1: Run this script to create database and all tables
--   Step 2: Import CSVs in this order:
--           DimDate → DimPlan → DimDeliveryChannel →
--           DimAcquisitionChannel → DimSubscriber →
--           FactSubscriptionWeekly
-- ============================================================


-- ============================================================
-- CREATE DATABASE
-- ============================================================
CREATE DATABASE BrightBowlMealsBI
GO

USE BrightBowlMealsBI
GO


-- ============================================================
-- DIMENSION TABLES
-- Always created before the fact table
-- Fact table foreign keys reference these tables
-- ============================================================


-- DimDate
-- One row per week | 104 rows total
-- WeekID is the join key used in FactSubscriptionWeekly
-- Business flags (IsJanuarySpike etc.) used for seasonal analysis
CREATE TABLE DimDate (
    WeekID          INT             NOT NULL,
    WeekStartDate   DATE            NOT NULL,
    WeekEndDate     DATE            NOT NULL,
    Month           INT             NOT NULL,
    MonthName       VARCHAR(20)     NOT NULL,
    Quarter         VARCHAR(5)      NOT NULL,
    Year            INT             NOT NULL,
    WeekOfYear      INT             NOT NULL,
    IsJanuarySpike  BIT             NOT NULL DEFAULT 0,
    IsHolidaySeason BIT             NOT NULL DEFAULT 0,
    IsSummer        BIT             NOT NULL DEFAULT 0,

    CONSTRAINT PK_DimDate PRIMARY KEY (WeekID)
)
GO


-- DimPlan
-- One row per meal plan tier
-- 7 rows: 5, 8, 10, 12, 15, 20 meals per week + B2B corporate
CREATE TABLE DimPlan (
    PlanID          INT             NOT NULL,
    PlanName        VARCHAR(50)     NOT NULL,
    MealsPerWeek    INT             NOT NULL,
    WeeklyPrice     DECIMAL(10,2)   NOT NULL,
    PricePerMeal    DECIMAL(10,2)   NOT NULL,

    CONSTRAINT PK_DimPlan PRIMARY KEY (PlanID)
)
GO


-- DimDeliveryChannel
-- 3 rows: Hand Delivery, National Shipping, B2B Corporate
CREATE TABLE DimDeliveryChannel (
    DeliveryChannelID   INT             NOT NULL,
    ChannelName         VARCHAR(50)     NOT NULL,
    DeliveryType        VARCHAR(50)     NOT NULL,
    Region              VARCHAR(50)     NOT NULL,

    CONSTRAINT PK_DimDeliveryChannel PRIMARY KEY (DeliveryChannelID)
)
GO


-- DimAcquisitionChannel
-- 6 rows: Referral, Enthusiast Program, Paid Social,
--         Organic Search, Gift Subscription, B2B Corporate
-- EstimatedCAC: cost to acquire one subscriber in USD
-- LTVMultiplier: how this channel's LTV compares to average
CREATE TABLE DimAcquisitionChannel (
    AcquisitionChannelID    INT             NOT NULL,
    ChannelName             VARCHAR(50)     NOT NULL,
    EstimatedCAC            DECIMAL(10,2)   NOT NULL,
    LTVMultiplier           DECIMAL(5,2)    NOT NULL,

    CONSTRAINT PK_DimAcquisitionChannel PRIMARY KEY (AcquisitionChannelID)
)
GO


-- DimSubscriber
-- One row per subscriber
-- JoinDate: actual join date (may be before 2023 for existing base)
-- JoinWeekID: week they first appear in our dataset
-- Dietary flags: IsGlutenFree, IsDairyFree, IsLowSodium
CREATE TABLE DimSubscriber (
    SubscriberID            INT             NOT NULL,
    JoinDate                DATE            NOT NULL,
    JoinWeekID              INT             NOT NULL,
    DeliveryChannelID       INT             NOT NULL,
    AcquisitionChannelID    INT             NOT NULL,
    PlanID                  INT             NOT NULL,
    MealPreference          VARCHAR(50)     NOT NULL,
    State                   VARCHAR(5)      NOT NULL,
    AgeGroup                VARCHAR(10)     NOT NULL,
    Gender                  VARCHAR(20)     NOT NULL,
    IsGlutenFree            BIT             NOT NULL DEFAULT 0,
    IsDairyFree             BIT             NOT NULL DEFAULT 0,
    IsLowSodium             BIT             NOT NULL DEFAULT 0,

    CONSTRAINT PK_DimSubscriber PRIMARY KEY (SubscriberID),

    CONSTRAINT FK_DimSubscriber_DimDate
        FOREIGN KEY (JoinWeekID)
        REFERENCES DimDate (WeekID),

    CONSTRAINT FK_DimSubscriber_DimDeliveryChannel
        FOREIGN KEY (DeliveryChannelID)
        REFERENCES DimDeliveryChannel (DeliveryChannelID),

    CONSTRAINT FK_DimSubscriber_DimAcquisitionChannel
        FOREIGN KEY (AcquisitionChannelID)
        REFERENCES DimAcquisitionChannel (AcquisitionChannelID),

    CONSTRAINT FK_DimSubscriber_DimPlan
        FOREIGN KEY (PlanID)
        REFERENCES DimPlan (PlanID)
)
GO


-- ============================================================
-- FACT TABLE
-- Created last because it references all dimension tables
-- One row per subscriber per week
-- This is the heartbeat of the entire dataset
-- ============================================================

-- FactSubscriptionWeekly
-- STATUS VALUES:
--   New     = subscriber's first week in the dataset
--   Active  = normal week, order placed, revenue generated
--   Skipped = subscriber paused this week, no revenue
--   Churned = subscriber cancelled, no further rows after this
CREATE TABLE FactSubscriptionWeekly (
    FactID                  INT             NOT NULL,
    SubscriberID            INT             NOT NULL,
    WeekID                  INT             NOT NULL,
    PlanID                  INT             NOT NULL,
    DeliveryChannelID       INT             NOT NULL,
    AcquisitionChannelID    INT             NOT NULL,
    Status                  VARCHAR(10)     NOT NULL,
    WeeklyRevenue           DECIMAL(10,2)   NOT NULL DEFAULT 0,
    MealsOrdered            INT             NOT NULL DEFAULT 0,
    DiscountAmount          DECIMAL(10,2)   NOT NULL DEFAULT 0,
    IsFirstWeek             BIT             NOT NULL DEFAULT 0,
    IsChurnWeek             BIT             NOT NULL DEFAULT 0,

    CONSTRAINT PK_FactSubscriptionWeekly PRIMARY KEY (FactID),

    CONSTRAINT FK_Fact_DimSubscriber
        FOREIGN KEY (SubscriberID)
        REFERENCES DimSubscriber (SubscriberID),

    CONSTRAINT FK_Fact_DimDate
        FOREIGN KEY (WeekID)
        REFERENCES DimDate (WeekID),

    CONSTRAINT FK_Fact_DimPlan
        FOREIGN KEY (PlanID)
        REFERENCES DimPlan (PlanID),

    CONSTRAINT FK_Fact_DimDeliveryChannel
        FOREIGN KEY (DeliveryChannelID)
        REFERENCES DimDeliveryChannel (DeliveryChannelID),

    CONSTRAINT FK_Fact_DimAcquisitionChannel
        FOREIGN KEY (AcquisitionChannelID)
        REFERENCES DimAcquisitionChannel (AcquisitionChannelID),

    CONSTRAINT CHK_Status
        CHECK (Status IN ('New', 'Active', 'Skipped', 'Churned'))
)
GO


-- ============================================================
-- VERIFY SCHEMA CREATED CORRECTLY
-- Run this after executing the script above
-- All 6 tables should appear with correct column counts
-- ============================================================
SELECT
    t.name                          AS TableName,
    COUNT(c.column_id)              AS ColumnCount
FROM sys.tables t
JOIN sys.columns c ON t.object_id = c.object_id
GROUP BY t.name
ORDER BY t.name
GO

-- Expected output:
-- DimAcquisitionChannel    4
-- DimDate                  11
-- DimDeliveryChannel       4
-- DimPlan                  5
-- DimSubscriber            13
-- FactSubscriptionWeekly   12

CREATE TABLE FactMarketingSpend (
    MarketingSpendID        INT             NOT NULL,
    WeekID                  INT             NOT NULL,
    AcquisitionChannelID    INT             NOT NULL,
    WeeklySpend             DECIMAL(10,2)   NOT NULL DEFAULT 0,

    CONSTRAINT PK_FactMarketingSpend 
        PRIMARY KEY (MarketingSpendID),

    CONSTRAINT FK_Marketing_DimDate
        FOREIGN KEY (WeekID)
        REFERENCES DimDate (WeekID),

    CONSTRAINT FK_Marketing_DimAcquisitionChannel
        FOREIGN KEY (AcquisitionChannelID)
        REFERENCES DimAcquisitionChannel (AcquisitionChannelID)
)
GO