
# 教育运营数据管理与分析项目

## 1. 项目概述

本项目是一个基于个人工作经历和实际业务场景的 Data Analytics Portfolio Project。

项目来源于在线语言教育机构日常运营过程中，对业务流程和数据管理方式的观察。

随着学生数量、教师数量以及课程规模不断增加，业务运营逐渐依赖多个 Excel / Google Sheets 文件完成信息记录、流程管理以及数据统计。

不同团队根据自身职责维护不同类型的数据：

| 团队                     | 主要职责      | 数据内容                     |
| ---------------------- | --------- | ------------------------ |
| Marketing / Operations | 市场获客与渠道管理 | 客户来源、内容运营、渠道数据           |
| Sales                  | 客户转化管理    | 客户咨询、试听安排、等级测试、报名信息      |
| Academic Operations    | 教务执行管理    | 学生信息、教师信息、课程安排、课程记录、出勤情况 |

在业务规模较小时，Excel / Google Sheets 具有灵活、低成本的优势，可以快速满足日常运营需求。

但是随着业务流程增加，Excel 文件逐渐承担越来越多的功能：

* 数据存储；
* 信息查询；
* 状态跟踪；
* 问题记录；
* 运营统计；
* 月度汇报。

数据记录、业务流程和分析需求逐渐集中在同一套文件体系中，使后续的数据维护和分析工作变得更加复杂。

因此，本项目希望通过梳理当前业务流程、数据来源以及数据结构，分析现有数据管理方式中的问题，并探索更加结构化的数据管理和分析方法。

---

# 2. Business Context

## 2.1 在线语言教育业务流程

在线语言教育机构通常包含以下业务流程：

```
Marketing Acquisition

        ↓

Customer Inquiry

        ↓

Trial Lesson / Level Assessment

        ↓

Enrollment

        ↓

Course Delivery

        ↓

Renewal / Completion
```

不同阶段会产生不同类型的数据：

| Business Stage        | Generated Data                                       |
| --------------------- | ---------------------------------------------------- |
| Marketing Acquisition | Channel, Campaign, Lead Source                       |
| Customer Inquiry      | Customer Information, Inquiry Time, Follow-up Status |
| Trial Lesson          | Trial Date, Teacher, Level Assessment                |
| Enrollment            | Course Package, Enrollment Date                      |
| Course Delivery       | Student, Teacher, Lesson, Attendance                 |
| Renewal               | Remaining Hours, Renewal Status                      |

这些数据由不同团队产生，并服务于不同业务目的。

---

# 3. Current Data Environment

## 3.1 Spreadsheet-based Data Management

当前业务数据主要通过 Excel / Google Sheets 进行管理。

典型数据流：

```
Marketing Data

        ↓

Sales Data

        ↓

Academic Data

        ↓

Operational Reporting
```

不同文件承担不同业务功能：

| 数据类别             | 示例数据           | 使用部门              |
| ---------------- | -------------- | ----------------- |
| Lead Data        | 客户咨询、来源渠道      | Marketing / Sales |
| Trial Data       | 试听安排、测试结果      | Sales             |
| Enrollment Data  | 报名信息、课程购买      | Sales / Academic  |
| Student Data     | 学生状态、学习信息      | Academic          |
| Lesson Data      | 课程记录、出勤情况      | Academic          |
| Operational Data | 异常记录、教师评价、运营统计 | Operations        |

---

## 3.2 Current Data Management Characteristics

### 数据来源分散

当前业务数据根据不同流程产生，并存储在不同文件中。

例如，一个学生的信息可能同时存在：

* 客户咨询记录；
* 试听记录；
* 报名记录；
* 学生信息表；
* 课程记录表；
* 续费记录。

这使得跨流程查询和分析需要额外的数据整理工作。

---

### 数据维护依赖人工流程

部分业务信息需要员工手动维护：

例如：

* 学生状态变化；
* 教师信息更新；
* 课程安排调整；
* 出勤记录；
* 月度运营统计。

当业务规模扩大时，人工维护成本会逐渐增加。

---

### 数据结构缺少统一设计

当前数据主要根据业务需求逐步形成，而不是按照统一的数据模型设计。

因此可能存在：

* 字段定义不一致；
* 数据关联困难；
* 分类标准不同。

---

# 4. Project Motivation

## 4.1 Business Question

本项目开始于一个实际业务问题：

> 当教育机构不断增长时，原本可以满足日常运营需求的 Excel 管理方式，为什么会逐渐增加数据维护和统计工作的复杂度？

---

## 4.2 Initial Observations

在整理当前业务流程过程中，发现以下问题：

---

## 数据分散（Data Fragmentation）

业务数据存在于多个文件和多个业务环节中。

例如：

学生完整生命周期可能涉及：

```
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

* 历史信息查询困难；
* 跨部门分析成本增加；
* 数据整理时间较长。

---

## 信息重复维护（Duplicate Data Maintenance）

相同业务信息可能在不同文件中重复记录。

例如：

学生信息可能同时存在于：

* 试听记录；
* 报名记录；
* 学生汇总表；
* 课程记录。

可能产生：

* 信息更新不同步；
* 数据版本不一致；
* 人工核对成本增加。

---

## 数据标准不统一（Lack of Standardization）

部分业务字段缺少统一定义。

例如课程类型：

```
1V1

私教

一对一

VIP课程
```

如果缺少统一分类标准，会影响：

* SQL 查询；
* 指标统计；
* 数据分析结果。

---

## 报表生成依赖人工（Manual Reporting）

部分运营指标需要人工整理：

例如：

* 试听转化率；
* 学生数量变化；
* 教师工作量；
* 出勤情况。

随着数据量增加，人工统计容易消耗较多时间。

---

# 5. Business Impact

当前数据管理方式主要影响以下方面：

## 5.1 Operational Efficiency

影响：

* 员工需要花费时间维护多个文件；
* 信息查询依赖人工搜索；
* 新成员需要学习多个数据来源。

---

## 5.2 Data Consistency

影响：

* 不同文件可能存在不同版本的信息；
* 数据更新可能无法同步；
* 统计结果需要人工确认。

---

## 5.3 Analytical Capability

影响：

* 难以快速生成统一业务指标；
* 难以进行跨业务分析；
* 历史数据利用效率有限。

---

# 6. Project Objectives

## 6.1 Understand Current Data Environment

目标：

梳理当前业务中的数据环境：

* 数据来源；
* 数据维护部门；
* 数据用途；
* 数据之间关系。

输出：

* Data Inventory
* Data Dictionary

---

## 6.2 Analyze Data Management Issues

分析：

* 数据分散问题；
* 数据重复维护问题；
* 字段标准问题；
* 数据关联问题。

---

## 6.3 Establish Analytical Data Foundation

根据业务流程设计适合分析的数据模型。

主要业务实体：

| Entity     | Description |
| ---------- | ----------- |
| Student    | 学生信息        |
| Teacher    | 教师信息        |
| Course     | 课程类型        |
| Lesson     | 单次课程记录      |
| Lead       | 客户线索        |
| Enrollment | 报名记录        |

用于支持：

* Marketing Analytics；
* Sales Analytics；
* Academic Operations Analytics；
* Retention Analytics。

---

# 7. Project Scope

## Included

本项目包含：

* 当前业务流程分析；
* 数据来源审计；
* 数据问题分析；
* 数据模型设计；
* SQL 分析；
* Dashboard 原型设计。

---

## Not Included

本项目不包含：

* 替换现有企业系统；
* 开发完整 ERP 系统；
* 建立生产环境数据库；
* 自动化所有业务流程。

---

# 8. Expected Deliverables

## Data Audit

### Data Inventory

用于：

* 记录已有数据来源；
* 明确数据用途；
* 识别数据维护关系。

---

### Data Dictionary

用于：

* 统一字段定义；
* 建立数据标准。

---

## Data Modeling

包括：

* Entity Relationship Diagram (ERD)
* Relational Data Model

---

## Data Analytics

包括：

* SQL Analysis；
* Business Metrics Definition；
* KPI Calculation。

---

## Visualization

包括：

* Power BI Dashboard Prototype。

---

# 9. Project Workflow

本项目按照 Data Analyst 常见工作流程推进：

```
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

Dashboard & Business Insights
```

---

# 10. Data Privacy Statement

由于实际业务数据包含敏感信息，包括：

* 学生信息；
* 家长联系方式；
* 教师信息；
* 内部运营记录。

本项目不会公开真实业务数据。

公开仓库中的数据将：

* 使用模拟数据；
* 删除敏感字段；
* 根据业务场景构造示例数据。

---

# 11. Project Positioning

本项目希望展示一个完整的数据分析流程：

```
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

项目重点不是单独完成某一个分析任务，而是展示如何从真实业务问题出发，建立数据分析流程，并支持运营分析与决策。

---