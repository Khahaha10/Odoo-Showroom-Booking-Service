from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleModel(models.Model):
    _name = "infinys.vehicle.model"
    _description = "Vehicle Model"

    name = fields.Char(string="Model Name", required=True)
    vehicle_brand = fields.Many2one(
        "infinys.vehicle.brand",
        string="Vehicle Brand",
        required=True,
        help="Choose vehicle brand",
    )

    vehicle_fuel_type = fields.Many2one(
        "infinys.vehicle.fuel.type", string="Fuel Type", required=True
    )

    vehicle_type = fields.Many2many(
        "infinys.vehicle.type", string="Vehicle Type", required=True
    )

    image = fields.Binary(string="Model Image")

    _sql_constraints = [
        ("name_unique", "unique(name)", "Vehicle Model Name must be unique.")
    ]
