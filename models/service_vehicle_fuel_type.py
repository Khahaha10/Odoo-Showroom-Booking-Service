import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class VehicleFuelType(models.Model):
    _name = "service.vehicle.fuel.type"
    _description = "Vehicle Fuel Type"
    ordering = "name asc"

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Vehicle Fuel Type name must be unique!")
    ]
