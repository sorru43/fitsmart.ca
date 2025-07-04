"""
Calculator package for Fit Smart.
Provides tools for calculating nutritional requirements, lifestyle recommendations,
and finding the best matching meal plans based on user input.
"""

from .lifestyle_calculator import (
    calculate_bmi,
    get_bmi_category,
    calculate_bmr,
    calculate_tdee,
    adjust_calories_for_goal,
    calculate_macros,
    calculate_water_needs,
    get_lifestyle_recommendations,
    find_matching_meal_plan,
    process_calculator_data
)

__all__ = [
    'calculate_bmi',
    'get_bmi_category',
    'calculate_bmr',
    'calculate_tdee',
    'adjust_calories_for_goal',
    'calculate_macros',
    'calculate_water_needs',
    'get_lifestyle_recommendations',
    'find_matching_meal_plan',
    'process_calculator_data'
]