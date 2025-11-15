# Canada Delivery Model - Evening Delivery System

## Overview

In Canada, FitSmart operates an **evening delivery model** where meals are delivered **one day before** the consumption date. This document explains how the system handles this delivery model.

---

## Delivery Model

### How It Works

1. **Meal Consumption Date**: The date when the customer will consume/eat the meals (e.g., Wednesday)
2. **Actual Delivery Date**: The evening before the consumption date (e.g., Tuesday evening)
3. **Delivery Window**: 6:00 PM - 10:00 PM (evening)

### Example Timeline

```
Monday 12:00 PM  →  Cutoff time to skip Wednesday meals
Tuesday Evening  →  Meals delivered (6:00 PM - 10:00 PM)
Wednesday        →  Customer consumes meals
```

**To skip Wednesday meals:**
- Must skip by **Monday 12:00 PM** (2 days before consumption)
- This gives kitchen **36+ hours** notice before Tuesday evening delivery

---

## Key Concepts

### 1. Meal Consumption Date vs Delivery Date

**Important:** Throughout the system, `delivery_date` in the database represents the **meal consumption date** (when customer will eat), NOT the actual delivery date.

- **Database `delivery_date`**: Meal consumption date (e.g., Wednesday)
- **Actual delivery**: Evening before (e.g., Tuesday evening)

### 2. Skip Meal Cutoff

**Cutoff Rule:**
- Must skip by **2 days before meal consumption date**
- Cutoff time: **12:00 PM (noon)**
- This ensures **36+ hours** notice before actual evening delivery

**Example:**
- To skip **Wednesday meals** (delivered Tuesday evening)
- Must skip by **Monday 12:00 PM**
- Cutoff: Monday 12:00 PM
- Actual delivery: Tuesday 6:00 PM - 10:00 PM
- Meal consumption: Wednesday

### 3. Daily Meal Prep

When admin views meal prep for a date, they see:
- **Prep date**: Date when meals are prepared (e.g., Tuesday)
- **Meals shown**: Meals for **next day consumption** (e.g., Wednesday)
- **Delivery**: Tuesday evening

---

## Configuration

### Config Settings (`config.py`)

```python
# Delivery Model Configuration (Canada)
DELIVERY_MODEL = 'evening_before'  # 'evening_before' or 'same_day'
DELIVERY_EVENING_START = '18:00'  # 6:00 PM - Start of evening delivery window
DELIVERY_EVENING_END = '22:00'    # 10:00 PM - End of evening delivery window
SKIP_MEAL_CUTOFF_HOURS_BEFORE_DELIVERY = 36  # Hours before actual delivery time
SKIP_MEAL_CUTOFF_TIME = '12:00'  # 12:00 PM (noon) cutoff time
```

---

## Helper Functions

### `get_actual_delivery_date(meal_consumption_date)`

Converts meal consumption date to actual delivery date.

```python
# Example
meal_consumption_date = Wednesday
actual_delivery_date = Tuesday  # (evening before)
```

### `get_meal_consumption_date(actual_delivery_date)`

Converts actual delivery date to meal consumption date.

```python
# Example
actual_delivery_date = Tuesday evening
meal_consumption_date = Wednesday
```

### `get_cutoff_time_for_meal(meal_type, meal_consumption_date)`

Calculates cutoff time for skipping meals.

```python
# Example
meal_consumption_date = Wednesday
cutoff_datetime = Monday 12:00 PM  # (2 days before at noon)
```

---

## User-Facing Messages

### Skip Meal Success Message

```
✅ Meals for Wednesday (delivered Tuesday evening) have been skipped. 
   Subscription extended by 1 day for skipped delivery.
```

### Cutoff Time Message

```
Cannot skip meals for Wednesday. Cutoff time was Monday at 12:00 PM.
```

### Upcoming Deliveries Display

```
Wednesday, January 10
Meals delivered: Tuesday, January 9 (6:00 PM - 10:00 PM)
```

---

## Database Schema

### SkippedDelivery Table

```python
class SkippedDelivery:
    delivery_date  # Meal consumption date (e.g., Wednesday)
    subscription_id
    created_at
```

**Note:** `delivery_date` stores meal consumption date, not actual delivery date.

### Delivery Table

```python
class Delivery:
    delivery_date  # Meal consumption date (e.g., Wednesday)
    status         # PENDING, DELIVERED, FAILED
    delivery_time  # Actual delivery time (Tuesday evening)
```

**Note:** `delivery_date` stores meal consumption date. `delivery_time` stores actual delivery time.

---

## Daily Meal Prep Workflow

### Admin View: Tuesday Meal Prep

1. Admin views meal prep for **Tuesday**
2. System shows meals needed for **Wednesday consumption**
3. Meals are prepared Tuesday
4. Meals are delivered **Tuesday evening** (6:00 PM - 10:00 PM)
5. Customer receives meals Tuesday evening
6. Customer consumes meals **Wednesday**

### Code Flow

```python
# Admin views prep for Tuesday
prep_date = Tuesday

# System calculates meals for next day (Wednesday)
meal_consumption_date = prep_date + 1 day  # Wednesday

# System checks which subscriptions need meals for Wednesday
for subscription in active_subscriptions:
    if should_deliver_on_date(subscription, meal_consumption_date):
        # Add to prep list
        # Meals will be delivered Tuesday evening
```

---

## Skip Meal Workflow

### User Skips Wednesday Meals

1. **User Action**: User clicks "Skip" for Wednesday meals
2. **System Check**: 
   - Current date: Monday 10:00 AM
   - Meal consumption date: Wednesday
   - Cutoff: Monday 12:00 PM
   - Result: ✅ Can skip (before cutoff)
3. **System Action**:
   - Creates `SkippedDelivery` record with `delivery_date = Wednesday`
   - Calculates compensation (extends subscription)
   - Updates subscription period end date
4. **User Message**: 
   ```
   ✅ Meals for Wednesday (delivered Tuesday evening) have been skipped.
   ```

### User Tries to Skip After Cutoff

1. **User Action**: User clicks "Skip" for Wednesday meals
2. **System Check**: 
   - Current date: Monday 1:00 PM
   - Meal consumption date: Wednesday
   - Cutoff: Monday 12:00 PM
   - Result: ❌ Cannot skip (after cutoff)
3. **System Action**:
   - Shows error message
   - Does not create skip record
4. **User Message**: 
   ```
   Cannot skip meals for Wednesday. Cutoff time was Monday at 12:00 PM.
   ```

---

## Benefits of This Model

1. **Fresh Meals**: Customers receive meals the evening before, ensuring freshness
2. **Convenience**: Meals ready for next day consumption
3. **Kitchen Planning**: 36+ hours notice for skip requests allows better planning
4. **Flexibility**: Customers can plan ahead and skip meals with sufficient notice

---

## Migration Notes

If switching from same-day to evening-before model:

1. Update `config.py`:
   ```python
   DELIVERY_MODEL = 'evening_before'
   ```

2. Existing `delivery_date` values in database represent meal consumption dates (no migration needed)

3. Update user-facing messages to clarify delivery timing

4. Update admin daily prep view to show next-day meals

---

## Testing Scenarios

### Scenario 1: Skip Wednesday Meals (Before Cutoff)

- **Current Time**: Monday 10:00 AM
- **Meal Date**: Wednesday
- **Cutoff**: Monday 12:00 PM
- **Expected**: ✅ Can skip

### Scenario 2: Skip Wednesday Meals (After Cutoff)

- **Current Time**: Monday 1:00 PM
- **Meal Date**: Wednesday
- **Cutoff**: Monday 12:00 PM
- **Expected**: ❌ Cannot skip

### Scenario 3: Skip Tomorrow's Meals

- **Current Time**: Monday 10:00 AM
- **Meal Date**: Tuesday (tomorrow)
- **Cutoff**: Sunday 12:00 PM (already passed)
- **Expected**: ❌ Cannot skip (cutoff already passed)

### Scenario 4: Daily Meal Prep

- **Prep Date**: Tuesday
- **Meals Shown**: Wednesday meals
- **Delivery**: Tuesday evening (6:00 PM - 10:00 PM)
- **Consumption**: Wednesday

---

## Summary

The Canada delivery model ensures:
- ✅ Meals delivered evening before consumption
- ✅ 36+ hours notice for skip requests
- ✅ Clear communication to customers about delivery timing
- ✅ Efficient kitchen planning and preparation
- ✅ Fresh meals ready for next-day consumption

