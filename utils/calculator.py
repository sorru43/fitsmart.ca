"""
Calculator Utilities

This module provides functions for calculating nutritional requirements
and making lifestyle recommendations based on user inputs.
"""

def validate_input_data(data):
    """
    Validate input data for meal calculation.
    
    Args:
        data (dict): Input data dictionary
        
    Returns:
        tuple: (validated_data, error_message)
    """
    required_fields = ['age', 'gender', 'weight', 'height', 'activity', 'goal']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return None, f'Missing required fields: {", ".join(missing_fields)}'
    
    try:
        validated = {
            'age': int(data['age']),
            'gender': data['gender'].lower(),
            'weight': float(data['weight']),
            'height': float(data['height']),
            'activity': data['activity'].lower(),
            'goal': data['goal'].lower(),
            'diet_preference': data.get('diet_preference', '').lower()
        }
        
        if not (1 <= validated['age'] <= 120):
            return None, 'Age must be between 1 and 120'
        if not (20 <= validated['weight'] <= 300):
            return None, 'Weight must be between 20 and 300 kg'
        if not (50 <= validated['height'] <= 250):
            return None, 'Height must be between 50 and 250 cm'
        if validated['gender'] not in ['male', 'female']:
            return None, 'Gender must be either male or female'
        if validated['activity'] not in ['sedentary', 'light', 'moderate', 'very', 'extra']:
            return None, 'Invalid activity level'
        if validated['goal'] not in ['lose', 'maintain', 'gain']:
            return None, 'Invalid goal'
            
        return validated, None
        
    except (ValueError, TypeError) as e:
        return None, f'Invalid data format: {str(e)}'

def calculate_bmr(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
    
    Args:
        weight (float): Weight in kg
        height (float): Height in cm
        age (int): Age in years
        gender (str): 'male' or 'female'
        
    Returns:
        float: BMR in calories
    """
    if gender == 'male':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure.
    
    Args:
        bmr (float): Basal Metabolic Rate
        activity_level (str): Activity level
        
    Returns:
        float: TDEE in calories
    """
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'very': 1.725,
        'extra': 1.9
    }
    return bmr * activity_multipliers.get(activity_level, 1.2)

def calculate_macros(calories, weight, goal, diet_preference=None):
    """
    Calculate macronutrient requirements.
    
    Args:
        calories (float): Daily calorie requirement
        weight (float): Weight in kg
        goal (str): Weight goal
        diet_preference (str, optional): Diet preference (keto, high_protein, etc.)
        
    Returns:
        dict: Macronutrient requirements
    """
    # Adjust protein based on goal and diet preference
    protein_multiplier = 2.2  # Default: 2.2g per kg
    
    if diet_preference == 'high_protein' or goal == 'gain':
        protein_multiplier = 2.5
    elif goal == 'lose':
        protein_multiplier = 2.0
        
    protein = weight * protein_multiplier
    protein_calories = protein * 4
    
    # Calculate remaining calories
    remaining_calories = calories - protein_calories
    
    # Adjust fat and carb ratios based on diet preference
    if diet_preference == 'keto':
        # Keto: 5% carbs, 70% fat, 25% protein
        carbs = (calories * 0.05) / 4
        fat = (calories * 0.70) / 9
    elif diet_preference == 'low_carb':
        # Low carb: 20% carbs, 50% fat, 30% protein
        carbs = (calories * 0.20) / 4
        fat = (calories * 0.50) / 9
    elif diet_preference == 'high_protein':
        # High protein: 30% carbs, 30% fat, 40% protein
        carbs = (calories * 0.30) / 4
        fat = (calories * 0.30) / 9
    else:
        # Default balanced: 45% carbs, 30% fat, 25% protein
        carbs = (remaining_calories * 0.60) / 4  # 60% of remaining calories as carbs
        fat = (remaining_calories * 0.40) / 9    # 40% of remaining calories as fat
    
    return {
        'calories': int(calories),
        'protein': int(protein),
        'carbs': int(carbs),
        'fat': int(fat)
    }

def calculate_bmi(weight, height):
    """
    Calculate Body Mass Index.
    
    Args:
        weight (float): Weight in kg
        height (float): Height in cm
        
    Returns:
        float: BMI value
    """
    height_m = height / 100  # Convert cm to m
    return weight / (height_m * height_m)

def get_bmi_category(bmi):
    """
    Get BMI category based on BMI value.
    
    Args:
        bmi (float): BMI value
        
    Returns:
        str: BMI category
    """
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal weight'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

def get_recommendations(data, macros):
    """
    Generate lifestyle and dietary recommendations.
    
    Args:
        data (dict): User input data
        macros (dict): Calculated macros
        
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    # Diet recommendations
    if data.get('diet_preference') == 'keto':
        recommendations.append(f"Keep your carb intake below {macros['carbs']}g per day to maintain ketosis.")
        recommendations.append("Focus on healthy fats like avocados, olive oil, and nuts.")
        recommendations.append("Monitor your ketone levels regularly to ensure you're in ketosis.")
    elif data.get('diet_preference') == 'low_carb':
        recommendations.append(f"Aim to keep your carb intake around {macros['carbs']}g per day.")
        recommendations.append("Choose complex carbs like vegetables and whole grains over simple sugars.")
    elif data.get('diet_preference') == 'high_protein':
        recommendations.append(f"Spread your {macros['protein']}g of protein throughout the day for optimal absorption.")
        recommendations.append("Include a protein source with each meal and snack.")
    
    # Activity recommendations
    if data.get('activity') in ['sedentary', 'light']:
        recommendations.append("Try to increase your daily activity by taking the stairs, walking more, or adding a short workout.")
    
    # Goal-specific recommendations
    if data.get('goal') == 'lose':
        recommendations.append("Create a small calorie deficit and be consistent rather than making drastic cuts.")
        recommendations.append("Include strength training to preserve muscle mass while losing fat.")
    elif data.get('goal') == 'gain':
        recommendations.append("Focus on progressive overload in your workouts to build muscle effectively.")
        recommendations.append("Eat slightly more calories than you burn, focusing on nutrient-dense foods.")
    
    # General recommendations
    recommendations.append("Stay hydrated by drinking at least 8 glasses of water daily.")
    recommendations.append("Aim for 7-9 hours of quality sleep each night for optimal recovery and hormonal balance.")
    
    return recommendations

def match_meal_plan(user_data, macro_needs, meal_plans):
    """
    Match user to the most appropriate meal plan.
    
    Args:
        user_data (dict): User input data
        macro_needs (dict): Calculated macro needs
        meal_plans (list): Available meal plans
        
    Returns:
        tuple: (best_plan, alternative_plans)
    """
    best_plan = None
    best_plan_score = 0
    alternative_plans = []
    
    user_diet = user_data.get('diet_preference', '').lower()
    
    for plan in meal_plans:
        score = 0
        
        # Match diet type
        if user_diet == 'keto' and plan.tag.lower() == 'keto':
            score += 10
        elif user_diet == 'low_carb' and plan.tag.lower() == 'low carb':
            score += 10
        elif user_diet == 'high_protein' and plan.tag.lower() == 'high protein':
            score += 10
        elif user_diet == 'vegetarian' and plan.is_vegetarian:
            score += 10
        elif user_diet == 'balanced' and plan.tag.lower() == 'balanced':
            score += 10
        
        # Match gender specificity if applicable
        if plan.for_gender == user_data.get('gender') or plan.for_gender == 'both':
            score += 5
        
        # Evaluate calorie match
        plan_calories = plan.calories.split('-')
        if len(plan_calories) == 2:
            min_cal = int(plan_calories[0])
            max_cal = int(plan_calories[1])
            
            if min_cal <= macro_needs['calories'] <= max_cal:
                score += 15
            elif abs(min_cal - macro_needs['calories']) < 200 or abs(max_cal - macro_needs['calories']) < 200:
                score += 10
            elif abs(min_cal - macro_needs['calories']) < 400 or abs(max_cal - macro_needs['calories']) < 400:
                score += 5
        
        # If score is better than best so far, update best plan
        if score > best_plan_score:
            if best_plan:
                alternative_plans = [best_plan] + [p for p in alternative_plans if p.id != best_plan.id][:2]
            best_plan = plan
            best_plan_score = score
        elif score > 0:
            alternative_plans.append(plan)
    
    # Return top 3 alternative plans at most
    return best_plan, alternative_plans[:2]

def process_calculator_data(form_data, meal_plans):
    """
    Process meal calculator data and return recommended values.
    
    Args:
        form_data (dict): Dictionary containing user input data
        meal_plans (list): List of available meal plans
        
    Returns:
        dict: Dictionary containing calculated values and recommendations
    """
    # Map form diet preference to internal values
    diet_mapping = {
        'standard': 'balanced',
        'high_protein': 'high_protein',
        'low_carb': 'low_carb',
        'balanced': 'balanced',
        'vegetarian': 'vegetarian',
        'keto': 'keto'
    }
    
    # Convert goal values from form to calculator values
    goal_mapping = {
        'weight_loss': 'lose',
        'maintenance': 'maintain',
        'muscle_gain': 'gain',
        'improve_health': 'maintain',
        'athletic_performance': 'gain'
    }
    
    # Activity level mapping
    activity_mapping = {
        'sedentary': 'sedentary',
        'light': 'light',
        'moderate': 'moderate',
        'very_active': 'very',
        'extra_active': 'extra'
    }
    
    # Prepare validated data
    validated_data = {
        'age': int(form_data.get('age', 0)),
        'gender': form_data.get('gender', 'male').lower(),
        'weight': float(form_data.get('weight', 0)),
        'height': float(form_data.get('height', 0)),
        'activity': activity_mapping.get(form_data.get('activity_level', ''), 'moderate'),
        'goal': goal_mapping.get(form_data.get('goal', ''), 'maintain'),
        'diet_preference': diet_mapping.get(form_data.get('diet_preference', ''), '')
    }
    
    # Calculate BMR and TDEE
    bmr = calculate_bmr(
        validated_data['weight'],
        validated_data['height'],
        validated_data['age'],
        validated_data['gender']
    )
    
    tdee = calculate_tdee(bmr, validated_data['activity'])
    
    # Adjust calories based on goal
    goal_adjustments = {
        'lose': 0.85,  # 15% calorie deficit
        'maintain': 1.0,
        'gain': 1.15   # 15% calorie surplus
    }
    
    adjusted_calories = tdee * goal_adjustments.get(validated_data['goal'], 1.0)
    
    # Calculate macronutrients
    macros = calculate_macros(
        adjusted_calories,
        validated_data['weight'],
        validated_data['goal'],
        validated_data['diet_preference']
    )
    
    # Calculate BMI
    bmi = calculate_bmi(validated_data['weight'], validated_data['height'])
    bmi_category = get_bmi_category(bmi)
    
    # Get recommendations
    recommendations = get_recommendations(validated_data, macros)
    
    # Match with meal plan
    recommended_plan, alternative_plans = match_meal_plan(validated_data, macros, meal_plans)
    
    # Prepare result dictionary
    result = {
        'tdee': int(tdee),
        'adjusted_calories': adjusted_calories,
        'macros': macros,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'recommendations': recommendations,
        'recommended_plan': recommended_plan,
        'alternative_plans': alternative_plans
    }
    
    return result
