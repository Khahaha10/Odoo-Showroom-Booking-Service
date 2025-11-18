import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PartUsedLines(models.Model):
    _name = "service.parts.used.line"
    _description = "Parts Used Line"

    service_booking_id = fields.Many2one(
        "service.booking",
        string="Service Booking",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one("product.product", string="Part", required=True)
    qty = fields.Float(string="Qty", default=1.0)
    unit_price = fields.Float(
        string="Unit Price", related="product_id.list_price", readonly=1
    )
    on_hand_qty = fields.Float(
        string="On Hand", related="product_id.qty_available", readonly=1
    )

    subtotal = fields.Float(string="Price", compute="_compute_subtotal", store=True)

    @api.depends("qty", "unit_price")
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.qty * record.unit_price

    _sql_constraints = [
        (
            "service_booking_id",
            "unique (service_booking_id,product_id)",
            "Part must be unique!",
        )
    ]
