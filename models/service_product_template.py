import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    vehicle_part_ok = fields.Boolean(
        string="Is Vehicle Part",
        default=False,
        help="Indicates if the product is a vehicle part.",
    )
