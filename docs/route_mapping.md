# HealthyRizz Route Mapping Documentation

## Admin Routes (Blueprint: 'admin')

### Dashboard Routes
- Route: `/admin` and `/admin/dashboard`
- Function: `admin_dashboard()`
- Template: `admin/dashboard.html`
- URL For: `admin.admin_dashboard`

### User Management
- Route: `/admin/users`
- Function: `admin_users()`
- Template: `admin/users.html`
- URL For: `admin.admin_users`

- Route: `/admin/users/<int:user_id>`
- Function: `admin_view_user()`
- Template: `admin/user_view.html`
- URL For: `admin.admin_view_user`

- Route: `/admin/users/<int:user_id>/edit`
- Function: `admin_edit_user()`
- Template: `admin/user_edit.html`
- URL For: `admin.admin_edit_user`

- Route: `/admin/toggle-user-status`
- Function: `admin_toggle_user_status()`
- Template: N/A (POST only)
- URL For: `admin.admin_toggle_user_status`

- Route: `/admin/toggle-admin-status`
- Function: `admin_toggle_admin_status()`
- Template: N/A (POST only)
- URL For: `admin.admin_toggle_admin_status`

- Route: `/admin/delete-user`
- Function: `admin_delete_user()`
- Template: N/A (POST only)
- URL For: `admin.admin_delete_user`

### Location Management
- Route: `/admin/locations`
- Function: `admin_locations()`
- Template: `admin/locations.html`
- URL For: `admin.admin_locations`

- Route: `/admin/add/location`
- Function: `admin_add_location()`
- Template: `admin/add_location.html`
- URL For: `admin.admin_add_location`

- Route: `/admin/locations/edit/<int:id>`
- Function: `admin_edit_location()`
- Template: `admin/edit_location.html`
- URL For: `admin.admin_edit_location`

- Route: `/admin/locations/delete/<int:id>`
- Function: `admin_delete_location()`
- Template: N/A (POST only)
- URL For: `admin.admin_delete_location`

### Meal Plan Management
- Route: `/admin/meal-plans` and `/admin/meal_plans`
- Function: `admin_meal_plans()`
- Template: `admin/meal_plans.html`
- URL For: `admin.admin_meal_plans`

- Route: `/admin/add/meal-plan`
- Function: `admin_add_meal_plan()`
- Template: `admin/add_meal_plan.html`
- URL For: `admin.admin_add_meal_plan`

- Route: `/admin/toggle-meal-plan-status`
- Function: `admin_toggle_meal_plan_status()`
- Template: N/A (POST only)
- URL For: `admin.admin_toggle_meal_plan_status`

### Trial Requests
- Route: `/admin/trial-requests`
- Function: `admin_trial_requests()`
- Template: `admin/trial_requests.html`
- URL For: `admin.admin_trial_requests`

### Orders Management
- Route: `/admin/orders`
- Function: `admin_orders()`
- Template: `admin/orders.html`
- URL For: `admin.admin_orders`

### Subscription Management
- Route: `/admin/subscriptions`
- Function: `admin_subscriptions()`
- Template: `admin/subscriptions.html`
- URL For: `admin.admin_subscriptions`

### Newsletter Management
- Route: `/admin/newsletters`
- Function: `admin_newsletters()`
- Template: `admin/newsletters.html`
- URL For: `admin.admin_newsletters`

- Route: `/admin/export-newsletters`
- Function: `admin_export_newsletters()`
- Template: N/A (CSV download)
- URL For: `admin.admin_export_newsletters`

- Route: `/admin/delete-newsletter/<int:id>`
- Function: `admin_delete_newsletter()`
- Template: N/A (POST only)
- URL For: `admin.admin_delete_newsletter`

### Service Requests
- Route: `/admin/service-requests`
- Function: `admin_service_requests()`
- Template: `admin/service_requests.html`
- URL For: `admin.admin_service_requests`

### Blog Management
- Route: `/admin/blog`
- Function: `admin_blog()`
- Template: `admin/blog.html`
- URL For: `admin.admin_blog`

- Route: `/admin/add/blog-post`
- Function: `admin_add_blog_post()`
- Template: `admin/add_blog_post.html`
- URL For: `admin.admin_add_blog_post`

- Route: `/admin/delete-blog-post/<int:id>`
- Function: `admin_delete_blog_post()`
- Template: N/A (POST only)
- URL For: `admin.admin_delete_blog_post`

### FAQ Management
- Route: `/admin/faqs`
- Function: `admin_faqs()`
- Template: `admin/faqs.html`
- URL For: `admin.admin_faqs`

- Route: `/admin/add-faq`
- Function: `admin_add_faq()`
- Template: `admin/add_faq.html`
- URL For: `admin.admin_add_faq`

- Route: `/admin/delete-faq/<int:id>`
- Function: `admin_delete_faq()`
- Template: N/A (POST only)
- URL For: `admin.admin_delete_faq`

### Banner Management
- Route: `/admin/banners`
- Function: `admin_banners()`
- Template: `admin/banners.html`
- URL For: `admin.admin_banners`

- Route: `/admin/add-banner`
- Function: `admin_add_banner()`
- Template: `admin/add_banner.html`
- URL For: `admin.admin_add_banner`

### Coupon Management
- Route: `/admin/coupons`
- Function: `admin_coupons()`
- Template: `admin/coupons.html`
- URL For: `admin.admin_coupons`

- Route: `/admin/add-coupon`
- Function: `admin_add_coupon()`
- Template: `admin/add_coupon.html`
- URL For: `admin.admin_add_coupon`

- Route: `/admin/delete-coupon/<int:id>`
- Function: `admin_delete_coupon()`
- Template: N/A (POST only)
- URL For: `admin.admin_delete_coupon`

### Notification Management
- Route: `/admin/notifications`
- Function: `admin_notifications()`
- Template: `admin/send_notifications.html`
- URL For: `admin.admin_notifications`

- Route: `/admin/send-notification`
- Function: `send_notification()`
- Template: N/A (POST only)
- URL For: `admin.send_notification`

- Route: `/admin/notifications/history`
- Function: `notification_history()`
- Template: `admin/notification_history.html`
- URL For: `admin.notification_history`

## Frontend Routes (Main App)

### Public Pages
- Route: `/`
- Function: `index()`
- Template: `index.html`
- URL For: `index`

- Route: `/meal-plans`
- Function: `meal_plans()`
- Template: `meal_plans.html`
- URL For: `meal_plans`

- Route: `/blog`
- Function: `blog()`
- Template: `blog.html`
- URL For: `blog`

- Route: `/blog/<slug>`
- Function: `blog_post()`
- Template: `blog_post.html`
- URL For: `blog_post`

### Authentication
- Route: `/login`
- Function: `login()`
- Template: `login.html`
- URL For: `login`

- Route: `/register`
- Function: `register()`
- Template: `register.html`
- URL For: `register`

- Route: `/logout`
- Function: `logout()`
- Template: N/A
- URL For: `logout`

### User Profile
- Route: `/profile`
- Function: `profile()`
- Template: `profile.html`
- URL For: `profile`

- Route: `/profile/deliveries`
- Function: `user_deliveries()`
- Template: `user_deliveries.html`
- URL For: `user_deliveries`

### Subscription Management
- Route: `/subscribe/<int:plan_id>`
- Function: `subscribe()`
- Template: `subscribe.html`
- URL For: `subscribe`

- Route: `/checkout/<int:plan_id>`
- Function: `checkout()`
- Template: `checkout.html`
- URL For: `checkout`

### Utility Routes
- Route: `/check-location`
- Function: `check_location()`
- Template: N/A (AJAX)
- URL For: `check_location`

- Route: `/verify-coupon`
- Function: `verify_coupon()`
- Template: N/A (AJAX)
- URL For: `verify_coupon`

## Important Notes

1. All admin routes should be prefixed with `admin_` in their function names
2. All admin templates should be in the `templates/admin/` directory
3. All admin routes should use the `admin.` prefix in `url_for()`
4. All admin routes should have both `@login_required` and `@admin_required` decorators
5. Frontend routes should not use the `admin_` prefix
6. Frontend templates should be in the `templates/` directory
7. Frontend routes should use the base name in `url_for()`

## Common Errors to Avoid

1. Using wrong template paths (admin vs frontend)
2. Missing `admin_` prefix in admin route functions
3. Missing `admin.` prefix in admin `url_for()` calls
4. Using wrong route names in redirects
5. Missing required decorators on admin routes
6. Inconsistent naming between routes and templates

## Template Inheritance

### Admin Templates
- Base Template: `admin/base_admin.html`
- All admin templates should extend this base template

### Frontend Templates
- Base Template: `base.html`
- All frontend templates should extend this base template 
