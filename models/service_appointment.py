from odoo import api, fields, models, _

class ServiceAppointment(models.Model):
    _name = "service.appointment"
    _description = "Service Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = "name"
    _order = "create_date desc"

    name = fields.Char(
        string="Appointment Number", 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('New')
    )

    customer_name = fields.Many2one(
        "res.partner",
        string="Customer Name",
        required=True,
        help="Choose customer name",
    )
    contact_number = fields.Char(string="Contact Number", required=True)
    contact_email = fields.Char(string="Email")

    plat_number = fields.Char(string="Plate Number", required=True)
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
        help="Choose vehicle model",
        domain="[('vehicle_brand', '=', vehicle_brand)]"
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
        string="Planned Service Date", required=True, default=fields.Date.context_today
    )
    service_type = fields.Many2one(
        "service.type",
        string="Service Type",
        required=True,
        help="Service type",
    )
    
    media_document = fields.Many2many("ir.attachment", "appointment_media_rel", "appointment_id", "attachment_id", string="Attachments")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
        ],
        default="draft",
        string="Status",
        tracking=1,
    )

    job_order_id = fields.Many2one(
        "service.booking",
        string="Job Order",
        readonly=True,
        copy=False,
    )
    job_order_count = fields.Integer(
        string="Job Order Count", compute="_compute_job_order_count"
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('service.appointment') or _('New')
        res = super(ServiceAppointment, self).create(vals)
        return res

    @api.onchange('vehicle_brand')
    def _onchange_vehicle_brand(self):
        if self.vehicle_brand:
            self.vehicle_model = False
            return {'domain': {'vehicle_model': [('vehicle_brand', '=', self.vehicle_brand.id)]}}
        else:
            self.vehicle_model = False
            return {'domain': {'vehicle_model': []}}

    def _compute_job_order_count(self):
        for rec in self:
            rec.job_order_count = 1 if rec.job_order_id else 0

    def action_view_job_order(self):
        self.ensure_one()
        return {
            'name': _('Job Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'form',
            'res_id': self.job_order_id.id,
            'target': 'current',
        }

    def action_create_job_order(self):
        self.ensure_one()
        if self.job_order_id:
            raise ValidationError(_("A Job Order already exists for this appointment."))

        job_order_vals = {
            'customer_name': self.customer_name.id,
            'contact_number': self.contact_number,
            'contact_email': self.contact_email,
            'plat_number': self.plat_number,
            'vehicle_brand': self.vehicle_brand.id,
            'vehicle_model': self.vehicle_model.id,
            'vehicle_type': self.vehicle_type.id,
            'vehicle_year_manufacture': self.vehicle_year_manufacture,
            'kilometers': self.kilometers,
            'complaint_issue': self.complaint_issue,
            'plan_service_date': self.plan_service_date,
            'service_type': self.service_type.id,
            'media_document': [(6, 0, self.media_document.ids)],
            'appointment_id': self.id,
        }

        new_job_order = self.env['service.booking'].create(job_order_vals)
        self.write({
            'state': 'done',
            'job_order_id': new_job_order.id,
        })

        return {
            'name': _('Job Order Created'),
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'form',
            'res_id': new_job_order.id,
            'target': 'current',
        }
