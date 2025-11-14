from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ServiceBooking(models.Model):
    _name = "infinys.service.booking"
    _description = "Service Booking"
    _rec_name = "partner_id"
    ordering = "plan_service_date desc"

    name = fields.Char(
        string="Booking Number", help="Enter the booking number for the vehicle service"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
        required=True,
        help="Choose customer name",
    )
    phone = fields.Char(
        string="Contact Number",
        required=True,
        related="partner_id.phone",
        readonly=False,
    )
    email = fields.Char(string="Email", related="partner_id.email", readonly=False)
    vehicle_brand = fields.Many2one(
        "infinys.vehicle.brand",
        string="Vehicle Brand",
        required=True,
        help="Choose vehicle brand",
    )
    vehicle_model = fields.Many2one(
        "infinys.vehicle.model",
        string="Vehicle Model",
        required=True,
        help="Choose vehicle brand",
    )

    plan_service_date = fields.Date(
        string="Plan Service Date", required=True, default=fields.Date.context_today
    )
    service_date = fields.Date(
        string="Service Date", required=True, default=fields.Date.context_today
    )
    plat_number = fields.Char(string="Plat Number", required=True)

    service_type = fields.Selection(
        [
            ("maintenance", "Maintenance"),
            ("repair", "Repair"),
            ("inspection", "Inspection"),
        ],
        string="Service Type",
        required=True,
    )

    notes = fields.Text(string="Additional Notes")

    total_amount = fields.Float(string="Total Amount", required=True)

    sales_id = fields.Many2one("sale.order", string="Sales Order")

    error_msg = fields.Text(string="Error Message")
    state = fields.Selection(
        [
            ("booking", "Booking"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="booking",
        required=True,
    )

    @api.constrains("plan_service_date")
    def _plan_service_date(self):
        for record in self:
            if record.state != "booking":
                return
            if record.plan_service_date < date.today():
                raise ValidationError(_("Service date cannot be in the past."))

    @api.constrains("plat_number")
    def _plat_number(self):
        for record in self:
            if record.plat_number:
                record.plat_number = record.plat_number.upper()
