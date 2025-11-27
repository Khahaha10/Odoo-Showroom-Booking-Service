from odoo import api, fields, models


class ServiceUsedLine(models.Model):
    _name = "service.used.line"
    _description = "Service Used Line"

    service_booking_id = fields.Many2one("service.booking", string="Service Booking")
    product_id = fields.Many2one("product.product", string="Service", domain="[('type', '=', 'service')]")
    qty = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Unit Price", related="product_id.list_price", readonly=True)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends("qty", "unit_price")
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.qty * record.unit_price
