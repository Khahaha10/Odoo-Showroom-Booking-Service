import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class InspectionImageLines(models.Model):
    _name = "service.inspection.image.line"
    _description = "Inspection Image"

    service_booking_id = fields.Many2one(
        "service.booking",
        string="Service Booking",
        required=True,
        ondelete="cascade",
    )
    image = fields.Many2one(
        "ir.attachment", string="Image", required=True, ondelete="cascade"
    )
    description = fields.Char(string="Description")
