# 02 Current Workflow Analysis

# 教育运营业务流程分析与现有工作流程评估

## 1. Introduction

本文件基于 `01_project_background`
中描述的业务背景，进一步分析在线语言教育机构当前实际运营流程。

如果说：

-   `01 Project Background` 主要回答"为什么需要这个项目"；
-   `02 Current Workflow Analysis`
    则回答"当前业务是如何运行的，以及现有流程为什么会产生数据管理问题"。

本章节重点分析：

-   Marketing 如何产生客户线索；
-   Sales 如何完成客户转化；
-   Academic Operations 如何管理课程交付；
-   私教与班课为什么需要不同管理方式；
-   当前 Workflow 中的数据问题和流程瓶颈。

------------------------------------------------------------------------

# 2. Overall Business Workflow

当前学生生命周期主要包括：

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

不同阶段由不同团队参与：

  ------------------------------------------------------------------------------
  Stage                   Responsible Team        Main Activity
  ----------------------- ----------------------- ------------------------------
  Marketing Acquisition   Marketing / Operations  内容运营、广告投放、获取咨询

  Customer Inquiry        Sales                   客户沟通、需求确认

  Trial / Assessment      Sales + Academic        试听安排、等级测试

  Enrollment              Sales + Academic        报名确认、课程安排

  Course Delivery         Academic Operations     排课、教师协调、课程记录

  Renewal                 Sales + Academic        续费跟进
  ------------------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Marketing Acquisition Workflow

## 3.1 Content Operation Process

当前市场获客主要依靠内容运营和广告投放。

流程：

``` text
Content Creation

↓

Post Publishing

↓

Advertisement Promotion

↓

Customer Interaction

↓

Sales Follow-up
```

运营人员负责：

-   创建内容；
-   管理账号；
-   发布帖子；
-   观察曝光和互动；
-   配合投流获取客户。

------------------------------------------------------------------------

## 3.2 Marketing Data Flow

当前产生的数据包括：

### Account Level

账号维度：

-   账号名称；
-   运营人员；
-   粉丝数量；
-   总曝光。

### Post Level

帖子维度：

-   帖子 ID；
-   作品名称；
-   发布时间；
-   曝光量。

### Customer Interaction Level

客户行为维度：

-   点击广告；
-   私信；
-   评论；
-   咨询时间；
-   回复时间。

当前问题：

不同业务粒度的数据可能存在于同一管理体系中，需要进一步区分：

``` text
Account

↓

Post

↓

Customer Interaction
```

------------------------------------------------------------------------

# 4. Lead Generation Workflow

## 4.1 Customer Inquiry Process

客户咨询主要来自：

## 主动咨询

客户主动点击广告：

``` text
Advertisement

↓

Click

↓

Inquiry
```

## 被动私信

运营主动联系潜在客户：

``` text
Post Exposure

↓

Operation Message

↓

Customer Response
```

## 主动评论

客户在帖子下产生互动：

``` text
Post

↓

Comment

↓

Sales Follow-up
```

## 回访

之前未完成转化的客户重新回复。

------------------------------------------------------------------------

## 4.2 Lead Record Management

当前客户咨询记录包含：

-   咨询日期；
-   咨询类型；
-   广告贴编号；
-   引流账号；
-   客户账号；
-   咨询时间；
-   回复时间；
-   响应时间；
-   销售负责人；
-   微信添加状态；
-   客户关键词；
-   地区信息。

当前流程：

``` text
Customer Interaction

↓

Lead Record

↓

Sales Assignment

↓

Follow-up
```

------------------------------------------------------------------------

## 4.3 Lead Entity Problem

当前客户咨询数据存在一个重要问题：

一条记录通常代表：

``` text
Customer Interaction Event
```

而不是：

``` text
Unique Customer
```

例如：

同一个客户可能：

-   多次点击广告；
-   多次咨询；
-   不同日期再次回复。

因此后续数据模型需要区分：

### Lead

客户主体：

-   Customer ID；
-   Account；
-   Region。

### Lead Interaction

客户行为：

-   Click；
-   Inquiry；
-   Comment；
-   Follow-up。

------------------------------------------------------------------------

# 5. Sales Workflow

## 5.1 Sales Responsibility

销售主要负责：

-   客户沟通；
-   需求确认；
-   课程推荐；
-   试听安排；
-   报名转化。

销售连接：

``` text
Marketing

↓

Sales

↓

Academic Operations
```

------------------------------------------------------------------------

## 5.2 Customer Conversion Funnel

当前转化流程：

``` text
Lead

↓

Sales Contact

↓

Wechat Added

↓

Trial / Assessment

↓

Enrollment

↓

Student
```

关键状态：

-   是否回复；
-   是否添加微信；
-   是否预约试听；
-   是否报名。

------------------------------------------------------------------------

# 6. Trial and Level Assessment Workflow

## 6.1 Trial Lesson

试听流程：

``` text
Customer Request

↓

Collect Student Information

↓

Arrange Teacher

↓

Trial Lesson

↓

Teacher Feedback

↓

Sales Follow-up
```

试听数据包括：

-   学生年龄；
-   当前水平；
-   学习目标；
-   教师反馈；
-   推荐课程。

------------------------------------------------------------------------

## 6.2 Level Assessment

等级测试流程：

``` text
Assessment Request

↓

Teacher Evaluation

↓

Level Result

↓

Course Recommendation
```

------------------------------------------------------------------------

# 7. Enrollment Workflow

报名后：

``` text
Enrollment Confirmation

↓

Student Information Collection

↓

Course Assignment

↓

Teacher Assignment

↓

Academic Management
```

产生：

-   学生信息；
-   课程类型；
-   课时；
-   销售负责人；
-   教务负责人。

------------------------------------------------------------------------

# 8. Academic Operations Workflow

Academic Operations 负责课程执行：

包括：

-   学生管理；
-   教师协调；
-   排课；
-   课程记录；
-   学习反馈；
-   异常处理；
-   续费提醒。

------------------------------------------------------------------------

# 9. Private Course Workflow

## 9.1 Private Course Characteristics

私教包括：

-   1V1；
-   1V2；
-   1V3；
-   1V4。

私教的核心特点：

> 学生数量较少，因此课程安排高度依赖学生个人需求。

------------------------------------------------------------------------

## 9.2 Private Course Scheduling Logic

私教排课：

``` text
Student Availability

+

Teacher Availability

+

Other Students Availability (1VN)

↓

Course Schedule
```

由于学生数量较少：

一个学生的需求变化可能影响整个课程安排。

例如：

``` text
Student requests schedule change

↓

Check teacher availability

↓

Check other students availability

↓

Rearrange schedule
```

因此私教管理具有：

-   高灵活性；
-   高协调成本；
-   高变化频率。

------------------------------------------------------------------------

# 10. Group Class Workflow

## 10.1 Group Class Characteristics

班课：

-   学生数量较多；
-   时间相对固定；
-   教师固定；
-   班级结构稳定。

流程：

``` text
Class Group

↓

Teacher

↓

Students

↓

Lesson Schedule
```

------------------------------------------------------------------------

## 10.2 Group Class Scheduling Logic

班课遵循：

> 班级整体安排优先于个人需求。

原因：

-   单个学生调整会影响多人；
-   教师时间已经确定；
-   需要保证多数学生安排。

因此：

-   学生通常跟随班级时间；
-   不会因为单个学生需求频繁改变整体课程。

------------------------------------------------------------------------

# 11. Private Course vs Group Class

                 Private Course                  Group Class
  -------------- ------------------------------- --------------------
  管理核心       学生个人需求                    班级整体
  人数           1-4人                           多学生
  排课方式       高度灵活                        相对固定
  时间变化       高频                            较低
  主要挑战       时间协调                        班级稳定
  数据模型方向   Course + Student Relationship   Class + Enrollment

------------------------------------------------------------------------

# 12. Lesson Delivery Workflow

课程执行：

``` text
Scheduled Lesson

↓

Teacher Teaching

↓

Lesson Record

↓

Teacher Feedback

↓

Academic Follow-up
```

课程记录：

-   学生；
-   教师；
-   日期；
-   时间；
-   课程编号；
-   课时；
-   学习内容；
-   教师反馈。

------------------------------------------------------------------------

# 13. Current Workflow Problems

## 13.1 Business Process and Data Structure Mismatch

当前数据结构无法完全表达真实业务：

-   Lead 与 Interaction 混合；
-   Student 与 Task 混合；
-   Private Course 与 Group Class 混合。

------------------------------------------------------------------------

## 13.2 Manual Coordination Dependency

大量流程依赖人工：

-   排课；
-   教师协调；
-   学生通知；
-   状态更新；
-   月度统计。

------------------------------------------------------------------------

## 13.3 Lack of Historical Tracking

当前部分变化通过修改当前表格体现：

例如：

-   学生状态；
-   排课时间；
-   续费状态。

导致：

-   历史变化无法追踪；
-   生命周期分析困难。

------------------------------------------------------------------------

## 13.4 Lack of Standardized Data Definition

不同员工可能使用不同分类：

例如：

``` text
1V1
私教
VIP
一对一
```

影响：

-   SQL 查询；
-   KPI；
-   Dashboard。

------------------------------------------------------------------------

## 13.5 Mixed Data Granularity

当前流程中存在：

-   Account Level；
-   Post Level；
-   Customer Level；
-   Student Level；
-   Task Level。

如果混合管理，会增加统计错误风险。

------------------------------------------------------------------------

## 13.6 Weak Entity Relationship

当前多个业务表主要通过：

-   姓名；
-   微信；
-   人工判断；

进行关联。

缺少统一：

-   Lead_ID；
-   Student_ID；
-   Course_ID；
-   Teacher_ID。

------------------------------------------------------------------------

## 13.7 Knowledge Dependency

大量业务规则依赖员工经验：

例如：

-   私教如何调整；
-   班课如何管理；
-   哪些学生需要跟进。

导致：

-   新员工学习成本高；
-   流程复制困难。

------------------------------------------------------------------------

## 13.8 Limited Analytical Capability

当前数据主要支持日常运营，而不是分析。

难以快速回答：

-   哪些渠道带来有效客户；
-   销售转化表现；
-   学生增长趋势；
-   续费情况；
-   教师工作量。

------------------------------------------------------------------------

# 14. Next Step: Data Audit

基于当前 Workflow Analysis，下一阶段需要：

## Data Inventory

明确：

-   数据来源；
-   数据负责人；
-   更新频率；
-   数据用途。

## Data Dictionary

定义：

-   字段；
-   数据类型；
-   标准分类。

## Data Modeling

建立：

-   Entity；
-   Relationship；
-   Event；
-   Workflow Status。

目标：

将当前 Spreadsheet Workflow 转换为更加结构化的数据分析基础。
