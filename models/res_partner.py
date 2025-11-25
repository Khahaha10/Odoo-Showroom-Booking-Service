from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    vehicle_ids = fields.One2many(
        "service.customer.vehicle",
        "customer_id",
        string="Vehicles",
        help="The vehicles owned by this customer",
    )
