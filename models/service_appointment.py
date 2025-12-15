import logging
from odoo import api, fields, models, _
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

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
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        string="Status",
        tracking=1,
    )

    cancel_reason = fields.Text(string="Cancellation Reason")

    job_order_id = fields.Many2one(
        "service.booking",
        string="Job Order",
        readonly=True,
        copy=False,
    )
    job_order_count = fields.Integer(
        string="Job Order Count", compute="_compute_job_order_count"
    )

    last_reminder_date_new_appointment = fields.Date(
        string="Last Reminder Date (New Appointment)",
        help="Date when the last reminder was sent for a new appointment needing a job order."
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('service.appointment') or _('New')
        res = super(ServiceAppointment, self).create(vals)

        ICPSudo = self.env["ir.config_parameter"].sudo()
        enable_new_appointment_supervisor_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_new_appointment_supervisor_reminders", "False"
        ).lower() == "true"
        reminder_new_appointment_supervisor_activity = ICPSudo.get_param(
            "infinys_service_showroom.reminder_new_appointment_supervisor_activity", "False"
        ).lower() == "true"
        reminder_new_appointment_supervisor_email = ICPSudo.get_param(
            "infinys_service_showroom.reminder_new_appointment_supervisor_email", "False"
        ).lower() == "true"

        if enable_new_appointment_supervisor_reminders:
            supervisor_group = self.env.ref('infinys_service_showroom.group_infinys_service_supervisor', raise_if_not_found=False)
            if supervisor_group:
                supervisor_users = supervisor_group.users
                if reminder_new_appointment_supervisor_activity:
                    res._send_activity_notification(
                        supervisor_users,
                        _("New Service Appointment: %s needs Job Order") % res.name,
                        _("A new service appointment %s has been created. Please review and create a Job Order.") % res.name
                    )
                if reminder_new_appointment_supervisor_email:
                    for user in supervisor_users:
                        res._send_reminder_email(
                            'email_template_new_appointment_supervisor_reminder',
                            user
                        )
        return res

    @api.onchange('vehicle_brand')
    def _onchange_vehicle_brand(self):
        if self.vehicle_brand:
            self.vehicle_model = False
            return {'domain': {'vehicle_model': [('vehicle_brand', '=', self.vehicle_brand.id)]}}
        else:
            self.vehicle_model = False
            return {'domain': {'vehicle_model': []}}

    def _send_activity_notification(self, user_ids, summary, note):
        if not user_ids:
            return
        for record in self:
            for user_id in user_ids:
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    note=note,
                    summary=summary,
                    user_id=user_id.id,
                    date_deadline=fields.Date.today(),
                )

    def _send_reminder_email(self, template_xml_id, recipient_user, booking_record=None):
        if not recipient_user or not recipient_user.partner_id.email:
            _logger.warning(f"No recipient or email address found for email reminder using template {template_xml_id}.")
            return

        body = ""
        subject = ""
        email_from = f"<{self.env.company.email or self.env.user.email}>"

        record = booking_record or self

        if template_xml_id == 'email_template_new_appointment_supervisor_reminder':
            subject = f"New Service Appointment: {record.name} needs Job Order"
            body = f"""
                <div style=\"margin: 0px; padding: 0px;">
                    <p style=\"margin: 0px; padding: 0px; font-size: 13px;\">
                        Hello {recipient_user.name},
                        <br/><br/>
                        A new service appointment, <strong>{record.name}</strong>, has been created and requires your attention to be converted into a Job Order.
                        <br/><br/>
                        <strong>Customer:</strong> {record.customer_name.name} <br/>
                        <strong>Vehicle:</strong> {record.vehicle_brand.name} {record.vehicle_model.name} ({record.plat_number}) <br/>
                        <strong>Planned Service Date:</strong> {record.plan_service_date} <br/>
                        <strong>Complaint:</strong> {record.complaint_issue or 'N/A'}
                        <br/><br/>
                        Please review the appointment and create a Job Order.
                        <br/><br/>
                        <a href=\"/web#model=service.appointment&amp;id={record.id}&amp;view_type=form\" style=\"background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px;\">View Service Appointment</a>
                        <br/><br/>
                        Thank you,<br/>
                        The Service Team
                    </p>
                </div>
            """
        
        if subject and body:
            mail_values = {
                'email_from': email_from,
                'author_id': self.env.user.partner_id.id,
                'email_to': recipient_user.partner_id.email,
                'subject': subject,
                'body_html': body,
                'auto_delete': True,
                'state': 'outgoing',
                'res_id': record.id,
                'model': 'service.appointment',
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
            _logger.info(f"Sent email reminder for appointment {record.name} to {recipient_user.partner_id.email} using template {template_xml_id}.")


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

    @api.model
    def _check_and_send_new_appointment_reminders(self):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        enable_new_appointment_supervisor_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_new_appointment_supervisor_reminders", "False"
        ).lower() == "true"

        if not enable_new_appointment_supervisor_reminders:
            _logger.info("New Appointment Supervisor Reminders are disabled.")
            return

        reminder_interval_days_new_appointment = int(ICPSudo.get_param(
            "infinys_service_showroom.reminder_interval_days_new_appointment", default="1"
        ))
        reminder_new_appointment_supervisor_activity = ICPSudo.get_param(
            "infinys_service_showroom.reminder_new_appointment_supervisor_activity", "False"
        ).lower() == "true"
        reminder_new_appointment_supervisor_email = ICPSudo.get_param(
            "infinys_service_showroom.reminder_new_appointment_supervisor_email", "False"
        ).lower() == "true"

        today = fields.Date.today()

        overdue_new_appointments = self.search([
            ('state', '=', 'draft'),
            ('job_order_id', '=', False),
            ('create_date', '<=', today - timedelta(days=reminder_interval_days_new_appointment)),
            '|',
            ('last_reminder_date_new_appointment', '=', False),
            ('last_reminder_date_new_appointment', '<', today)
        ])

        supervisor_group = self.env.ref('infinys_service_showroom.group_infinys_service_supervisor', raise_if_not_found=False)
        if not supervisor_group:
            _logger.warning("Service Supervisor group not found. Cannot send new appointment reminders.")
            return

        supervisor_users = supervisor_group.users

        for appointment in overdue_new_appointments:
            activity_reminder_sent = False
            email_reminder_sent = False

            if reminder_new_appointment_supervisor_activity:
                appointment._send_activity_notification(
                    supervisor_users,
                    _("REMINDER: New Service Appointment %s needs Job Order") % appointment.name,
                    _("Service Appointment %s created on %s is still awaiting Job Order creation.") % (appointment.name, appointment.create_date.strftime('%Y-%m-%d'))
                )
                activity_reminder_sent = True
            
            if reminder_new_appointment_supervisor_email:
                for user in supervisor_users:
                    appointment._send_reminder_email(
                        'email_template_new_appointment_supervisor_reminder',
                        user
                    )
                email_reminder_sent = True

            if activity_reminder_sent or email_reminder_sent:
                appointment.last_reminder_date_new_appointment = today

        return True

    @api.model
    def _cancel_overdue_appointments(self):
        today = fields.Date.today()
        overdue_appointments = self.search([
            ('state', '=', 'draft'),
            ('plan_service_date', '<', today),
            ('job_order_id', '=', False)
        ])
        for appointment in overdue_appointments:
            appointment.write({
                'state': 'cancelled',
                'cancel_reason': _("Appointment automatically cancelled due to overdue booking date."),
            })
            _logger.info(f"Appointment {appointment.name} otomatis dibatalkan karena tanggal terlewat.")
        return True

