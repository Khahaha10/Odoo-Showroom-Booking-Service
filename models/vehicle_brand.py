from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleBrand(models.Model):
    _name = "infinys.vehicle.brand"
    _description = "Vehicle Brand"

    name = fields.Char(string="Brand Name", required=True)
    images = fields.Binary(string="Brand Images")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Vehicle Brand name must be unique!")
    ]
