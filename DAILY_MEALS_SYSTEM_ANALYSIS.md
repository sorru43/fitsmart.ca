# FitSmart Daily Meals System - Comprehensive Analysis

## Table of Contents
1. [Overview](#overview)
2. [Meal Plan Structure](#meal-plan-structure)
3. [Daily Meal Calculation](#daily-meal-calculation)
4. [Skip Meal Functionality](#skip-meal-functionality)
5. [Delivery Scheduling](#delivery-scheduling)
6. [Meal Tracking System](#meal-tracking-system)
7. [Compensation System](#compensation-system)
8. [Workflow Examples](#workflow-examples)

---

## Overview

FitSmart operates a subscription-based meal delivery service where customers receive daily meals based on their selected meal plan. The system handles:
- **Meal Plan Configuration**: Different plans with various meal types (breakfast, lunch, dinner, snacks)
- **Delivery Scheduling**: Customizable delivery days per week
- **Skip Meal Feature**: Users can skip deliveries with compensation
- **Meal Tracking**: Comprehensive tracking of promised, delivered, and skipped meals
- **Automatic Compensation**: Subscription extension when meals are skipped

---

## Meal Plan Structure

### MealPlan Model (`database/models.py`)

Each meal plan has the following key properties:

```python
class MealPlan:
    # Meal Type Flags
    includes_breakfast = Boolean (default: True)
    includes_lunch = Boolean (default: True)
    includes_dinner = Boolean (default: True)
    includes_snacks = Boolean (default: False)
    
    # Delivery Time Windows
    breakfast_time = "7:00-9:00 AM"
    lunch_time = "12:00-2:00 PM"
    dinner_time = "6:00-8:00 PM"
    
    # Meal Plan Types
    meal_plan_type = 'all_day' | 'breakfast_only' | 'lunch_only' | 'dinner_only' | 
                     'breakfast_lunch' | 'lunch_dinner' | 'breakfast_dinner'
    
    # Dietary Options
    is_vegetarian, is_vegan, is_keto, is_gluten_free, etc.
```

### Meal Plan Types

1. **All Day Plan**: Includes breakfast, lunch, and dinner (3 meals/day)
2. **Breakfast Only**: Only breakfast meals
3. **Lunch Only**: Only lunch meals
4. **Dinner Only**: Only dinner meals
5. **Combination Plans**: Breakfast+Lunch, Lunch+Dinner, Breakfast+Dinner

---

## Daily Meal Calculation

### How Meals Are Calculated (`utils/meal_tracking.py`)

The system calculates meals using the `MealTracker.calculate_meals_promised()` method:

#### Step 1: Count Meals Per Day
```python
meals_per_day = 0
if meal_plan.includes_breakfast: meals_per_day += 1
if meal_plan.includes_lunch: meals_per_day += 1
if meal_plan.includes_dinner: meals_per_day += 1
if meal_plan.includes_snacks: meals_per_day += 1
```

**Example:**
- All Day Plan: 3 meals/day (breakfast + lunch + dinner)
- Lunch Only Plan: 1 meal/day
- Breakfast + Lunch Plan: 2 meals/day

#### Step 2: Get Delivery Days Per Week
```python
delivery_days = subscription.get_delivery_days_list()  # e.g., [0,1,2,3,4] = Mon-Fri
delivery_days_per_week = len(delivery_days)  # e.g., 5 days
```

**Default Delivery Days:**
- Monday-Friday (0,1,2,3,4) = 5 days/week
- Can be customized per subscription

#### Step 3: Calculate Weekly Meals
```python
total_meals_weekly = meals_per_day × delivery_days_per_week
```

**Example:**
- All Day Plan (3 meals/day) × 5 days/week = **15 meals/week**
- Lunch Only Plan (1 meal/day) × 5 days/week = **5 meals/week**

#### Step 4: Calculate Monthly Meals
```python
total_meals_monthly = total_meals_weekly × 4  # 4 weeks per month
```

**Example:**
- All Day Plan: 15 meals/week × 4 = **60 meals/month**
- Lunch Only Plan: 5 meals/week × 4 = **20 meals/month**

#### Step 5: Calculate Current Period Meals
Based on subscription frequency:

```python
if frequency == 'weekly':
    current_period_meals = total_meals_weekly
else:  # monthly
    current_period_meals = total_meals_monthly
```

**Example:**
- **Weekly Subscription** with All Day Plan: **15 meals** per period
- **Monthly Subscription** with All Day Plan: **60 meals** per period

---

## Skip Meal Functionality

### How Skip Meal Works (`routes/subscription_management_routes.py`)

#### 1. Skip Meal Rules

**Cutoff Time Rule:**
- Users must skip meals **1 day before** the delivery date
- Cutoff time: **7:00 PM (19:00)** the day before delivery
- Cannot skip past deliveries
- Cannot skip if cutoff time has passed

**Example:**
- To skip **Wednesday's delivery**, user must skip by **Tuesday 7:00 PM**
- If it's Tuesday 8:00 PM, user cannot skip Wednesday's delivery

#### 2. Holiday Protection

```python
# If there's an active holiday with meal protection
if holiday.protect_meals:
    # Meals cannot be skipped during protected holidays
    return False
```

**Protected Holidays:**
- During active holidays with `protect_meals = True`, users cannot skip deliveries
- This ensures meal preparation isn't disrupted during special periods

#### 3. Skip Meal Process

**Step 1: Validation**
```python
can_skip, cutoff_datetime, meal_type = can_skip_delivery(subscription, delivery_date)
```

Checks:
- ✅ Is delivery date in the future?
- ✅ Is current time before cutoff?
- ✅ Is there a holiday protection?
- ✅ Is delivery already skipped?

**Step 2: Create SkippedDelivery Record**
```python
skipped = SkippedDelivery(
    subscription_id=subscription_id,
    delivery_date=delivery_date,
    reason='user_request',
    meal_type=meal_type.value  # 'breakfast', 'lunch', 'dinner', 'all_day'
)
```

**Step 3: Calculate Compensation**
```python
compensation = calculate_skip_compensation(subscription, delivery_date)
```

**Step 4: Apply Compensation**
- Extends subscription period end date
- Recalculates meal allocation

---

## Delivery Scheduling

### Delivery Days Configuration (`database/models.py`)

```python
class Subscription:
    delivery_days = String  # e.g., "0,1,2,3,4" = Monday-Friday
    # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
```

### Delivery Day Check (`routes/main_routes.py`)

```python
def should_deliver_on_date(subscription, check_date):
    delivery_days = subscription.get_delivery_days_list()  # [0,1,2,3,4]
    weekday = check_date.weekday()  # 0-6
    return weekday in delivery_days
```

**Example:**
- Subscription with `delivery_days = "0,1,2,3,4"` (Mon-Fri)
- Check date: Wednesday (weekday = 2)
- Result: ✅ **Should deliver** (2 is in [0,1,2,3,4])

### Daily Meal Prep (`routes/main_routes.py`)

The admin can view daily meal preparation requirements:

```python
@main_bp.route('/admin/daily-meal-prep')
def daily_meal_prep():
    # For each active subscription:
    # 1. Check if delivery is scheduled for the date
    # 2. Check if delivery is skipped
    # 3. Count meals needed (veg/non-veg, breakfast, etc.)
    # 4. Generate prep list
```

**Daily Prep Data Structure:**
```python
meal_prep_data = {
    meal_plan_id: {
        'name': 'High Protein Plan',
        'veg_count': 5,        # Vegetarian meals needed
        'nonveg_count': 10,    # Non-vegetarian meals needed
        'breakfast_count': 3,  # Breakfast meals needed
        'total_count': 15,      # Total meals needed
        'customers': [...]     # Customer details
    }
}
```

---

## Meal Tracking System

### Meal Status Calculation (`utils/meal_tracking.py`)

The system tracks three key metrics:

#### 1. Promised Meals
```python
promised_meals = calculate_meals_promised(subscription)
# Returns: meals_per_day, delivery_days_per_week, total_meals_weekly, 
#          total_meals_monthly, current_period_meals
```

#### 2. Delivered Meals
```python
delivered_meals = count_delivered_meals(subscription, start_date, end_date)
# Counts all Delivery records with status = DELIVERED
```

#### 3. Skipped Meals
```python
skipped_meals = count_skipped_meals(subscription, start_date, end_date)
# Counts all SkippedDelivery records
```

#### 4. Remaining Meals
```python
remaining_meals = promised_meals - delivered_meals
# Note: Skipped meals are NOT deducted from remaining (compensation extends period)
```

### Complete Meal Status
```python
meal_status = {
    'promised_meals': 60,           # Total meals promised this period
    'delivered_meals': 45,          # Meals actually delivered
    'skipped_meals': 3,             # Meals skipped
    'remaining_meals': 15,          # Meals still remaining
    'completion_percentage': 75.0,  # 45/60 = 75%
    'is_period_complete': False,    # Period not complete yet
    'needs_renewal': False          # Doesn't need renewal yet
}
```

---

## Compensation System

### How Compensation Works (`utils/meal_tracking.py`)

When a meal is skipped, the system compensates by **extending the subscription period**.

#### Weekly Subscription Compensation
```python
if frequency == 'weekly':
    compensation['days_extended'] = 1
    compensation['description'] = 'Subscription extended by 1 day for skipped delivery'
```

**Example:**
- Weekly subscription ends: **Friday, Jan 10**
- User skips **Monday, Jan 6** delivery
- New end date: **Saturday, Jan 11** (extended by 1 day)

#### Monthly Subscription Compensation
```python
elif frequency == 'monthly':
    delivery_days_per_month = len(delivery_days) × 4  # e.g., 5 × 4 = 20
    days_per_delivery = 30 / delivery_days_per_month  # 30 / 20 = 1.5 days
    compensation['days_extended'] = max(1, int(days_per_delivery))
```

**Example:**
- Monthly subscription: 5 delivery days/week = 20 delivery days/month
- Days per delivery: 30 / 20 = **1.5 days**
- User skips 1 delivery → Subscription extended by **2 days** (rounded up)

#### Compensation Application
```python
if compensation['days_extended'] > 0:
    subscription.current_period_end += timedelta(days=compensation['days_extended'])
    # Recalculate meal allocation for extended period
    meal_status = MealTracker.get_meal_status(subscription)
```

**Key Point:** Compensation extends the subscription period, so users don't lose meals - they get them later.

---

## Workflow Examples

### Example 1: Weekly Subscription - All Day Plan

**Setup:**
- Meal Plan: All Day (breakfast + lunch + dinner = 3 meals/day)
- Delivery Days: Monday-Friday (5 days/week)
- Frequency: Weekly

**Calculation:**
1. Meals per day: **3 meals**
2. Delivery days per week: **5 days**
3. Total meals per week: **3 × 5 = 15 meals**
4. Current period meals: **15 meals** (weekly subscription)

**Skip Meal Scenario:**
- User skips **Wednesday's delivery** (3 meals)
- Cutoff: Must skip by **Tuesday 7:00 PM**
- Compensation: Subscription extended by **1 day**
- New period end: Original end date + 1 day
- Remaining meals: Still **15 meals** (period extended, not deducted)

### Example 2: Monthly Subscription - Lunch Only Plan

**Setup:**
- Meal Plan: Lunch Only (1 meal/day)
- Delivery Days: Monday-Friday (5 days/week)
- Frequency: Monthly

**Calculation:**
1. Meals per day: **1 meal**
2. Delivery days per week: **5 days**
3. Total meals per week: **1 × 5 = 5 meals**
4. Total meals per month: **5 × 4 = 20 meals**
5. Current period meals: **20 meals** (monthly subscription)

**Skip Meal Scenario:**
- User skips **Monday's delivery** (1 meal)
- Cutoff: Must skip by **Sunday 7:00 PM**
- Compensation: 
  - Delivery days per month: 5 × 4 = 20 days
  - Days per delivery: 30 / 20 = 1.5 days
  - Extended by: **2 days** (rounded up)
- New period end: Original end date + 2 days
- Remaining meals: Still **20 meals** (period extended)

### Example 3: Daily Meal Prep Workflow

**Scenario:** Admin views meal prep for **Wednesday, January 8**

**Process:**
1. System queries all active subscriptions
2. For each subscription:
   - Checks if Wednesday is a delivery day
   - Checks if delivery is skipped
   - If not skipped, counts meals needed
3. Groups by meal plan:
   - High Protein Plan: 10 customers, 30 meals (10 × 3 meals)
   - Lunch Only Plan: 5 customers, 5 meals (5 × 1 meal)
4. Separates by dietary preference:
   - Vegetarian: 8 meals
   - Non-vegetarian: 27 meals
5. Generates prep list for kitchen

**Result:**
```
Wednesday, January 8 Meal Prep:
- High Protein Plan: 30 meals (8 veg, 22 non-veg)
- Lunch Only Plan: 5 meals (2 veg, 3 non-veg)
Total: 35 meals to prepare
```

---

## Key Features Summary

### ✅ What the System Does

1. **Flexible Meal Plans**: Supports breakfast, lunch, dinner, snacks in any combination
2. **Customizable Delivery Days**: Users can choose which days of the week to receive meals
3. **Skip Meal Feature**: Users can skip deliveries with proper timing rules
4. **Automatic Compensation**: Subscription period extended when meals are skipped
5. **Holiday Protection**: Prevents skipping during protected holidays
6. **Comprehensive Tracking**: Tracks promised, delivered, and skipped meals
7. **Daily Prep Planning**: Admin can view daily meal requirements
8. **Vegetarian Days**: Support for specific vegetarian days per week

### ⚠️ Important Rules

1. **Cutoff Time**: Must skip meals **1 day before** delivery by **7:00 PM**
2. **No Past Skipping**: Cannot skip deliveries that have already passed
3. **Holiday Protection**: Cannot skip during protected holidays
4. **Compensation**: Skipped meals extend subscription period (not deducted)
5. **Meal Counting**: Each delivery counts as all meals in the plan (breakfast + lunch + dinner if applicable)

### 📊 Meal Calculation Formula

```
Total Meals = (Meals Per Day) × (Delivery Days Per Week) × (Weeks Per Period)

Where:
- Meals Per Day = Count of (breakfast + lunch + dinner + snacks)
- Delivery Days Per Week = Number of days in delivery_days list
- Weeks Per Period = 1 (weekly) or 4 (monthly)
```

---

## Database Models

### Subscription
- Links user to meal plan
- Stores delivery days, frequency, period dates
- Tracks subscription status

### MealPlan
- Defines meal types included (breakfast, lunch, dinner, snacks)
- Stores pricing, dietary options, delivery times

### SkippedDelivery
- Records skipped delivery dates
- Links to subscription
- Stores skip reason and meal type

### Delivery
- Records actual deliveries
- Tracks delivery status (PENDING, DELIVERED, FAILED)
- Links to subscription and delivery date

---

## API Endpoints

### User Endpoints
- `POST /skip_delivery/<subscription_id>` - Skip a delivery
- `POST /unskip_delivery/<subscription_id>` - Cancel a skip
- `GET /profile` - View subscription and upcoming deliveries

### Admin Endpoints
- `GET /admin/daily-meal-prep` - View daily meal preparation requirements
- `GET /admin/daily-orders` - View daily orders and deliveries
- `GET /admin/meal-tracking` - View meal tracking statistics

---

## Conclusion

The FitSmart meal delivery system provides a comprehensive solution for managing daily meal subscriptions with:
- Flexible meal plan configurations
- User-friendly skip meal functionality
- Automatic compensation system
- Detailed meal tracking
- Admin tools for daily operations

The system ensures users get value for their subscription while providing flexibility to skip meals when needed, with fair compensation through subscription period extension.

