# Pardelta Dashboard - Project Summary

## Overview

- Platform: Streamlit
- Data Source: Supabase (read-only)
- Stores: 8 stores mapped by pc_number, store_name, and address

## Getting Started

1. Install dependencies in your Streamlit environment.
2. Configure Supabase connection variables (read-only credentials).
3. Run the app with Streamlit.

Example:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Functional Specification

### Layout Summary

- Section 1: Ranking tables (4 tables side by side)
- Section 2: Performance table (single table)

### Ranking Tables Spec

- Tables: HME | HME DP_2 | Labour | OSAT
- Columns:

| Column | Type | Description |
| --- | --- | --- |
| Store | text | Store name (sorted by pc_number) |
| Green | integer | Count of green days in period |
| Yellow | integer | Count of yellow days in period |
| Red | integer | Count of red days in period |

- Sorting: Red count descending (stores with most red days appear first)
- Period default: Week to Date (Sunday-Saturday)
- Data logic:
  - For each store and day in the selected period, evaluate the metric value against color ranges
  - Tally color counts per store

### Performance Table Spec

- Columns:

| Column | Type | Description |
| --- | --- | --- |
| Store | text | Store name (sorted by pc_number) |
| HME | number | Average metric for period |
| HME DP_2 | number | Average metric for period |
| Labour | number | Average metric for period |
| OSAT | number | Average metric for period (percent) |

- Rows: All 8 stores sorted by pc_number
- Cell styling: Background color based on performance ranges
- Filters: Week to Date (default) | Month to Date | Year to Date
- Data logic:
  - Compute average value per metric per store for the selected period
  - Apply color based on metric ranges

## Metrics and Color Coding

### 1. HME (Drive-Thru Speed)

- Source: hme_report table
- Calculation: Average of all 5 dayparts (lane_total) per day per store
- Color Ranges:
	- Green: <= 150 seconds
	- Yellow: 150-160 seconds
	- Red: > 160 seconds

### 2. HME DP_2 (Drive-Thru Speed - Daypart 2)

- Source: hme_report table
- Calculation: Only "Daypart 2" data (lane_total) per day per store
- Color Ranges:
	- Green: <= 140 seconds
	- Yellow: 140-150 seconds
	- Red: > 150 seconds

### 3. Labour

- Source: labor_metrics table
- Calculation: Sum of percent_labor for all positions EXCEPT:
	- DD Manager
	- DD Manager - Salary
- Included Positions:
	- DD Crew Plus
	- DD Crew Standard
	- DD Shift Leader Plus
	- Any other positions not in exclusion list
- Color Ranges:
	- Green: < 20%
	- Yellow: 20%-23%
	- Red: > 23%

### 4. OSAT (Guest Satisfaction)

- Source: medallia_report table
- Calculation:
	- Average daily OSAT score (1-5 scale) per store
	- Convert to percentage: (average_osat / 5) * 100
- Color Ranges:
	- Green: > 90%
	- Yellow: 85%-90%
	- Red: < 85%

## Time Periods

- Week to Date: Sunday - Saturday (default)
- Month to Date: Calendar month (e.g., Feb 1-28)
- Year to Date: Calendar year (e.g., Jan 1 - Dec 31)

## Database Tables

### 1. hme_report

- Tracks drive-thru timing metrics
- Key fields: date, store, time_measure (Daypart 1-5), lane_total

### 2. labor_metrics

- Tracks labor hours and costs by position
- Key fields: date, store, pc_number, labor_position, percent_labor

### 3. medallia_report

- Guest satisfaction survey responses
- Key fields: report_date, pc_number, osat (1-5 scale)

### 4. Store Mapping (Config)

- json
- 8 stores with: pc_number, store_name, address, company, bank_account_last4

## Technical Stack

- Frontend: Streamlit
- Database: Supabase (PostgreSQL)
- Data Flow: Read-only queries from Supabase tables

## Example Screenshots and Mock Data

- Screenshots: Place files in docs/screenshots and reference them here.
	- Example: docs/screenshots/overview.png
- Mock data: Use anonymized rows for each source table with a full week of dates.
	- Include at least one green, yellow, and red day for each metric.

