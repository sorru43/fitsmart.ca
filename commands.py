import click
from flask.cli import with_appcontext
from extensions import db
from database.models import User, SiteSetting, State, City, Area
from werkzeug.security import generate_password_hash
import os

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')

@click.command('create-admin')
@click.option('--username', prompt='Admin username', help='Admin username')
@click.option('--email', prompt='Admin email', help='Admin email')
@click.option('--password', prompt='Admin password', hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user."""
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        click.echo(f'User with email {email} already exists.')
        return

    # Create admin user
    admin_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=True,
        is_active=True
    )
    
    db.session.add(admin_user)
    db.session.commit()
    click.echo(f'Admin user {username} created successfully.')

@click.command('seed-data')
@with_appcontext
def seed_data_command():
    """Seed the database with sample data."""
    # Create sample meal plans
    meal_plans = [
        {
            'name': 'Weight Loss Plan',
            'description': 'Perfect for those looking to lose weight',
            'price': 2999,
            'duration_days': 30,
            'calories_per_day': 1500,
            'is_featured': True
        },
        {
            'name': 'Muscle Gain Plan',
            'description': 'Ideal for building muscle mass',
            'price': 3499,
            'duration_days': 30,
            'calories_per_day': 2500,
            'is_featured': True
        },
        {
            'name': 'Maintenance Plan',
            'description': 'Keep your current weight and stay healthy',
            'price': 2499,
            'duration_days': 30,
            'calories_per_day': 2000,
            'is_featured': False
        }
    ]
    
    for plan_data in meal_plans:
        existing_plan = MealPlan.query.filter_by(name=plan_data['name']).first()
        if not existing_plan:
            meal_plan = MealPlan(**plan_data)
            db.session.add(meal_plan)
    
    # Create sample site settings
    site_settings = [
        {'key': 'site_name', 'value': 'HealthyRizz'},
        {'key': 'site_description', 'value': 'Your healthy meal delivery service'},
        {'key': 'contact_email', 'value': 'info@healthyrizz.in'},
        {'key': 'contact_phone', 'value': '+91-9876543210'},
        {'key': 'delivery_charge', 'value': '100'},
        {'key': 'free_delivery_threshold', 'value': '1000'},
        {'key': 'trial_days', 'value': '7'},
        {'key': 'trial_price', 'value': '499'}
    ]
    
    for setting_data in site_settings:
        existing_setting = SiteSetting.query.filter_by(key=setting_data['key']).first()
        if not existing_setting:
            site_setting = SiteSetting(**setting_data)
            db.session.add(site_setting)
    
    # Create sample states and cities
    states_data = [
        {'name': 'Maharashtra', 'cities': ['Mumbai', 'Pune', 'Nagpur', 'Thane']},
        {'name': 'Delhi', 'cities': ['New Delhi', 'Delhi']},
        {'name': 'Karnataka', 'cities': ['Bangalore', 'Mysore', 'Hubli']},
        {'name': 'Tamil Nadu', 'cities': ['Chennai', 'Coimbatore', 'Madurai']}
    ]
    
    for state_data in states_data:
        existing_state = State.query.filter_by(name=state_data['name']).first()
        if not existing_state:
            state = State(name=state_data['name'])
            db.session.add(state)
            db.session.flush()  # Get the state ID
            
            for city_name in state_data['cities']:
                existing_city = City.query.filter_by(name=city_name, state_id=state.id).first()
                if not existing_city:
                    city = City(name=city_name, state_id=state.id)
                    db.session.add(city)
    
    db.session.commit()
    click.echo('Sample data seeded successfully.')

@click.command('list-users')
@with_appcontext
def list_users_command():
    """List all users in the database."""
    users = User.query.all()
    if not users:
        click.echo('No users found in the database.')
        return
    
    click.echo('Users in the database:')
    for user in users:
        admin_status = ' (Admin)' if user.is_admin else ''
        active_status = ' (Active)' if user.is_active else ' (Inactive)'
        click.echo(f'- {user.username} ({user.email}){admin_status}{active_status}')

@click.command('reset-db')
@with_appcontext
def reset_db_command():
    """Reset the database (drop all tables and recreate)."""
    if click.confirm('This will delete all data. Are you sure?'):
        db.drop_all()
        db.create_all()
        click.echo('Database reset successfully.')

def init_app(app):
    """Initialize commands with the Flask app."""
    register_commands(app)

def register_commands(app):
    """Register all CLI commands with the Flask app."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(seed_data_command)
    app.cli.add_command(list_users_command)
    app.cli.add_command(reset_db_command) 