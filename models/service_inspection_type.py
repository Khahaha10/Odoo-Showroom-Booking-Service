import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class InspectionType(models.Model):
    _name = "service.inspection.type"
    _description = "Inspection Type"

    name = fields.Char(string="Inspection Type Name", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("name_unique", "unique(name)", "Inspection Type name must be unique.")
    ]
