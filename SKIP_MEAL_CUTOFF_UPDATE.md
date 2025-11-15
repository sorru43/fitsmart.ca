# Skip Meal Cutoff Update - Same Day 10 AM

## Summary

Updated the skip meal cutoff time to **same day at 10:00 AM**. After 10 AM, users can still mark meals for donation/no delivery to save delivery resources.

---

## Changes Made

### 1. Configuration Updated (`config.py`)

**Before:**
- Cutoff: 2 days before meal consumption date at 12:00 PM
- Example: Skip Wednesday → Must skip by Monday 12:00 PM

**After:**
- Cutoff: Same day (meal consumption date) at 10:00 AM
- Example: Skip Wednesday → Must skip by Wednesday 10:00 AM
- After 10 AM: Can mark for donation/no delivery

```python
SKIP_MEAL_CUTOFF_TIME = '10:00'  # 10:00 AM cutoff time (same day)
SKIP_MEAL_CUTOFF_DAYS_BEFORE = 0  # 0 = same day cutoff
```

### 2. Database Model Updated (`database/models.py`)

Added fields to `SkippedDelivery` model:

```python
class SkippedDelivery:
    skip_type = String  # 'regular', 'donation', 'no_delivery'
    notes = Text  # Additional notes about the skip
```

### 3. Skip Logic Updated (`routes/subscription_management_routes.py`)

**Updated Functions:**

1. **`get_cutoff_time_for_meal()`**
   - Now calculates same-day cutoff at 10:00 AM
   - Cutoff date: Same as meal consumption date

2. **`can_skip_delivery()`**
   - Returns 4 values: `(can_skip, cutoff_datetime, meal_type, can_donate)`
   - `can_donate`: True if after cutoff but same day

3. **`skip_delivery()`**
   - Handles regular skip before 10 AM
   - Shows donation option if after cutoff

4. **`mark_donation()`** (NEW)
   - New route for marking meals for donation/no delivery after cutoff
   - Saves delivery resources even if too late to skip
   - No compensation (meals already prepared)

---

## How It Works

### Scenario 1: Skip Before 10 AM

**Timeline:**
- **Wednesday 9:00 AM**: User wants to skip Wednesday meals
- **Cutoff**: Wednesday 10:00 AM
- **Result**: ✅ Can skip
- **Action**: Regular skip with compensation
- **Message**: "Meals for Wednesday have been skipped. Subscription extended by 1 day."

### Scenario 2: Skip After 10 AM (Same Day)

**Timeline:**
- **Wednesday 11:00 AM**: User wants to skip Wednesday meals
- **Cutoff**: Wednesday 10:00 AM (already passed)
- **Result**: ❌ Cannot skip, but can mark for donation
- **Action**: Mark for donation/no delivery
- **Message**: "Skip cutoff (10:00 AM) has passed. You can mark this for donation/no delivery to save delivery resources."

### Scenario 3: Mark for Donation

**Timeline:**
- **Wednesday 11:00 AM**: User marks meals for donation
- **Result**: ✅ Marked for donation
- **Action**: Creates skip record with `skip_type='donation'`
- **Message**: "Meals for Wednesday marked for donation. This saves delivery resources and helps those in need. Thank you!"
- **Note**: No compensation (meals already prepared)

---

## Skip Types

### 1. Regular Skip (`skip_type='regular'`)
- Before 10 AM cutoff
- Full compensation (subscription extended)
- Meals not prepared

### 2. Donation (`skip_type='donation'`)
- After 10 AM cutoff, same day
- No compensation (meals already prepared)
- Meals can be donated to those in need
- Saves delivery resources

### 3. No Delivery (`skip_type='no_delivery'`)
- After 10 AM cutoff, same day
- No compensation (meals already prepared)
- Delivery not attempted
- Saves delivery guy time

---

## Benefits

1. **Flexibility**: Users can still save delivery resources even after cutoff
2. **Resource Efficiency**: Delivery team knows not to deliver
3. **Social Impact**: Donation option helps those in need
4. **Cost Savings**: Reduces wasted delivery attempts
5. **User Satisfaction**: Users feel they can still take action

---

## API Endpoints

### Regular Skip (Before 10 AM)
```
POST /skip_delivery/<subscription_id>
Form data:
  - delivery_date: YYYY-MM-DD (meal consumption date)
```

### Mark for Donation (After 10 AM)
```
POST /mark_donation/<subscription_id>
Form data:
  - delivery_date: YYYY-MM-DD (meal consumption date)
  - skip_type: 'donation' or 'no_delivery'
```

---

## Admin View

Admins can see skip types in daily orders:
- Regular skips: Full compensation applied
- Donation skips: Meals available for donation
- No delivery: Delivery not attempted

---

## User Experience

### Before 10 AM
- User sees "Skip" button
- Clicking skip works normally
- Gets compensation

### After 10 AM (Same Day)
- User sees "Skip" button (disabled or shows message)
- Message: "Cutoff passed. Mark for donation?"
- User can click "Mark for Donation" or "No Delivery"
- No compensation but saves resources

---

## Database Migration

If upgrading existing database, add new fields:

```sql
ALTER TABLE skipped_delivery 
ADD COLUMN skip_type VARCHAR(20) DEFAULT 'regular';

ALTER TABLE skipped_delivery 
ADD COLUMN notes TEXT;
```

Existing records will have `skip_type='regular'` by default.

---

## Testing Checklist

- [ ] Skip Wednesday meals before 10 AM → Should succeed with compensation
- [ ] Skip Wednesday meals after 10 AM → Should show donation option
- [ ] Mark for donation after cutoff → Should save without compensation
- [ ] Mark for no delivery after cutoff → Should save without compensation
- [ ] Skip past dates → Should fail
- [ ] Admin view shows skip types correctly
- [ ] Daily orders exclude donation/no_delivery from delivery list

