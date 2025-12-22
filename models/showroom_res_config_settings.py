from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_infinys_showroom = fields.Boolean(
        string="Manage Showroom",
    )
    module_infinys_booking_service = fields.Boolean(
        string="Manage Service Bookings",
    )
    show_advanced_settings = fields.Boolean(
        string="Show Advanced Settings",
        help="Enable to display advanced configuration options."
    )

    automate_delivery_order_done = fields.Boolean(
        string="Automate Delivery Order to Done",
        help="If checked, delivery orders created from service bookings will be automatically marked as 'done'."
    )
    automate_invoice_creation = fields.Boolean(
        string="Automate Invoice Creation", 
        help="If checked, sales orders created from service bookings will be automatically confirmed and a draft invoice will be created."
    )

    whatsapp_phone_number = fields.Char(
        string="WhatsApp Phone Number",
        help="Enter the WhatsApp number for showroom inquiries (e.g., 628123456789).",
        default="628xxxxxxxxxx",
    )
    whatsapp_prefill_message = fields.Text(
        string="WhatsApp Prefill Message",
        help="Default message to prefill when opening WhatsApp chat from car details. Use {car_name} placeholder.",
        default="Halo, saya tertarik dengan mobil {car_name}. Bisakah saya mendapatkan informasi lebih lanjut?",
    )
    
    enable_service_booking_reminders = fields.Boolean(
        string="Enable Service Booking Reminders",
        help="Globally enable or disable reminders for service bookings.",
    )
    reminder_interval_days_assigned = fields.Integer(
        string="Reminder for Assigned (Days)",
        default=1,
        help="Number of days after 'Assigned' status without 'In Progress' to send a reminder.",
    )
    reminder_interval_days_in_progress = fields.Integer(
        string="Reminder for In Progress (Days)",
        default=1,
        help="Number of days after 'In Progress' status without 'Completed' to send a reminder.",
    )
    reminder_new_booking_supervisor = fields.Boolean(
        string="New Booking Reminder to Supervisor",
        help="Send a reminder to the supervisor for new service bookings.",
    )
    reminder_assigned_technician_initial = fields.Boolean(
        string="Initial Reminder to Technician (Assigned)",
        help="Send an immediate reminder to the technician when a booking is assigned.",
    )
    reminder_in_progress_notification = fields.Boolean(
        string="In Progress Status Change Notification",
        help="Notify the other party (supervisor/technician) when a booking status changes to 'In Progress'.",
    )

    enable_service_booking_email_reminders = fields.Boolean(
        string="Enable Email Reminders for Service Bookings",
        help="Globally enable or disable email reminders for service bookings."
    )
    reminder_new_booking_supervisor_email = fields.Boolean(
        string="New Booking Email to Supervisor",
        help="Send an email to the supervisor for new service bookings."
    )
    reminder_assigned_technician_initial_email = fields.Boolean(
        string="Initial Email to Technician (Assigned)",
        help="Send an immediate email to the technician when a booking is assigned."
    )
    reminder_in_progress_notification_email = fields.Boolean(
        string="In Progress Status Change Email",
        help="Send an email notification to the other party (supervisor/technician) when a booking status changes to 'In Progress'."
    )
    reminder_interval_days_assigned_email = fields.Integer(
        string="Email Reminder for Assigned (Days)",
        default=1,
        help="Number of days after 'Assigned' status without 'In Progress' to send an email reminder."
    )
    reminder_interval_days_in_progress_email = fields.Integer(
        string="Email Reminder for In Progress (Days)",
        default=1,
        help="Number of days after 'In Progress' status without 'Completed' to send an email reminder."
    )

    enable_new_appointment_supervisor_reminders = fields.Boolean(
        string="Enable New Appointment Supervisor Reminders",
        help="Globally enable or disable reminders for new service appointments that need job orders.",
    )
    reminder_new_appointment_supervisor_activity = fields.Boolean(
        string="New Appointment Activity to Supervisor",
        help="Send an activity reminder to the supervisor for new service appointments.",
    )
    reminder_new_appointment_supervisor_email = fields.Boolean(
        string="New Appointment Email to Supervisor",
        help="Send an email reminder to the supervisor for new service appointments.",
    )
    reminder_interval_days_new_appointment = fields.Integer(
        string="Daily Reminder for New Appointments (Days)",
        default=1,
        help="Number of days after a new appointment without a job order to send a daily reminder.",
    )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        res.update(
            module_infinys_showroom=self.env.user.has_group(
                "infinys_service_showroom.group_infinys_showroom"
            ),
            module_infinys_booking_service=self.env.user.has_group(
                "infinys_service_showroom.group_infinys_booking_service"
            ),
            automate_delivery_order_done=ICPSudo.get_param(
                "infinys_service_showroom.automate_delivery_order_done", default="False"
            ).lower() == "true",
            automate_invoice_creation=ICPSudo.get_param(
                "infinys_service_showroom.automate_invoice_creation", default="False"
            ).lower() == "true",
            show_advanced_settings=ICPSudo.get_param(
                "infinys_service_showroom.show_advanced_settings", default="False"
            ).lower() == "true",
            whatsapp_phone_number=ICPSudo.get_param(
                "infinys_service_showroom.whatsapp_phone_number", default="628xxxxxxxxxx"
            ),
            whatsapp_prefill_message=ICPSudo.get_param(
                "infinys_service_showroom.whatsapp_prefill_message", default="Halo, saya tertarik dengan mobil {car_name}. Bisakah saya mendapatkan informasi lebih lanjut?"
            ),
            enable_service_booking_reminders=ICPSudo.get_param(
                "infinys_service_showroom.enable_service_booking_reminders", default="False"
            ).lower() == "true",
            reminder_interval_days_assigned=int(ICPSudo.get_param(
                "infinys_service_showroom.reminder_interval_days_assigned", default="1"
            )),
            reminder_interval_days_in_progress=int(ICPSudo.get_param(
                "infinys_service_showroom.reminder_interval_days_in_progress", default="1"
            )),
            reminder_new_booking_supervisor=ICPSudo.get_param(
                "infinys_service_showroom.reminder_new_booking_supervisor", default="False"
            ).lower() == "true",
            reminder_assigned_technician_initial=ICPSudo.get_param(
                "infinys_service_showroom.reminder_assigned_technician_initial", default="False"
            ).lower() == "true",
            reminder_in_progress_notification=ICPSudo.get_param(
                "infinys_service_showroom.reminder_in_progress_notification", default="False"
            ).lower() == "true",
            enable_service_booking_email_reminders=ICPSudo.get_param(
                "infinys_service_showroom.enable_service_booking_email_reminders", default="False"
            ).lower() == "true",
            reminder_new_booking_supervisor_email=ICPSudo.get_param(
                "infinys_service_showroom.reminder_new_booking_supervisor_email", default="False"
            ).lower() == "true",
            reminder_assigned_technician_initial_email=ICPSudo.get_param(
                "infinys_service_showroom.reminder_assigned_technician_initial_email", default="False"
            ).lower() == "true",
            reminder_in_progress_notification_email=ICPSudo.get_param(
                "infinys_service_showroom.reminder_in_progress_notification_email", default="False"
            ).lower() == "true",
            reminder_interval_days_assigned_email=int(ICPSudo.get_param(
                "infinys_service_showroom.reminder_interval_days_assigned_email", default="1"
            )),
            reminder_interval_days_in_progress_email=int(ICPSudo.get_param(
                "infinys_service_showroom.reminder_interval_days_in_progress_email", default="1"
            )),
            enable_new_appointment_supervisor_reminders=ICPSudo.get_param(
                "infinys_service_showroom.enable_new_appointment_supervisor_reminders", default="False"
            ).lower() == "true",
            reminder_new_appointment_supervisor_activity=ICPSudo.get_param(
                "infinys_service_showroom.reminder_new_appointment_supervisor_activity", default="False"
            ).lower() == "true",
            reminder_new_appointment_supervisor_email=ICPSudo.get_param(
                "infinys_service_showroom.reminder_new_appointment_supervisor_email", default="False"
            ).lower() == "true",
            reminder_interval_days_new_appointment=int(ICPSudo.get_param(
                "infinys_service_showroom.reminder_interval_days_new_appointment", default="1"
            )),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        ICPSudo.set_param(
            "infinys_service_showroom.automate_delivery_order_done",
            str(self.automate_delivery_order_done)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.automate_invoice_creation",
            str(self.automate_invoice_creation)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.show_advanced_settings",
            str(self.show_advanced_settings)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.whatsapp_phone_number", self.whatsapp_phone_number
        )
        ICPSudo.set_param(
            "infinys_service_showroom.whatsapp_prefill_message", self.whatsapp_prefill_message
        )
        ICPSudo.set_param(
            "infinys_service_showroom.enable_service_booking_reminders",
            str(self.enable_service_booking_reminders)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_interval_days_assigned",
            str(self.reminder_interval_days_assigned)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_interval_days_in_progress",
            str(self.reminder_interval_days_in_progress)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_new_booking_supervisor",
            str(self.reminder_new_booking_supervisor)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_assigned_technician_initial",
            str(self.reminder_assigned_technician_initial)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_in_progress_notification",
            str(self.reminder_in_progress_notification)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.enable_service_booking_email_reminders",
            str(self.enable_service_booking_email_reminders)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_new_booking_supervisor_email",
            str(self.reminder_new_booking_supervisor_email)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_assigned_technician_initial_email",
            str(self.reminder_assigned_technician_initial_email)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_in_progress_notification_email",
            str(self.reminder_in_progress_notification_email)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_interval_days_assigned_email",
            str(self.reminder_interval_days_assigned_email)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_interval_days_in_progress_email",
            str(self.reminder_interval_days_in_progress_email)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.enable_new_appointment_supervisor_reminders",
            str(self.enable_new_appointment_supervisor_reminders)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_new_appointment_supervisor_activity",
            str(self.reminder_new_appointment_supervisor_activity)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_new_appointment_supervisor_email",
            str(self.reminder_new_appointment_supervisor_email)
        )
        ICPSudo.set_param(
            "infinys_service_showroom.reminder_interval_days_new_appointment",
            str(self.reminder_interval_days_new_appointment)
        )
        group_showroom = self.env.ref("infinys_service_showroom.group_infinys_showroom")
        group_booking_service = self.env.ref(
            "infinys_service_showroom.group_infinys_booking_service"
        )

        current_user = self.env.user

        if self.module_infinys_showroom:
            if group_showroom not in current_user.groups_id:
                current_user.write({"groups_id": [(4, group_showroom.id)]})
        else:
            if group_showroom in current_user.groups_id:
                current_user.write({"groups_id": [(3, group_showroom.id)]})

        if self.module_infinys_booking_service:
            if group_booking_service not in current_user.groups_id:
                current_user.write({"groups_id": [(4, group_booking_service.id)]})
        else:
            if group_booking_service in current_user.groups_id:
                current_user.write({"groups_id": [(3, group_booking_service.id)]})
