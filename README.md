# Education Operations Analytics

## 在线语言教育机构运营数据分析与管理优化项目

[中文](README.md) | [English](README_EN.md)

---

# 项目简介

本项目基于在线语言教育机构的真实运营场景，探索如何通过**数据整理、数据建模和业务分析方法**，优化日常运营流程，并支持业务决策。

项目关注的问题并不是单纯的数据分析，而是从实际业务流程出发：

> 当教育机构随着学生数量、教师数量和课程规模不断增长，原本依赖 Excel / Google Sheets 的管理方式逐渐变得复杂时，如何通过结构化的数据管理方式提升运营效率。

项目主要覆盖以下业务环节：

- Marketing（市场获客）
- Sales（销售转化）
- Academic Operations（教务运营）
- Retention（学生留存）

---

# 项目背景

在线语言教育机构通常由多个团队共同完成学生生命周期管理。

## Marketing

负责：

- 社交媒体内容运营
- 广告投放
- 客户咨询获取
- 渠道效果记录

---

## Sales

负责：

- 客户沟通
- 试听安排
- 等级测试
- 报名转化

---

## Academic Operations

负责：

- 学生信息管理
- 教师匹配
- 课程安排
- 课程记录
- 出勤管理

---

在业务初期，Excel / Google Sheets 具有灵活、低成本的优势，可以快速支持日常运营。

但随着业务规模扩大，Excel 逐渐承担越来越多功能：

- 数据存储
- 工作流程管理
- 异常事件追踪
- 教师评价
- 月度运营统计

因此逐渐出现以下问题：

- 数据分散在多个文件中
- 不同部门维护不同版本的信息
- 字段命名和分类缺少统一标准
- 数据统计依赖人工整理
- 历史信息查询困难

---

# 项目目标

## 1. 梳理当前业务数据环境

分析：

- 当前使用的数据表
- 数据维护部门
- 数据用途
- 不同数据之间的关系

建立：

- Data Inventory（数据资产清单）
- Data Dictionary（数据字典）

---

## 2. 分析当前数据管理问题

### 数据分散

例如，一个学生的信息可能同时存在：

- 客户咨询记录
- 试听记录
- 报名记录
- 学生信息表
- 课程记录表
- 续费记录

---

### 数据重复维护

同一业务信息可能由多个团队重复记录。

可能导致：

- 信息更新不同步
- 数据统计不一致
- 人工检查成本增加

---

### 数据标准化不足

例如课程类型可能存在：

```
1V1
私教
一对一
VIP课程
```

需要建立统一分类标准。

---

# 数据模型设计

根据业务流程设计：

- 数据实体
- 表之间关系
- 数据库结构

主要业务实体包括：

| Entity | Description |
|---|---|
| Student | 学生信息 |
| Teacher | 教师信息 |
| Course | 课程类型 |
| Lesson | 单节课程记录 |
| Lead | 客户线索 |
| Enrollment | 报名记录 |

---

# 业务分析方向

## Marketing Analytics

分析：

- 不同渠道带来的客户数量
- 广告和内容效果
- 客户来源质量

---

## Sales Analytics

分析：

- 试听转化率
- 销售跟进效率
- 不同来源客户转化情况

---

## Academic Operations Analytics

分析：

- 学生增长趋势
- 教师工作量
- 课程资源利用情况
- 学生出勤情况

---

## Retention Analytics

分析：

- 学生学习参与情况
- 续费情况
- 影响长期学习的因素

---

# 项目流程

本项目按照实际 Data Analyst 工作流程推进：

```
Phase 0
项目定义
(Project Scoping)

        ↓

Phase 1
当前业务流程与数据审计
(Current State Assessment)

        ↓

Phase 2
数据建模
(Data Modeling)

        ↓

Phase 3
数据清洗与 ETL
(Data Cleaning & ETL)

        ↓

Phase 4
SQL 分析与 Dashboard
(SQL Analysis & Visualization)

        ↓

Phase 5
业务洞察与优化建议
(Business Insights)
```

---

# 当前进度

## Phase 0：项目定义 ✅

已完成：

- 项目背景分析
- 业务问题梳理
- 项目目标定义
- 项目范围确定

---

## Phase 1：当前流程与数据审计 🚧

正在进行：

### Marketing Data

包括：

- 小红书客户咨询记录
- 内容运营统计

---

### Sales Data

包括：

- 试听记录
- 等级测试记录
- 报名记录

---

### Academic Data

包括：

- 学生信息
- 教师信息
- 课程记录
- 出勤记录

---

### Operational Data

包括：

- 异常事件记录
- 教师月度评价
- 月度运营汇总

---

# 项目结构

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

# 技术栈

## 数据处理

- Excel / Google Sheets
- SQL
- Python
- Pandas

---

## 数据建模

- Entity Relationship Diagram (ERD)
- Relational Database Design

---

## 数据分析

- SQL Query
- 用户转化分析
- 留存分析
- 运营指标分析

---

## 数据可视化

- Power BI

---

## 项目管理

- Git
- GitHub
- Markdown

---

# 数据隐私说明

由于原始业务数据包含敏感信息：

- 学生信息
- 家长联系方式
- 教师信息
- 内部运营记录

本项目不会上传真实业务数据。

公开仓库中的数据将：

- 使用模拟数据
- 进行匿名化处理
- 删除敏感字段

---

# 后续计划

## Data Modeling

计划完成：

- 数据库 Schema 设计
- ER Diagram
- Fact Table / Dimension Table 划分

---

## Data Pipeline

计划完成：

- 数据清洗
- 字段标准化
- ETL 流程设计

---

## Analytics Dashboard

计划建立：

- Marketing Dashboard
- Sales Dashboard
- Academic Dashboard

---

# 项目总结

本项目希望展示一个完整的数据分析流程：

```
业务问题

↓

现有流程分析

↓

数据审计

↓

数据建模

↓

SQL分析

↓

业务洞察
```

而不是仅关注单次数据分析结果。

---

# Author

## Yiye Chen

Data Analytics / Business Intelligence Portfolio Project

关注方向：

- Data Analysis
- SQL
- Business Intelligence
- Education Operations Analytics