import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

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
    vehicle_type = fields.Many2one(
        'service.vehicle.type',
        string='Vehicle Type',
        required=False
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

    assigned_technician_id = fields.Many2one(
        "res.users", string="Assigned Technician", help="Select the technician assigned to this service"
    )
    assigned_datetime = fields.Datetime(string="Assigned Time", readonly=True)
    in_progress_datetime = fields.Datetime(string="In Progress Time", readonly=True)
    completed_datetime = fields.Datetime(string="Completed Time", readonly=True)
    cancel_reason = fields.Text(string="Cancel Reason")

    media_document = fields.Many2many("ir.attachment", string="Attachments")

    total_amount = fields.Float(string="Total Amount")
    total_sparepart = fields.Float(string="Total Sparepart")
    total_service_fee = fields.Float(string="Total Service Fee")
    tax_id = fields.Many2one("account.tax", string="Tax")

    invoice_id = fields.Many2one("account.move", string="Invoice")

    error_msg = fields.Text(string="Error Message")

    state = fields.Selection(
        [
            ("booking", "Booking"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="booking",
        string="Status",
        tracking=1,
    )

    state_idx = fields.Integer(
        string="State Index", compute="_compute_state_idx", store=True, index=True
    )

    inspection_checklist_line_ids = fields.One2many(
        "service.inspection.checklist.line",
        "service_booking_id",
        string="Inspection Checklist",
    )

    is_checklist_readonly = fields.Boolean(
        string="Is Checklist Readonly",
        compute="_compute_is_checklist_readonly",
        store=False,
    )

    @api.depends("state")
    def _compute_is_checklist_readonly(self):
        for record in self:
            record.is_checklist_readonly = record.state in ('completed', 'cancelled')

    @api.constrains("plan_service_date")
    def _plan_service_date(self):
        for record in self:
            if record.state != "booking":
                return
            if record.plan_service_date < date.today():
                raise ValidationError(_("Service date cannot be in the past."))

    @api.model
    def create(self, vals):
        if "plat_number" in vals and vals["plat_number"]:
            vals["plat_number"] = vals["plat_number"].upper()
        if vals.get("name", "/") in ("/", False, None):
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("infinys.vehicle.service") or "/"
            )
        res = super().create(vals)
        if res.customer_name and res.plat_number:
            vehicle = self.env["service.customer.vehicle"].search(
                [
                    ("customer_id", "=", res.customer_name.id),
                    ("vehicle_plate_no", "=", res.plat_number),
                ]
            )
            if not vehicle:
                self.env["service.customer.vehicle"].create(
                    {
                        "customer_id": res.customer_name.id,
                        "vehicle_plate_no": res.plat_number,
                        "vehicle_brand_id": res.vehicle_brand.id,
                        "vehicle_model_id": res.vehicle_model.id,
                        "vehicle_year": res.vehicle_year_manufacture,
                    }
                )
        res._populate_inspection_checklist()
        return res

    def _populate_inspection_checklist(self):
        for record in self:
            if not record.inspection_checklist_line_ids:
                inspection_types = self.env["service.inspection.type"].search([("active", "=", True)])
                for insp_type in inspection_types:
                    record.env["service.inspection.checklist.line"].create({
                        "service_booking_id": record.id,
                        "inspection_type_id": insp_type.id,
                        "checklist_ok": False,
                    })

    def write(self, vals):
        if "plat_number" in vals and vals["plat_number"]:
            vals["plat_number"] = vals["plat_number"].upper()
        res = super().write(vals)
        self._populate_inspection_checklist()
        return res

    def action_assign(self):
        self.ensure_one()
        return {
            'name': _('Assign Technician'),
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking.assign.technician.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_booking_id': self.id},
        }

    def action_start(self):
        for rec in self:
            rec.write({
                'state': 'in_progress',
                'in_progress_datetime': fields.Datetime.now(),
            })

    def action_complete(self):
        for rec in self:
            rec.write({
                'state': 'completed',
                'completed_datetime': fields.Datetime.now(),
            })

    def action_cancel(self):
        for rec in self:
            return {
                'name': _('Cancel Service Booking'),
                'type': 'ir.actions.act_window',
                'res_model': 'service.booking.cancel.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_booking_id': self.id},
            }

    @api.depends("state", "state_idx")
    def _compute_state_idx(self):
        self.state_idx = 1
        for record in self:
            idx = 1
            match record.state:
                case "booking":
                    idx = 1
                case "assigned":
                    idx = 2
                case "in_progress":
                    idx = 3
                case "completed":
                    idx = 4
                case "cancelled":
                    idx = 5
            record.state_idx = idx
