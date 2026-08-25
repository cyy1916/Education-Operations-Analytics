# Education Operations Analytics

## Data Analytics & Operations Optimization Project for an Online Language Education Business

[中文](README.md) | [English](README_EN.md)

---

# Project Overview

This project explores how **data organization, data modeling, and business analytics methods** can be applied to improve operational efficiency and support decision-making in an online language education business.

Rather than focusing only on isolated data analysis tasks, this project starts from real operational processes:

> As an education business grows in terms of students, teachers, and course volume, how can structured data management improve operational efficiency when traditional Excel / Google Sheets workflows become increasingly complex?

The project covers several key business areas:

- Marketing Analytics
- Sales Analytics
- Academic Operations Analytics
- Student Retention Analytics

---

# Business Background

An online language education business usually requires collaboration between multiple teams throughout the student lifecycle.

## Marketing Team

Main responsibilities:

- Social media content operations
- Advertising campaigns
- Lead acquisition
- Channel performance tracking

---

## Sales Team

Main responsibilities:

- Customer communication
- Trial lesson arrangement
- Level assessment
- Enrollment conversion

---

## Academic Operations Team

Main responsibilities:

- Student information management
- Teacher assignment
- Course scheduling
- Lesson tracking
- Attendance management

---

At the early stage of a business, Excel / Google Sheets provides flexibility and low-cost support for daily operations.

However, as the business grows, spreadsheets gradually take on more responsibilities:

- Data storage
- Workflow management
- Issue tracking
- Teacher performance evaluation
- Monthly operational reporting

This creates several challenges:

- Data scattered across multiple files
- Different departments maintaining different versions of information
- Inconsistent naming conventions and classifications
- Manual data aggregation for reporting
- Difficulty retrieving historical information

---

# Project Objectives

## 1. Understand the Current Data Environment

Analyze:

- Existing operational data sources
- Data ownership across teams
- Data usage scenarios
- Relationships between different datasets

Deliverables:

- Data Inventory
- Data Dictionary

---

## 2. Identify Data Management Issues

### Data Fragmentation

A student's information may exist in multiple places:

- Customer inquiry records
- Trial lesson records
- Enrollment records
- Student information database
- Lesson records
- Renewal records

---

### Duplicate Data Maintenance

The same business information may be recorded by different teams.

Potential problems:

- Information inconsistency
- Conflicting reports
- Increased manual checking effort

---

### Lack of Data Standardization

For example, the same course type may appear as:

```
1V1
Private Lesson
One-to-One
VIP Course
```

A unified classification system is required for consistent analysis.

---

# Data Modeling

Based on business processes, this project designs:

- Data entities
- Relationships between tables
- Relational database structure

Main business entities include:

| Entity | Description |
|---|---|
| Student | Student information |
| Teacher | Teacher information |
| Course | Course types and packages |
| Lesson | Individual lesson records |
| Lead | Customer leads |
| Enrollment | Enrollment and purchase records |

---

# Business Analytics Scope

## Marketing Analytics

Analysis areas:

- Lead volume by acquisition channel
- Content and advertising performance
- Lead quality comparison

---

## Sales Analytics

Analysis areas:

- Trial lesson conversion rate
- Sales follow-up efficiency
- Conversion performance by lead source

---

## Academic Operations Analytics

Analysis areas:

- Student growth trends
- Teacher workload analysis
- Course resource utilization
- Attendance performance

---

## Retention Analytics

Analysis areas:

- Student engagement patterns
- Renewal behavior
- Factors influencing long-term learning continuation

---

# Project Workflow

This project follows a typical Data Analyst workflow:

```
Phase 0
Project Scoping

        ↓

Phase 1
Current State Assessment

        ↓

Phase 2
Data Modeling

        ↓

Phase 3
Data Cleaning & ETL

        ↓

Phase 4
SQL Analysis & Dashboard

        ↓

Phase 5
Business Insights & Recommendations
```

---

# Current Progress

## Phase 0: Project Scoping ✅

Completed:

- Business background analysis
- Problem identification
- Project objectives definition
- Project scope definition

---

## Phase 1: Current State Assessment 🚧

Currently working on:

---

## Marketing Data

Including:

- Customer inquiry records from social media channels
- Content performance tracking

---

## Sales Data

Including:

- Trial lesson records
- Level assessment records
- Enrollment records

---

## Academic Data

Including:

- Student information
- Teacher information
- Course records
- Attendance records

---

## Operational Data

Including:

- Operational issue tracking
- Teacher monthly evaluations
- Monthly operation summaries

---

# Project Structure

```
Education-Operations-Analytics/

├── README.md
├── README_EN.md

├── docs/
│   ├── 01_Project_Overview.md
│   ├── 02_Current_State_Assessment.md
│   ├── 03_Data_Audit_and_Findings.md
│   ├── 04_Data_Inventory.xlsx
│   └── 05_Data_Dictionary.xlsx

├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/

├── sql/
│   ├── schema.sql
│   └── analysis/

├── notebooks/

└── dashboard/
    └── screenshots/
```

---

# Technology Stack

## Data Processing

- Excel / Google Sheets
- SQL
- Python
- Pandas

---

## Data Modeling

- Entity Relationship Diagram (ERD)
- Relational Database Design

---

## Data Analytics

- SQL Queries
- Conversion Analysis
- Retention Analysis
- Operational KPI Analysis

---

## Data Visualization

- Power BI

---

## Project Management

- Git
- GitHub
- Markdown

---

# Data Privacy Statement

The original operational data contains sensitive information, including:

- Student information
- Parent contact details
- Teacher information
- Internal operational records

Therefore, real business data will not be uploaded to this public repository.

Public datasets will:

- Use synthetic data
- Apply anonymization techniques
- Remove sensitive fields

---

# Future Development Plan

## Data Modeling

Planned:

- Database schema design
- Entity Relationship Diagram (ERD)
- Fact Table / Dimension Table design

---

## Data Pipeline

Planned:

- Data cleaning
- Field standardization
- ETL pipeline design

---

## Analytics Dashboard

Planned dashboards:

- Marketing Dashboard
- Sales Dashboard
- Academic Operations Dashboard

---

# Project Summary

This project demonstrates an end-to-end analytics workflow:

```
Business Problem

↓

Current Process Analysis

↓

Data Audit

↓

Data Modeling

↓

SQL Analysis

↓

Business Insights
```

The goal is not only to produce analytical results, but to demonstrate how data can support operational improvement and business decision-making.

---

# Author

## Yiye Chen

Data Analytics / Business Intelligence Portfolio Project

Areas of Interest:

- Data Analysis
- SQL
- Business Intelligence
- Education Operations Analytics