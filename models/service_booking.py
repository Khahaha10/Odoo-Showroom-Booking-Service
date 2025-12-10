import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
from odoo.addons.mail.models.mail_activity_mixin import MailActivityMixin
from odoo.addons.portal.models.portal_mixin import PortalMixin
from odoo.addons.mail.models.mail_thread import MailThread


_logger = logging.getLogger(__name__)


class ServiceBooking(models.Model, MailActivityMixin, MailThread, PortalMixin):
    _name = "service.booking"
    _description = "Service Booking"
    _rec_name = "name"
    _order = "plan_service_date desc"

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
    cancel_reason = fields.Text(string="Cancel Reason")
    error_msg = fields.Text(string="Error Message")

    supervisor_user_id = fields.Many2one(
        "service.supervisor.user", string="Supervisor", help="Select supervisor user"
    )
    assigned_technician_id = fields.Many2one(
        "res.users", string="Assigned Technician", help="Select the technician assigned to this service"
    )

    assigned_datetime = fields.Datetime(string="Assigned Time", readonly=True)
    in_progress_datetime = fields.Datetime(string="In Progress Time", readonly=True)
    completed_datetime = fields.Datetime(string="Completed Time", readonly=True)

    last_reminder_date_assigned = fields.Date(
        string="Last Reminder Date (Assigned)",
        help="Date when the last reminder was sent for 'Assigned' state."
    )
    last_reminder_date_in_progress = fields.Date(
        string="Last Reminder Date (In Progress)",
        help="Date when the last reminder was sent for 'In Progress' state."
    )

    appointment_id = fields.Many2one(
        "service.appointment",
        string="Originating Appointment",
        readonly=True,
        copy=False,
        help="The service appointment from which this booking was created."
    )

    media_document = fields.Many2many("ir.attachment", "service_booking_media_rel", "booking_id", "attachment_id", string="Attachments")
    internal_media_document = fields.Many2many("ir.attachment", "service_booking_internal_media_rel", "booking_id", "attachment_id", string="Internal Documents")

    total_sparepart = fields.Float(
        string="Total Sparepart",
        compute="_compute_totals",
        store=True,
    )
    total_service_fee = fields.Float(
        string="Total Service Fee",
        compute="_compute_totals",
        store=True,
    )
    tax_id = fields.Many2one("account.tax", string="Tax")
    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_totals",
        store=True,
    )
    invoice_id = fields.Many2one("account.move", string="Invoice")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", copy=False, readonly=True)
    stock_picking_id = fields.Many2one("stock.picking", string="Delivery Order", copy=False, readonly=True)
    
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
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', 
        related='company_id.currency_id', readonly=True
    )

    inspection_checklist_line_ids = fields.One2many(
        "service.inspection.checklist.line",
        "service_booking_id",
        string="Inspection Checklist",
    )
    spare_part_line_ids = fields.One2many(
        "service.parts.used.line",
        "service_booking_id",
        string="Spare Parts Used",
    )
    service_line_ids = fields.One2many(
        "service.used.line",
        "service_booking_id",
        string="Services Used",
    )

    sale_order_count = fields.Integer(compute='_compute_order_count', string='Sale Order Count')
    delivery_order_count = fields.Integer(compute='_compute_order_count', string='Delivery Order Count')
    invoice_count = fields.Integer(compute='_compute_order_count', string='Invoice Count')
    is_checklist_readonly = fields.Boolean(
        string="Is Checklist Readonly",
        compute="_compute_is_checklist_readonly",
        store=False,
    )

    @api.onchange('vehicle_brand')
    def _onchange_vehicle_brand(self):
        if self.vehicle_brand:
            self.vehicle_model = False
            return {'domain': {'vehicle_model': [('vehicle_brand', '=', self.vehicle_brand.id)]}}
        else:
            self.vehicle_model = False
            return {'domain': {'vehicle_model': []}}

    def _compute_order_count(self):
        for rec in self:
            rec.sale_order_count = 1 if rec.sale_order_id else 0
            rec.delivery_order_count = 1 if rec.stock_picking_id else 0
            rec.invoice_count = 1 if rec.invoice_id else 0

    @api.depends("spare_part_line_ids.subtotal", "service_line_ids.subtotal")
    def _compute_totals(self):
        for record in self:
            record.total_sparepart = sum(record.spare_part_line_ids.mapped("subtotal"))
            record.total_service_fee = sum(record.service_line_ids.mapped("subtotal")),
            record.total_amount = record.total_sparepart + record.total_service_fee

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
        
        ICPSudo = self.env["ir.config_parameter"].sudo()
        enable_service_booking_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_service_booking_reminders", "False"
        ).lower() == "true"
        reminder_new_booking_supervisor = ICPSudo.get_param(
            "infinys_service_showroom.reminder_new_booking_supervisor", "False"
        ).lower() == "true"
        enable_service_booking_email_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_service_booking_email_reminders", "False"
        ).lower() == "true"
        reminder_new_booking_supervisor_email = ICPSudo.get_param(
            "infinys_service_showroom.reminder_new_booking_supervisor_email", "False"
        ).lower() == "true"

        if enable_service_booking_reminders and reminder_new_booking_supervisor:
            supervisor_users = self.env['res.users'].search([('id', '=', res.supervisor_user_id.user_id.id)])
            if supervisor_users:
                res._send_activity_notification(
                    supervisor_users,
                    _("New Service Booking: %s needs assignment") % res.name,
                    _("Please assign technician for Service Booking %s.") % res.name
                )
        if enable_service_booking_email_reminders and reminder_new_booking_supervisor_email:
            if res.supervisor_user_id and res.supervisor_user_id.user_id:
                res._send_reminder_email(
                    'email_template_new_booking_supervisor_reminder',
                    res.supervisor_user_id.user_id
                )
        return res

    def write(self, vals):
        old_state = self.state
        
        if "plat_number" in vals and vals["plat_number"]:
            vals["plat_number"] = vals["plat_number"].upper()
        
        res = super().write(vals)
        
        self._populate_inspection_checklist()

        ICPSudo = self.env["ir.config_parameter"].sudo()
        enable_service_booking_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_service_booking_reminders", "False"
        ).lower() == "true"
        reminder_assigned_technician_initial = ICPSudo.get_param(
            "infinys_service_showroom.reminder_assigned_technician_initial", "False"
        ).lower() == "true"
        reminder_in_progress_notification = ICPSudo.get_param(
            "infinys_service_showroom.reminder_in_progress_notification", "False"
        ).lower() == "true"
        enable_service_booking_email_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_service_booking_email_reminders", "False"
        ).lower() == "true"
        reminder_assigned_technician_initial_email = ICPSudo.get_param(
            "infinys_service_showroom.reminder_assigned_technician_initial_email", "False"
        ).lower() == "true"
        reminder_in_progress_notification_email = ICPSudo.get_param(
            "infinys_service_showroom.reminder_in_progress_notification_email", "False"
        ).lower() == "true"

        for record in self:
            if enable_service_booking_reminders and record.state == 'assigned' and old_state != 'assigned':
                if reminder_assigned_technician_initial and record.assigned_technician_id:
                    record._send_activity_notification(
                        record.assigned_technician_id,
                        _("Service Booking %s Assigned") % record.name,
                        _("You have been assigned to service booking %s. Please start working on it.") % record.name
                    )
                if enable_service_booking_email_reminders and reminder_assigned_technician_initial_email:
                    if record.assigned_technician_id:
                        record._send_reminder_email(
                            'email_template_assigned_technician_overdue_reminder',
                            record.assigned_technician_id
                        )
            
            if enable_service_booking_reminders and record.state == 'in_progress' and old_state != 'in_progress':
                if reminder_in_progress_notification:
                    if self.env.user == record.assigned_technician_id:
                        if record.supervisor_user_id and record.supervisor_user_id.user_id:
                            record._send_activity_notification(
                                record.supervisor_user_id.user_id,
                                _("Service Booking %s is In Progress") % record.name,
                                _("Technician %s has started working on Service Booking %s.") % (self.env.user.name, record.name)
                            )
                    else:
                        if record.assigned_technician_id:
                            record._send_activity_notification(
                                record.assigned_technician_id.user_ids,
                                _("Service Booking %s is In Progress") % record.name,
                                _("Service Booking %s has been marked as in progress.") % record.name
                            )
                if enable_service_booking_email_reminders and reminder_in_progress_notification_email:
                    if self.env.user == record.assigned_technician_id: 
                        if record.supervisor_user_id and record.supervisor_user_id.user_id:
                            record._send_reminder_email(
                                'email_template_in_progress_supervisor_overdue_reminder',
                                record.supervisor_user_id.user_id
                            )
                    else: 
                        if record.assigned_technician_id:
                            record._send_reminder_email(
                                'email_template_in_progress_technician_overdue_reminder',
                                record.assigned_technician_id
                            )
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

    def _send_reminder_email(self, template_xml_id, recipient_user):
        if not recipient_user or not recipient_user.partner_id.email:
            _logger.warning(f"No recipient or email address found for email reminder using template {template_xml_id}.")
            return

        body = ""
        subject = ""
        email_from = f"<{self.env.company.email or self.env.user.email}>"

        for record in self:
            if template_xml_id == 'email_template_assigned_technician_overdue_reminder':
                subject = f"REMINDER: Service Booking {record.name} Overdue to Start"
                body = f"""
                    <div style=\"margin: 0px; padding: 0px;">
                        <p style=\"margin: 0px; padding: 0px; font-size: 13px;">
                            Hello {recipient_user.name},
                            <br/><br/>
                            This is a reminder that Service Booking <strong>{record.name}</strong> was assigned to you on <strong>{record.assigned_datetime.strftime('%Y-%m-%d')}</strong> and has not been started yet.
                            <br/><br/>
                            <strong>Customer:</strong> {record.customer_name.name} <br/>
                            <strong>Vehicle:</strong> {record.vehicle_brand.name} {record.vehicle_model.name} ({record.plat_number}) <br/>
                            <strong>Booking Date:</strong> {record.plan_service_date} <br/>
                            <strong>Complaint:</strong> {record.complaint_issue or 'N/A'}
                            <br/><br/>
                            Please start working on this service booking.
                            <br/><br/>
                            <a href=\"/web#model=service.booking&amp;id={record.id}&amp;view_type=form\" style=\"background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px;\">View Service Booking</a>
                            <br/><br/>
                            Thank you,<br/>
                            The Service Team
                        </p>
                    </div>
                """
            elif template_xml_id == 'email_template_new_booking_supervisor_reminder':
                subject = f"New Service Booking: {record.name} needs assignment"
                body = f"""
                    <div style=\"margin: 0px; padding: 0px;">
                        <p style=\"margin: 0px; padding: 0px; font-size: 13px;">
                            Hello {recipient_user.name},
                            <br/><br/>
                            A new service booking, <strong>{record.name}</strong>, has been created and requires your attention for technician assignment.
                            <br/><br/>
                            <strong>Customer:</strong> {record.customer_name.name} <br/>
                            <strong>Vehicle:</strong> {record.vehicle_brand.name} {record.vehicle_model.name} ({record.plat_number}) <br/>
                            <strong>Booking Date:</strong> {record.plan_service_date} <br/>
                            <strong>Complaint:</strong> {record.complaint_issue or 'N/A'}
                            <br/><br/>
                            Please assign a technician to this booking as soon as possible.
                            <br/><br/>
                            <a href=\"/web#model=service.booking&amp;id={record.id}&amp;view_type=form\" style=\"background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px;\">View Service Booking</a>
                            <br/><br/>
                            Thank you,<br/>
                            The Service Team
                        </p>
                    </div>
                """
            elif template_xml_id == 'email_template_assigned_supervisor_overdue_reminder':
                subject = f"REMINDER: Service Booking {record.name} Overdue to Start (Supervisor)"
                body = f"""
                    <div style=\"margin: 0px; padding: 0px;">
                        <p style=\"margin: 0px; padding: 0px; font-size: 13px;">
                            Hello {recipient_user.name},
                            <br/><br/>
                            This is a reminder that Service Booking <strong>{record.name}</strong>, assigned to <strong>{record.assigned_technician_id.name}</strong> on <strong>{record.assigned_datetime.strftime('%Y-%m-%d')}</strong>, is overdue to start.
                            <br/><br/>
                            <strong>Customer:</strong> {record.customer_name.name} <br/>
                            <strong>Vehicle:</strong> {record.vehicle_brand.name} {record.vehicle_model.name} ({record.plat_number}) <br/>
                            <strong>Booking Date:</strong> {record.plan_service_date} <br/>
                            <strong>Complaint:</strong> {record.complaint_issue or 'N/A'}
                            <br/><br/>
                            Please follow up with the assigned technician.
                            <br/><br/>
                            <a href=\"/web#model=service.booking&amp;id={record.id}&amp;view_type=form\" style=\"background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px;\">View Service Booking</a>
                            <br/><br/>
                            Thank you,<br/>
                            The Service Team
                        </p>
                    </div>
                """
            elif template_xml_id == 'email_template_in_progress_technician_overdue_reminder':
                subject = f"REMINDER: Service Booking {record.name} Overdue to Complete"
                body = f"""
                    <div style=\"margin: 0px; padding: 0px;">
                        <p style=\"margin: 0px; padding: 0px; font-size: 13px;">
                            Hello {recipient_user.name},
                            <br/><br/>
                            This is a reminder that Service Booking <strong>{record.name}</strong> has been in progress since <strong>{record.in_progress_datetime.strftime('%Y-%m-%d')}</strong> and is overdue to be completed.
                            <br/><br/>
                            <strong>Customer:</strong> {record.customer_name.name} <br/>
                            <strong>Vehicle:</strong> {record.vehicle_brand.name} {record.vehicle_model.name} ({record.plat_number}) <br/>
                            <strong>Booking Date:</strong> {record.plan_service_date} <br/>
                            <strong>Complaint:</strong> {record.complaint_issue or 'N/A'}
                            <br/><br/>
                            Please complete this service booking.
                            <br/><br/>
                            <a href=\"/web#model=service.booking&amp;id={record.id}&amp;view_type=form\" style=\"background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px;\">View Service Booking</a>
                            <br/><br/>
                            Thank you,<br/>
                            The Service Team
                        </p>
                    </div>
                """
            elif template_xml_id == 'email_template_in_progress_supervisor_overdue_reminder':
                subject = f"REMINDER: Service Booking {record.name} Overdue to Complete (Supervisor)"
                body = f"""
                    <div style=\"margin: 0px; padding: 0px;">
                        <p style=\"margin: 0px; padding: 0px; font-size: 13px;">
                            Hello {recipient_user.name},
                            <br/><br/>
                            This is a reminder that Service Booking <strong>{record.name}</strong>, handled by <strong>{record.assigned_technician_id.name}</strong>, has been in progress since <strong>{record.in_progress_datetime.strftime('%Y-%m-%d')}</strong> and is overdue to be completed.
                            <br/><br/>
                            <strong>Customer:</strong> {record.customer_name.name} <br/>
                            <strong>Vehicle:</strong> {record.vehicle_brand.name} {record.vehicle_model.name} ({record.plat_number}) <br/>
                            <strong>Booking Date:</strong> {record.plan_service_date} <br/>
                            <strong>Complaint:</strong> {record.complaint_issue or 'N/A'}
                            <br/><br/>
                            Please follow up with the assigned technician.
                            <br/><br/>
                            <a href=\"/web#model=service.booking&amp;id={record.id}&amp;view_type=form\" style=\"background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px;\">View Service Booking</a>
                            <br/><br/>
                            Thank you,<br/>
                            The Service Team
                        </p>
                    </div>
                """
            
            mail_values = {
                'email_from': email_from,
                'author_id': self.env.user.partner_id.id,
                'email_to': recipient_user.partner_id.email,
                'subject': subject,
                'body_html': body,
                'auto_delete': True,
                'state': 'outgoing',
                'res_id': record.id,
                'model': 'service.booking',
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
            _logger.info(f"Sent email reminder for booking {record.name} to {recipient_user.partner_id.email} using template {template_xml_id}.")

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def action_view_delivery_order(self):
        self.ensure_one()
        return {
            'name': _('Delivery Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.stock_picking_id.id,
            'target': 'current',
        }

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

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
        ICPSudo = self.env["ir.config_parameter"].sudo()
        automate_delivery_order_done = ICPSudo.get_param(
            "infinys_service_showroom.automate_delivery_order_done", default="False"
        ).lower() == "true"
        automate_invoice_creation = ICPSudo.get_param(
            "infinys_service_showroom.automate_invoice_creation", default="False"
        ).lower() == "true"

        for rec in self:
            sale_order = self.env['sale.order']
            if rec.spare_part_line_ids or rec.service_line_ids:
                sale_order = self.env['sale.order'].create({
                    'partner_id': rec.customer_name.id,
                    'origin': rec.name,
                })
                if rec.spare_part_line_ids:
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'name': 'Spare Parts',
                        'display_type': 'line_section',
                    })
                for part in rec.spare_part_line_ids:
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'product_id': part.product_id.id,
                        'product_uom_qty': part.qty,
                        'price_unit': part.unit_price,
                    })
                if rec.service_line_ids:
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'name': 'Services',
                        'display_type': 'line_section',
                    })
                for service in rec.service_line_ids:
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'product_id': service.product_id.id,
                        'product_uom_qty': service.qty,
                        'price_unit': service.unit_price,
                    })
                rec.sale_order_id = sale_order.id

                if automate_invoice_creation:
                    if sale_order:
                        sale_order.action_confirm()
                        invoices = sale_order._create_invoices()
                        if invoices:
                            rec.invoice_id = invoices[0].id

            if rec.spare_part_line_ids:
                default_warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
                picking_type = default_warehouse.out_type_id if default_warehouse else self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
                if not picking_type:
                    picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)

                if picking_type:
                    stock_picking = self.env['stock.picking'].create({
                        'partner_id': rec.customer_name.id,
                        'picking_type_id': picking_type.id,
                        'location_id': picking_type.default_location_src_id.id,
                        'location_dest_id': rec.customer_name.property_stock_customer.id,
                        'origin': rec.name,
                    })
                    for part in rec.spare_part_line_ids:
                        self.env['stock.move'].create({
                            'name': part.product_id.name,
                            'product_id': part.product_id.id,
                            'product_uom_qty': part.qty,
                            'product_uom': part.product_id.uom_id.id,
                            'picking_id': stock_picking.id,
                            'location_id': picking_type.default_location_src_id.id,
                            'location_dest_id': rec.customer_name.property_stock_customer.id,
                        })
                    stock_picking.action_confirm()
                    stock_picking.action_assign()
                    if automate_delivery_order_done:
                        stock_picking.button_validate()
                    rec.stock_picking_id = stock_picking.id

            rec.write({
                'state': 'completed',
                'completed_datetime': fields.Datetime.now(),
            })
            for activity in rec.activity_ids:
                activity.action_feedback()

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

    def get_portal_url(self, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        return self.get_base_url() + '/my/service-booking/%s' % (self.id)

    @api.model
    def _check_and_send_daily_reminders(self):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        enable_service_booking_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_service_booking_reminders", "False"
        ).lower() == "true"

        if not enable_service_booking_reminders:
            _logger.info("Service Booking Reminders are disabled.")
            return

        reminder_interval_days_assigned = int(ICPSudo.get_param(
            "infinys_service_showroom.reminder_interval_days_assigned", default="1"
        ))
        reminder_interval_days_in_progress = int(ICPSudo.get_param(
            "infinys_service_showroom.reminder_interval_days_in_progress", default="1"
        ))
        reminder_interval_days_assigned_email = int(ICPSudo.get_param(
            "infinys_service_showroom.reminder_interval_days_assigned_email", default="1"
        ))
        reminder_interval_days_in_progress_email = int(ICPSudo.get_param(
            "infinys_service_showroom.reminder_interval_days_in_progress_email", default="1"
        ))
        
        enable_service_booking_email_reminders = ICPSudo.get_param(
            "infinys_service_showroom.enable_service_booking_email_reminders", "False"
        ).lower() == "true"
        
        today = fields.Date.today()

        bookings_to_assign = self.search([
            ('state', '=', 'booking'),
            ('assigned_technician_id', '=', False),
        ])
        for booking in bookings_to_assign:
            if booking.supervisor_user_id and booking.supervisor_user_id.user_id:
                last_activity = self.env['mail.activity'].search([
                    ('res_id', '=', booking.id),
                    ('res_model_id', '=', self.env.ref('infinys_service_showroom.model_service_booking').id),
                    ('user_id', '=', booking.supervisor_user_id.user_id.id),
                    ('summary', 'ilike', 'New Service Booking%needs assignment'),
                    ('date_deadline', '=', today),
                ], limit=1)
                if not last_activity:
                    booking._send_activity_notification(
                        booking.supervisor_user_id.user_id,
                        _("REMINDER: Service Booking %s needs assignment") % booking.name,
                        _("Service Booking %s is still awaiting technician assignment. Please assign a technician.") % booking.name
                    )

        overdue_assigned_bookings = self.search([
            ('state', '=', 'assigned'),
            ('assigned_datetime', '!=', False),
            ('in_progress_datetime', '=', False),
        ])
        for booking in overdue_assigned_bookings:
            activity_reminder_sent = False
            email_reminder_sent = False

            if enable_service_booking_reminders and \
                booking.assigned_datetime.date() <= today - timedelta(days=reminder_interval_days_assigned) and \
                booking.last_reminder_date_assigned != today:
                if booking.assigned_technician_id:
                    booking._send_activity_notification(
                        booking.assigned_technician_id,
                        _("REMINDER: Service Booking %s Overdue to Start") % booking.name,
                        _("Service Booking %s was assigned on %s and has not been started yet.") % (booking.name, booking.assigned_datetime.strftime('%Y-%m-%d'))
                    )
                    activity_reminder_sent = True
                if booking.supervisor_user_id and booking.supervisor_user_id.user_id:
                    booking._send_activity_notification(
                        booking.supervisor_user_id.user_id,
                        _("REMINDER: Service Booking %s Overdue to Start (Supervisor)") % booking.name,
                        _("Service Booking %s assigned to %s on %s is overdue to start.") % (booking.name, booking.assigned_technician_id.name, booking.assigned_datetime.strftime('%Y-%m-%d'))
                    )
                    activity_reminder_sent = True
            
            if enable_service_booking_email_reminders and \
                booking.assigned_datetime.date() <= today - timedelta(days=reminder_interval_days_assigned_email) and \
                booking.last_reminder_date_assigned != today:
                if booking.assigned_technician_id:
                    booking._send_reminder_email(
                        'email_template_assigned_technician_overdue_reminder',
                        booking.assigned_technician_id
                    )
                    email_reminder_sent = True
                if booking.supervisor_user_id and booking.supervisor_user_id.user_id:
                    booking._send_reminder_email(
                        'email_template_assigned_supervisor_overdue_reminder',
                        booking.supervisor_user_id.user_id
                    )
                    email_reminder_sent = True

            if activity_reminder_sent or email_reminder_sent:
                booking.last_reminder_date_assigned = today

        overdue_in_progress_bookings = self.search([
            ('state', '=', 'in_progress'),
            ('in_progress_datetime', '!=', False),
            ('completed_datetime', '=', False),
        ])
        for booking in overdue_in_progress_bookings:
            activity_reminder_sent = False
            email_reminder_sent = False

            if enable_service_booking_reminders and \
                booking.in_progress_datetime.date() <= today - timedelta(days=reminder_interval_days_in_progress) and \
                booking.last_reminder_date_in_progress != today:
                if booking.assigned_technician_id:
                    booking._send_activity_notification(
                        booking.assigned_technician_id,
                        _("REMINDER: Service Booking %s Overdue to Complete") % booking.name,
                        _("Service Booking %s has been in progress since %s and is overdue to be completed.") % (booking.name, booking.in_progress_datetime.strftime('%Y-%m-%d'))
                    )
                    activity_reminder_sent = True
                if booking.supervisor_user_id and booking.supervisor_user_id.user_id:
                    booking._send_activity_notification(
                        booking.supervisor_user_id.user_id,
                        _("REMINDER: Service Booking %s Overdue to Complete (Supervisor)") % booking.name,
                        _("Service Booking %s handled by %s has been in progress since %s and is overdue to be completed.") % (booking.name, booking.assigned_technician_id.name, booking.in_progress_datetime.strftime('%Y-%m-%d'))
                    )
                    activity_reminder_sent = True
            
            if enable_service_booking_email_reminders and \
                booking.in_progress_datetime.date() <= today - timedelta(days=reminder_interval_days_in_progress_email) and \
                booking.last_reminder_date_in_progress != today:
                if booking.assigned_technician_id:
                    booking._send_reminder_email(
                        'email_template_in_progress_technician_overdue_reminder',
                        booking.assigned_technician_id
                    )
                    email_reminder_sent = True
                if booking.supervisor_user_id and booking.supervisor_user_id.user_id:
                    booking._send_reminder_email(
                        'email_template_in_progress_supervisor_overdue_reminder',
                        booking.supervisor_user_id.user_id
                    )
                    email_reminder_sent = True

            if activity_reminder_sent or email_reminder_sent:
                booking.last_reminder_date_in_progress = today

        return True