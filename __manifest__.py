# -*- coding: utf-8 -*-
{
    "name": "Infinys Vehicle Showroom & Service",
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
    "depends": ["base", "website", "crm", "account", "sale_management", "stock"],
    "data": [
        "security/infinys_vehicle_service_groups.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/car_vehicle_views.xml",
        "views/crm_lead_views.xml",
        "views/vehicle_brand_views.xml",
        "views/vehicle_fuel_type_views.xml",
        "views/vehicle_type_views.xml",
        "views/vehicle_model_views.xml",
        "views/service_booking_views.xml",
        "views/website_car_templates.xml",
        "views/service_booking_templates.xml",
        "views/vehicle_menu_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "infinys_service_showroom/static/src/css/car_showroom.css",
        ],
    },
    "images": ["static/description/banner.png"],
}
