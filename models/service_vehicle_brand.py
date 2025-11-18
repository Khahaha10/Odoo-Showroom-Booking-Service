import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class VehicleBrand(models.Model):
    _name = "service.vehicle.brand"
    _description = "Vehicle Brand"

    name = fields.Char(string="Brand Name", required=True)
    images = fields.Binary(string="Brand Images")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Vehicle Brand name must be unique!")
    ]
