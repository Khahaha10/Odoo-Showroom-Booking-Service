# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_infinys_showroom = fields.Boolean(
        string="Manage Showroom",
    )
    module_infinys_booking_service = fields.Boolean(
        string="Manage Service Bookings",
    )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            module_infinys_showroom=self.env.user.has_group(
                "infinys_service_showroom.group_infinys_showroom"
            ),
            module_infinys_booking_service=self.env.user.has_group(
                "infinys_service_showroom.group_infinys_booking_service"
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
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
