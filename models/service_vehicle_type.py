import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class VehicleType(models.Model):
    _name = "service.vehicle.type"
    _description = "Vehicle Type"

    name = fields.Char(string="Vehicle Type Name", required=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ("name_unique", "unique(name)", "Vehicle Type Name must be unique.")
    ]
