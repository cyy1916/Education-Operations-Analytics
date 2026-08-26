# 教育运营数据管理与分析项目

# 01 Project Background

# 1. Project Overview

本项目是一个基于个人工作经历和实际业务场景的 Data Analytics Portfolio
Project。

项目来源于在线语言教育机构日常运营过程中，对市场获客、销售转化、学生管理、课程执行以及运营统计流程的观察。

随着学生数量、教师数量以及课程规模不断增加，业务逐渐依赖 Excel / Google
Sheets 完成信息记录、流程管理以及数据统计。

当前 Spreadsheet 系统主要承担：

-   数据存储；
-   信息查询；
-   状态跟踪；
-   问题记录；
-   运营统计；
-   月度汇报。

在业务规模较小时，Excel / Google Sheets
具有灵活、低成本、易维护的优势，可以快速支持日常运营。

但是随着业务流程增加，业务数据、流程管理和分析需求逐渐集中在同一套文件体系中，使数据维护、跨部门协作以及业务分析变得更加复杂。

因此，本项目希望通过梳理当前业务流程、数据来源以及数据结构，分析现有数据管理方式中的限制，并探索更加结构化的数据管理和分析方法。

------------------------------------------------------------------------

# 2. Business Context

## 2.1 Online Language Education Business Process

在线语言教育机构主要包含以下业务流程：

``` text
Marketing Acquisition

        ↓

Customer Inquiry

        ↓

Sales Follow-up

        ↓

Trial Lesson / Level Assessment

        ↓

Enrollment

        ↓

Course Delivery

        ↓

Renewal / Completion
```

不同业务阶段会产生不同类型的数据：

| 业务阶段 | 产生的数据 |
| --- | --- |
| 市场获客（Marketing Acquisition） | 获客渠道、账号、帖子、曝光量、点击量 |
| 客户咨询（Customer Inquiry） | 客户信息、咨询记录、跟进状态 |
| 试听课（Trial Lesson） | 试听日期、试听教师、等级评估 |
| 正式报名（Enrollment） | 课程套餐、学生信息 |
| 课程交付（Course Delivery） | 学生、教师、课程、排课信息 |

这些数据由不同团队产生，并服务于不同业务目的。

------------------------------------------------------------------------

# 3. Current Data Environment

## 3.1 Spreadsheet-based Data Management

当前业务主要通过 Excel / Google Sheets 管理。

不同团队根据职责维护不同类型的数据：

  ----------------------------------------------------------------------------------
  Team                    Responsibility          Data
  ----------------------- ----------------------- ----------------------------------
  Marketing / Operations  市场获客与渠道管理      客户来源、内容运营、广告数据

  Sales                   客户转化管理            客户咨询、试听、测试、报名信息

  Academic Operations     教务执行管理            学生、教师、课程、反馈、异常记录
  ----------------------------------------------------------------------------------

当前主要数据类型包括：

## Lead Data

用于记录：

-   客户来源；
-   咨询时间；
-   咨询方式；
-   销售跟进；
-   客户状态。

## Trial Data

用于记录：

-   试听安排；
-   测试结果；
-   教师反馈；
-   推荐课程。

## Enrollment Data

用于记录：

-   报名信息；
-   课程类型；
-   课时；
-   负责人。

## Student Data

用于记录：

-   学生基本信息；
-   教师信息；
-   当前学习状态。

## Lesson Data

用于记录：

-   上课日期；
-   时间；
-   教师；
-   课程反馈。

## Operational Data

用于记录：

-   异常事件；
-   教师协调；
-   月度运营统计。

------------------------------------------------------------------------

# 4. Initial Business Problems

## 4.1 Data Fragmentation

当前业务数据根据不同流程产生，并存储在不同文件中。

一个学生完整生命周期可能涉及：

``` text
Lead

↓

Trial

↓

Enrollment

↓

Student

↓

Lesson

↓

Renewal
```

不同阶段的数据需要通过人工方式进行关联。

可能导致：

-   历史信息查询困难；
-   跨部门分析成本增加；
-   数据整理时间增加。

------------------------------------------------------------------------

## 4.2 Duplicate Data Maintenance

相同业务信息可能在多个文件中重复记录。

例如学生信息可能同时存在于：

-   咨询记录；
-   试听记录；
-   报名记录；
-   学生汇总表；
-   课程记录。

可能产生：

-   信息更新不同步；
-   多个版本同时存在；
-   人工核对成本增加。

------------------------------------------------------------------------

## 4.3 Lack of Standardized Data Definition

部分业务字段缺少统一定义。

例如课程类型：

``` text
1V1

私教

一对一

VIP
```

如果缺少统一分类标准，会影响：

-   SQL 查询；
-   指标统计；
-   Dashboard 分析；
-   跨周期比较。

------------------------------------------------------------------------

## 4.4 Mixed Data Granularity

当前部分表格同时包含不同层级的数据。

例如：

运营数据可能同时包含：

-   帖子级数据；
-   账号级汇总数据。

学生管理数据可能同时包含：

-   学生基本信息；
-   当前运营任务状态。

不同粒度的数据混合会增加分析时的重复计算风险。

------------------------------------------------------------------------

## 4.5 Manual Reporting Dependency

部分业务指标仍依赖人工整理：

例如：

-   试听转化率；
-   学生数量变化；
-   教师工作量；
-   开班情况；
-   月度运营统计。

随着业务规模扩大，人工统计成本逐渐增加。

------------------------------------------------------------------------

# 5. Business Impact

## 5.1 Operational Efficiency

当前数据管理方式影响：

-   员工维护多个文件的时间；
-   信息查询效率；
-   部门之间的信息交接；
-   新员工理解业务流程的速度。

------------------------------------------------------------------------

## 5.2 Data Consistency

可能出现：

-   不同文件存在不同版本信息；
-   数据更新无法同步；
-   统计结果需要人工确认。

------------------------------------------------------------------------

## 5.3 Analytical Capability

当前结构限制了快速分析能力。

例如难以快速回答：

### Marketing Analytics

-   哪些渠道带来更多有效客户？
-   哪些内容表现更好？

### Sales Analytics

-   客户响应速度如何影响转化？
-   不同销售转化表现如何？

### Academic Operations Analytics

-   当前学生数量变化；
-   教师工作量；
-   课程执行情况；
-   续费情况。

------------------------------------------------------------------------

# 6. Project Objectives

## 6.1 Understand Current Data Environment

目标：

梳理当前业务数据环境：

-   数据来源；
-   数据维护部门；
-   数据用途；
-   数据关系。

输出：

-   Data Inventory；
-   Data Dictionary。

------------------------------------------------------------------------

## 6.2 Analyze Current Data Management Issues

分析：

-   数据分散；
-   重复维护；
-   字段标准问题；
-   数据关联问题；
-   数据粒度问题。

------------------------------------------------------------------------

## 6.3 Establish Analytical Data Foundation

根据业务流程设计适合分析的数据模型。

主要业务实体：

  Entity       Description
  ------------ --------------
  Lead         客户线索
  Student      学生信息
  Teacher      教师信息
  Course       课程类型
  Enrollment   报名记录
  Lesson       单次课程记录
  Renewal      续费记录

用于支持：

-   Marketing Analytics；
-   Sales Analytics；
-   Academic Operations Analytics；
-   Retention Analytics。

------------------------------------------------------------------------

# 7. Project Scope

## Included

本项目包含：

-   当前业务流程分析；
-   数据来源审计；
-   数据问题分析；
-   数据模型设计；
-   SQL Analysis；
-   Business Metrics Definition；
-   Dashboard Prototype。

------------------------------------------------------------------------

## Not Included

本项目不包含：

-   替换现有企业系统；
-   开发完整 ERP 系统；
-   建立生产环境数据库；
-   自动化全部业务流程。

------------------------------------------------------------------------

# 8. Expected Deliverables

## Data Audit

包括：

-   Data Inventory；
-   Data Dictionary。

用于：

-   记录已有数据来源；
-   明确数据用途；
-   建立数据标准。

------------------------------------------------------------------------

## Data Modeling

包括：

-   Entity Relationship Diagram (ERD)；
-   Relational Data Model。

------------------------------------------------------------------------

## Data Analytics

包括：

-   SQL Analysis；
-   KPI Calculation；
-   Business Metrics Definition。

------------------------------------------------------------------------

## Visualization

包括：

-   Power BI Dashboard Prototype。

------------------------------------------------------------------------

# 9. Project Workflow

本项目按照 Data Analyst 常见流程推进：

``` text
Business Understanding

        ↓

Current Workflow Analysis

        ↓

Data Audit

        ↓

Data Modeling

        ↓

Data Cleaning & ETL

        ↓

SQL Analysis

        ↓

Dashboard

        ↓

Business Insights
```

------------------------------------------------------------------------

# 10. Data Privacy Statement

由于实际业务数据包含敏感信息：

-   学生信息；
-   家长联系方式；
-   教师信息；
-   内部运营记录。

本项目不会公开真实业务数据。

公开仓库中的数据将：

-   使用模拟数据；
-   删除敏感字段；
-   匿名化个人信息；
-   根据业务场景构造示例数据。

------------------------------------------------------------------------

# 11. Project Positioning

本项目希望展示一个完整的数据分析流程：

``` text
Business Problem

↓

Business Process Understanding

↓

Data Audit

↓

Data Modeling

↓

SQL Analysis

↓

Business Insights
```

项目重点不是开发一个新的业务系统，而是展示如何从真实业务问题出发，理解业务流程，整理数据结构，并建立支持运营分析的数据基础。
