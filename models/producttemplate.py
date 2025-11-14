from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_vehicle_part = fields.Boolean(string="Is Vehicle Part", default=False)
