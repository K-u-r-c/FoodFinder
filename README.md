# FoodOnline Marketplace

A Django-based food delivery marketplace where customers can order from multiple restaurants and vendors can manage their menus and orders. Like Pyszne.pl

## Features

**Customer Features:**
- User registration and profile management
- Location-based restaurant search
- Shopping cart with multiple vendors
- Order tracking and history
- PayPal payment integration

**Vendor Features:**
- Restaurant registration with admin approval
- Menu management (categories and food items)
- Opening hours configuration
- Order management and tracking
- Revenue dashboard

**Admin Features:**
- Vendor approval system
- Tax configuration
- Order oversight

## Technical Stack

- **Backend:** Django 5.0.1
- **Database:** PostgreSQL with PostGIS extension
- **Location Services:** Google Maps API
- **Payments:** PayPal API
- **Email:** SMTP configuration for notifications

## Key Functionality

- **Geographic Search:** Uses PostGIS for location-based vendor discovery
- **Multi-vendor Cart:** Customers can order from multiple restaurants
- **Dynamic Tax Calculation:** Configurable tax rates applied at checkout
- **Real-time Notifications:** Email alerts for orders and vendor approvals
- **Role-based Access:** Separate dashboards for customers, vendors, and admins

## Project Structure

```
├── accounts/          # User authentication and profiles
├── vendor/           # Restaurant management
├── menu/             # Food categories and items
├── marketplace/      # Shopping cart and search
├── customers/        # Customer dashboard
├── orders/           # Order processing and payments
└── foodOnline_main/  # Main project settings
```

## Setup Requirements

- Python 3.x
- PostgreSQL with PostGIS
- Google Maps API key
- PayPal developer account
- SMTP email configuration
