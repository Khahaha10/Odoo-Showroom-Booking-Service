import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CustomerVehicle(models.Model):
    _name = "service.customer.vehicle"
    _description = "Customer Vehicle"
    ordering = "id desc, name asc"

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        help="Select the customer who owns the vehicle",
    )

    vehicle_brand_id = fields.Many2one(
        "service.vehicle.brand",
        string="Vehicle Brand",
        required=True,
        help="Select the brand of the vehicle",
    )

    vehicle_model_id = fields.Many2one(
        "service.vehicle.model",
        string="Vehicle Model",
        required=True,
        help="Select the model of the vehicle",
    )

    vehicle_type_id = fields.Many2one(
        "service.vehicle.type",
        string="Vehicle Type",
        required=True,
        help="Select the type of the vehicle",
    )

    vehicle_plate_no = fields.Char(
        string="Vehicle Plate No",
        required=True,
        help="Enter the plate number of the vehicle",
    )

    vehicle_color = fields.Char(
        string="Vehicle Color", required=True, help="Enter the color of the vehicle"
    )

    vehicle_year = fields.Integer(
        string="Vehicle Year", required=True, help="Enter the year of the vehicle"
    )

    vehicle_mileage = fields.Integer(
        string="Vehicle Mileage", required=True, help="Enter the mileage of the vehicle"
    )

    vehicle_fuel_type = fields.Many2one(
        "service.vehicle.fuel.type",
        string="Vehicle Fuel Type",
        help="Select the fuel type of the vehicle",
    )
