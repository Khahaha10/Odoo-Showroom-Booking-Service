import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class VehicleModel(models.Model):
    _name = "service.vehicle.model"
    _description = "Vehicle Model"

    name = fields.Char(string="Model Name", required=True)
    vehicle_brand = fields.Many2one(
        "service.vehicle.brand",
        string="Vehicle Brand",
        required=True,
        help="Choose vehicle brand",
    )

    vehicle_fuel_type = fields.Many2one(
        "service.vehicle.fuel.type", string="Fuel Type", required=True
    )

    vehicle_type = fields.Many2many(
        "service.vehicle.type", string="Vehicle Type", required=True
    )

    image = fields.Binary(string="Model Image")

    _sql_constraints = [
        ("name_unique", "unique(name)", "Vehicle Model Name must be unique.")
    ]
