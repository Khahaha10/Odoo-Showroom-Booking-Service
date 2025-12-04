{
    "name": "Infinys Vehicle Service & Showroom",
    "summary": "Manage vehicle showroom sales and service bookings.",
    "description": """
        A comprehensive module to manage both a car showroom and vehicle service center.
        - Website Showroom: Display vehicles for sale, manage listings, and capture sales leads.
        - Service Booking: Allow customers to book vehicle maintenance and repair appointments.
        - Unified Vehicle Data: Centralized management of vehicle brands, models, types, etc.
        - Configurable Features: Enable or disable showroom and service booking features individually.
    """,
    "author": "Infinys System Indonesia",
    "website": "https://infinyscloud.com",
    "category": "Sales/Vehicle",
    "version": "1.1",
    "license": "AGPL-3",
    "depends": ["base", "website", "crm", "account", "sale_management", "stock", "mail"],
    "data": [
        "security/infinys_vehicle_service_groups.xml",
        "security/ir.model.access.csv",
        "data/service_booking_reminders_cron.xml",
        "data/service_booking_sequence.xml",
        "views/service_customer_vehicle_views.xml",
        "views/res_partner_views.xml",
        "views/showroom_res_config_settings_views.xml",
        "views/showroom_car_vehicle_views.xml",
        "views/showroom_crm_lead_views.xml",
        "views/service_vehicle_brand_views.xml",
        "views/service_vehicle_fuel_type_views.xml",
        "views/service_vehicle_type_views.xml",
        "views/service_vehicle_model_views.xml",
        "views/service_booking_views.xml",
        "views/service_booking_wizard_views.xml",
        "views/showroom_website_car_templates.xml",
        "views/service_booking_templates.xml",
        "views/service_inspection_type_views.xml",
        "views/service_product_template_views.xml",
        "views/service_type_views.xml",
        "views/service_supervisor_user_views.xml",
        "views/service_showroom_dashboard_views.xml",
        "views/service_vehicle_menu_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "infinys_service_showroom/static/src/css/car_showroom.css",
            "infinys_service_showroom/static/src/css/service_dashboard.css",
        ],
    },
    "images": ["static/description/banner.png"],
    "icon": "/infinys_service_showroom/static/description/assets/icon.png",
}
