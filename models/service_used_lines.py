from odoo import api, fields, models


class ServiceUsedLine(models.Model):
    _name = "service.used.line"
    _description = "Service Used Line"

    service_booking_id = fields.Many2one("service.booking", string="Service Booking")
    product_id = fields.Many2one("product.product", string="Service", domain="[('type', '=', 'service')]")
    qty = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Unit Price", compute="_compute_product_info", store=False)

    product_name_display = fields.Char(
        string="Service Name", compute="_compute_product_info", store=False
    )

    @api.depends('product_id')
    def _compute_product_info(self):
        for rec in self:
            if rec.product_id:
                product_sudo = rec.product_id.sudo()
                rec.unit_price = product_sudo.list_price
                rec.product_name_display = product_sudo.display_name
            else:
                rec.unit_price = 0.0
                rec.product_name_display = False
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends("qty", "unit_price")
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.qty * record.unit_price
