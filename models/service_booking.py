import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ServiceBooking(models.Model):
    _name = "service.booking"
    _description = "Service Booking Header"
    _rec_name = "customer_name"
    ordering = "plan_service_date desc"

    name = fields.Char(
        string="Booking Number", help="Enter the booking number for the vehicle service"
    )

    customer_name = fields.Many2one(
        "res.partner",
        string="Customer Name",
        required=True,
        help="Choose customer name",
    )
    contact_number = fields.Char(string="Contact Number", required=True)
    contact_email = fields.Char(string="Email")

    plat_number = fields.Char(string="Plat Number", required=True)
    vehicle_brand = fields.Many2one(
        "service.vehicle.brand",
        string="Vehicle Brand",
        required=True,
        help="Choose vehicle brand",
    )
    vehicle_model = fields.Many2one(
        "service.vehicle.model",
        string="Vehicle Model",
        required=True,
        help="Choose vehicle brand",
    )

    vehicle_year_manufacture = fields.Integer(string="Year of Manufacture")
    kilometers = fields.Integer(string="Current Kilometers")

    complaint_issue = fields.Text(string="Complaints")

    plan_service_date = fields.Date(
        string="Booking Date", required=True, default=fields.Date.context_today
    )

    service_date = fields.Date(
        string="Service Date", required=True, default=fields.Date.context_today
    )
    service_type = fields.Many2one(
        "service.type",
        string="Service Type",
        required=True,
        help="Service type",
    )

    return_date = fields.Date(string="Return Date")

    internal_notes = fields.Text(string="Notes")

    supervisor_user_id = fields.Many2one(
        "service.supervisor.user", string="Supervisor", help="Select supervisor user"
    )

    media_document = fields.Many2many("ir.attachment", string="Attachments")

    total_amount = fields.Float(string="Total Amount")
    total_sparepart = fields.Float(string="Total Sparepart")
    total_service_fee = fields.Float(string="Total Service Fee")
    tax_id = fields.Many2one("account.tax", string="Tax")

    invoice_id = fields.Many2one("account.move", string="Invoice")

    error_msg = fields.Text(string="Error Message")

    state = fields.Selection(
        [
            ("booking", "BOOKING"),
            ("assigned", "ASSIGNED"),
            ("in_progress", "IN PROGRESS"),
            ("returned", "RETURNED"),
            ("cancelled", "CANCELLED"),
            ("completed", "COMPLETED"),
        ],
        default="booking",
        string="Status",
        tracking=1,
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

    @api.model
    def create(self, vals):
        if vals.get("name", "/") in ("/", False, None):
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("infinys.vehicle.service") or "/"
            )
        return super().create(vals)
