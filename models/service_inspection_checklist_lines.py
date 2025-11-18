import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class InspectionChecklistLines(models.Model):
    _name = "service.inspection.checklist.line"
    _description = "Inspection Checklist Line"

    service_booking_id = fields.Many2one(
        "service.booking",
        string="Service Booking",
        required=True,
        ondelete="cascade",
    )
    inspection_type_id = fields.Many2one(
        "service.inspection.type",
        string="Inspection Type",
        required=True,
        ondelete="cascade",
    )
    checklist_ok = fields.Boolean(string="Checklist", default=False)

    _sql_constraints = [
        (
            "service_inspection_unique",
            "unique(service_booking_id, inspection_type_id)",
            "Each inspection type can only appear once per service booking.",
        )
    ]
