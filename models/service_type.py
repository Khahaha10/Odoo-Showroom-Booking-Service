import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ServiceType(models.Model):
    _name = "service.type"
    _description = "Service Type"

    name = fields.Char(string="Service Type Name", required=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Service Type name must be unique!")
    ]
