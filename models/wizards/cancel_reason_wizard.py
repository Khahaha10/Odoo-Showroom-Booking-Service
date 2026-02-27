from odoo import api, fields, models, _


class CancelReasonWizard(models.TransientModel):
    _name = "cancel.reason.wizard"
    _description = "Cancellation Reason Wizard"

    cancel_reason = fields.Text(string="Cancellation Reason", required=True)

    appointment_id = fields.Many2one("service.appointment", string="Appointment")
    booking_id = fields.Many2one("service.booking", string="Job Order")

    def action_confirm_cancel(self):
        self.ensure_one()
        if self.appointment_id:
            self.appointment_id.write(
                {
                    "state": "cancelled",
                    "cancel_reason": self.cancel_reason,
                }
            )
            if self.appointment_id.job_order_id:
                self.appointment_id.job_order_id.write(
                    {
                        "state": "cancelled",
                        "cancel_reason": self.cancel_reason,
                    }
                )
        elif self.booking_id:
            self.booking_id.write(
                {
                    "state": "cancelled",
                    "cancel_reason": self.cancel_reason,
                }
            )
            if self.booking_id.appointment_id:
                self.booking_id.appointment_id.write(
                    {
                        "state": "cancelled",
                        "cancel_reason": self.cancel_reason,
                    }
                )
        return {"type": "ir.actions.act_window_close"}
