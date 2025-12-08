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
    qty = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(
        string="Unit Price", compute="_compute_product_info", store=False
    )
    on_hand_qty = fields.Float(
        string="On Hand", compute="_compute_product_info", store=False
    )

    @api.depends('product_id')
    def _compute_product_info(self):
        for rec in self:
            if rec.product_id:
                product_sudo = rec.product_id.sudo()
                rec.unit_price = product_sudo.list_price
                rec.on_hand_qty = product_sudo.qty_available
            else:
                rec.unit_price = 0.0
                rec.on_hand_qty = 0.0

    product_name_display = fields.Char(
        string="Part Name", compute="_compute_product_name_display", store=False
    )

    @api.depends('product_id')
    def _compute_product_name_display(self):
        for rec in self:
            rec.product_name_display = rec.product_id.sudo().display_name if rec.product_id else False

    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

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
