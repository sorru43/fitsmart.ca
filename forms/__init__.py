"""
Forms package initialization
"""
from .auth_forms import LoginForm, RegisterForm, ProfileForm, MealCalculatorForm, ContactForm, NewsletterForm
from .checkout_forms import CheckoutForm
from .trial_forms import TrialRequestForm
from .forms import ContactForm as GeneralContactForm, CorporateInquiryForm

__all__ = ['LoginForm', 'RegisterForm', 'ProfileForm', 'MealCalculatorForm', 'ContactForm', 'NewsletterForm', 'CheckoutForm', 'TrialRequestForm', 'GeneralContactForm', 'CorporateInquiryForm'] 