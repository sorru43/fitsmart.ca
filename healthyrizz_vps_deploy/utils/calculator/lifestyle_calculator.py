"""
Lifestyle Calculator Utilities

This module provides functions for calculating nutritional requirements
and making lifestyle recommendations based on user inputs.
"""

def calculate_bmi(weight, height):
    """
    Calculate BMI (Body Mass Index)
    
    Args:
        weight (float): Weight in kilograms
        height (float): Height in centimeters
        
    Returns:
        float: BMI value
    """
    # Convert height from cm to meters
    height_m = height / 100
    
    # Calculate BMI formula: weight (kg) / height^2 (m^2)
    bmi = weight / (height_m * height_m)
    
    return bmi

def get_bmi_category(bmi):
    """
    Get BMI category
    
    Args:
        bmi (float): BMI value
        
    Returns:
        str: BMI category
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def calculate_bmr(weight, height, age, gender):
    """
    Calculate BMR (Basal Metabolic Rate) using the Mifflin-St Jeor Equation
    
    Args:
        weight (float): Weight in kilograms
        height (float): Height in centimeters
        age (int): Age in years
        gender (str): 'male' or 'female'
        
    Returns:
        float: BMR in calories
    """
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female or other
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    return bmr

def calculate_tdee(bmr, activity_level):
    """
    Calculate TDEE (Total Daily Energy Expenditure)
    
    Args:
        bmr (float): Basal Metabolic Rate
        activity_level (str): Activity level
        
    Returns:
        float: TDEE in calories
    """
    activity_multipliers = {
        'sedentary': 1.2,  # Little or no exercise
        'light': 1.375,    # Light exercise 1-3 days/week
        'moderate': 1.55,  # Moderate exercise 3-5 days/week
        'active': 1.725,   # Hard exercise 6-7 days/week
        'very_active': 1.9 # Very hard exercise & physical job
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return bmr * multiplier

def adjust_calories_for_goal(tdee, goal):
    """
    Adjust calories based on goal
    
    Args:
        tdee (float): Total Daily Energy Expenditure
        goal (str): Goal
        
    Returns:
        float: Adjusted calories
    """
    goal_adjustments = {
        'weight_loss': 0.8,      # 20% deficit
        'maintenance': 1.0,      # No change
        'muscle_gain': 1.1,      # 10% surplus
        'improve_health': 0.95,  # 5% deficit
        'athletic_performance': 1.05  # 5% surplus
    }
    
    multiplier = goal_adjustments.get(goal.lower(), 1.0)
    return tdee * multiplier

def calculate_macros(adjusted_calories, goal, diet_preference):
    """
    Calculate macronutrient requirements
    
    Args:
        adjusted_calories (float): Adjusted calories
        goal (str): Goal
        diet_preference (str): Diet preference
        
    Returns:
        dict: Macronutrient requirements
    """
    # Default macro ratios (protein/carbs/fat)
    default_ratios = {
        'standard': (0.25, 0.50, 0.25),     # Standard balanced diet
        'high_protein': (0.35, 0.40, 0.25), # Higher protein for muscle building
        'low_carb': (0.30, 0.35, 0.35),     # Lower carbs
        'balanced': (0.30, 0.45, 0.25),     # Balanced approach
        'vegetarian': (0.25, 0.55, 0.20),   # Higher carbs for vegetarian
        'keto': (0.30, 0.10, 0.60),         # Keto diet (low carb, high fat)
    }
    
    # Get ratios based on diet preference
    protein_ratio, carb_ratio, fat_ratio = default_ratios.get(
        diet_preference.lower(), default_ratios['standard']
    )
    
    # Adjust ratios based on goal
    if goal.lower() == 'muscle_gain':
        protein_ratio += 0.05
        carb_ratio -= 0.05
    elif goal.lower() == 'weight_loss':
        protein_ratio += 0.05
        carb_ratio -= 0.05
    
    # Calculate macros in grams (protein and carbs 4 cal/g, fat 9 cal/g)
    protein_grams = (adjusted_calories * protein_ratio) / 4
    carb_grams = (adjusted_calories * carb_ratio) / 4
    fat_grams = (adjusted_calories * fat_ratio) / 9
    
    return {
        'protein': protein_grams,
        'carbs': carb_grams,
        'fat': fat_grams,
        'protein_ratio': protein_ratio * 100,
        'carb_ratio': carb_ratio * 100,
        'fat_ratio': fat_ratio * 100
    }

def calculate_water_needs(weight, activity_level):
    """
    Calculate daily water needs
    
    Args:
        weight (float): Weight in kilograms
        activity_level (str): Activity level
        
    Returns:
        float: Water needs in liters
    """
    # Base water intake: 30ml per kg of body weight
    base_intake = weight * 0.03
    
    # Additional water based on activity level
    activity_additions = {
        'sedentary': 0,
        'light': 0.2,
        'moderate': 0.5,
        'active': 0.7,
        'very_active': 1.0
    }
    
    additional = activity_additions.get(activity_level.lower(), 0)
    return base_intake + additional

def get_lifestyle_recommendations(data):
    """
    Generate lifestyle recommendations based on user data
    
    Args:
        data (dict): User data including goal, activity_level, etc.
        
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    # Weight management recommendations
    goal = data.get('goal', '').lower()
    bmi_category = data.get('bmi_category', '').lower()
    
    if goal == 'weight_loss':
        recommendations.append("Aim for a sustainable calorie deficit of 300-500 calories per day.")
        recommendations.append("Include regular strength training to prevent muscle loss during weight loss.")
    elif goal == 'muscle_gain':
        recommendations.append("Ensure you're in a small calorie surplus, with adequate protein intake.")
        recommendations.append("Focus on progressive overload in your strength training program.")
    
    # Protein recommendations
    if goal in ['muscle_gain', 'athletic_performance']:
        recommendations.append("Distribute protein intake evenly throughout the day (4-5 meals with 25-40g protein each).")
    
    # Activity recommendations
    activity_level = data.get('activity_level', '').lower()
    if activity_level in ['sedentary', 'light']:
        recommendations.append("Try to increase your daily activity by walking more, taking the stairs, or adding short activity breaks.")
    
    # Water intake
    water_needs = data.get('water_needs', 0)
    recommendations.append(f"Aim to drink at least {water_needs:.1f} liters of water daily.")
    
    # General health recommendations
    recommendations.append("Include a variety of colorful vegetables and fruits in your diet for optimal micronutrient intake.")
    recommendations.append("Prioritize quality sleep (7-9 hours) to support your fitness and nutrition goals.")
    
    return recommendations

def find_matching_meal_plan(database_plans, user_data, macros):
    """
    Find the best matching meal plan from the database
    
    Args:
        database_plans (list): List of meal plan objects from database
        user_data (dict): User input data
        macros (dict): Calculated macronutrient requirements
        
    Returns:
        tuple: (recommended_plan, alternative_plans)
    """
    # Get user preferences
    gender = user_data.get('gender', '').lower()
    is_vegetarian = user_data.get('diet_preference', '').lower() == 'vegetarian'
    goal = user_data.get('goal', '').lower()
    adjusted_calories = user_data.get('adjusted_calories', 0)
    
    # Convert plans to list if it's a SQLAlchemy query result
    plans = list(database_plans)
    
    # Filter plans based on dietary preferences and goals
    filtered_plans = []
    for plan in plans:
        # Skip inactive plans
        if not plan.is_active:
            continue
        
        # Check if vegetarian preference matches
        if is_vegetarian and not plan.is_vegetarian:
            continue
        
        # Check if gender-specific plan is appropriate
        if plan.for_gender != 'both' and plan.for_gender != gender:
            continue
        
        # Check if plan matches the goal
        plan_tag = plan.tag.lower() if plan.tag else ''
        if goal == 'weight_loss' and not any(tag in plan_tag for tag in ['weight loss', 'low carb', 'keto']):
            continue
        elif goal == 'muscle_gain' and not any(tag in plan_tag for tag in ['muscle gain', 'high protein', 'bulk']):
            continue
        elif goal == 'maintenance' and not any(tag in plan_tag for tag in ['balanced', 'maintenance', 'healthy']):
            continue
        
        filtered_plans.append(plan)
    
    # If no plans match dietary preferences and goals, try matching just dietary preferences
    if not filtered_plans:
        filtered_plans = [p for p in plans if p.is_active and (not is_vegetarian or p.is_vegetarian)]
    
    # If still no plans, return all active plans
    if not filtered_plans:
        filtered_plans = [p for p in plans if p.is_active]
    
    # Score each plan based on how well it matches nutritional needs
    scored_plans = []
    for plan in filtered_plans:
        score = 0
        
        # Parse calorie range
        try:
            cal_range = plan.calories.split('-')
            plan_calories_min = float(cal_range[0])
            plan_calories_max = float(cal_range[1]) if len(cal_range) > 1 else plan_calories_min
        except (ValueError, AttributeError):
            plan_calories_min = plan_calories_max = 2000  # Default if parsing fails
        
        # Parse protein range
        try:
            prot_range = plan.protein.split('-')
            plan_protein_min = float(prot_range[0].replace('g', ''))
            plan_protein_max = float(prot_range[1].replace('g', '')) if len(prot_range) > 1 else plan_protein_min
        except (ValueError, AttributeError):
            plan_protein_min = plan_protein_max = 100  # Default if parsing fails
        
        # Calculate calorie match score (0-40 points)
        calorie_avg = (plan_calories_min + plan_calories_max) / 2
        calorie_distance = abs(calorie_avg - adjusted_calories)
        calorie_score = max(0, 40 - (calorie_distance / 100) * 10)
        score += calorie_score
        
        # Calculate protein match score (0-30 points)
        protein_avg = (plan_protein_min + plan_protein_max) / 2
        protein_distance = abs(protein_avg - macros['protein'])
        protein_score = max(0, 30 - (protein_distance / 20) * 10)
        score += protein_score
        
        # Goals match score (0-30 points)
        plan_tag = plan.tag.lower() if plan.tag else ''
        if goal == 'weight_loss':
            if 'weight loss' in plan_tag:
                score += 30
            elif 'low carb' in plan_tag or 'keto' in plan_tag:
                score += 20
        elif goal == 'muscle_gain':
            if 'muscle gain' in plan_tag:
                score += 30
            elif 'high protein' in plan_tag or 'bulk' in plan_tag:
                score += 20
        elif goal == 'maintenance':
            if 'maintenance' in plan_tag:
                score += 30
            elif 'balanced' in plan_tag or 'healthy' in plan_tag:
                score += 20
        
        scored_plans.append((plan, score))
    
    # Sort plans by score, highest first
    scored_plans.sort(key=lambda x: x[1], reverse=True)
    
    # Get the top recommended plan and 2-3 alternatives
    recommended_plan = scored_plans[0][0] if scored_plans else None
    alternatives = [plan for plan, _ in scored_plans[1:4]] if len(scored_plans) > 1 else []
    
    return recommended_plan, alternatives

def process_calculator_data(form_data, meal_plans):
    """
    Process the calculator form data and generate recommendations
    
    Args:
        form_data (dict): Form data from request
        meal_plans (list): List of meal plan objects from database
        
    Returns:
        dict: Dictionary of results
    """
    # Extract user data
    age = form_data.get('age', 0)
    if isinstance(age, str):
        age = float(age) if age.strip() else 0
    
    weight = form_data.get('weight', 0)
    if isinstance(weight, str):
        weight = float(weight) if weight.strip() else 0
    
    height = form_data.get('height', 0)
    if isinstance(height, str):
        height = float(height) if height.strip() else 0
    
    gender = form_data.get('gender', 'male')
    activity_level = form_data.get('activity_level', 'moderate')
    goal = form_data.get('goal', 'maintenance')
    diet_preference = form_data.get('diet_preference', 'standard')
    
    # Calculate nutritional needs
    bmi = calculate_bmi(weight, height)
    bmi_category = get_bmi_category(bmi)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    adjusted_calories = adjust_calories_for_goal(tdee, goal)
    macros = calculate_macros(adjusted_calories, goal, diet_preference)
    water_needs = calculate_water_needs(weight, activity_level)
    
    # Prepare user data for recommendations
    user_data = {
        'gender': gender,
        'age': age,
        'weight': weight,
        'height': height,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'activity_level': activity_level,
        'goal': goal,
        'diet_preference': diet_preference,
        'adjusted_calories': adjusted_calories,
    }
    
    # Generate lifestyle recommendations
    user_data['water_needs'] = water_needs
    recommendations = get_lifestyle_recommendations(user_data)
    
    # Find matching meal plans
    recommended_plan, alternative_plans = find_matching_meal_plan(meal_plans, user_data, macros)
    
    # Compile results
    results = {
        'bmi': bmi,
        'bmi_category': bmi_category,
        'bmr': bmr,
        'tdee': tdee,
        'adjusted_calories': adjusted_calories,
        'macros': macros,
        'water_needs': water_needs,
        'recommendations': recommendations,
        'recommended_plan': recommended_plan,
        'alternative_plans': alternative_plans
    }
    
    return results