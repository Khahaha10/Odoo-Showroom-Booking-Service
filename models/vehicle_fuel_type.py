from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleFuelType(models.Model):
    _name = "infinys.vehicle.fuel.type"
    _description = "Vehicle Fuel Type"
    ordering = "name asc"

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Vehicle Fuel Type name must be unique!")
    ]
