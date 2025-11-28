from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_infinys_showroom = fields.Boolean(
        string="Manage Showroom",
    )
    module_infinys_booking_service = fields.Boolean(
        string="Manage Service Bookings",
    )

    automate_delivery_order_done = fields.Boolean(
        string="Automate Delivery Order to Done",
        help="If checked, delivery orders created from service bookings will be automatically marked as 'done'."
    )
    automate_invoice_creation = fields.Boolean(
        string="Automate Invoice Creation", 
        help="If checked, sales orders created from service bookings will be automatically confirmed and a draft invoice will be created."
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
