from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleType(models.Model):
    _name = "infinys.vehicle.type"
    _description = "Vehicle Type"

    name = fields.Char(string="Vehicle Type Name", required=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ("name_unique", "unique(name)", "Vehicle Type Name must be unique.")
    ]
