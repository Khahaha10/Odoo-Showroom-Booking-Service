from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ServiceBookingAssignTechnicianWizard(models.TransientModel):
    _name = 'service.booking.assign.technician.wizard'
    _description = 'Assign Technician Wizard'

    booking_id = fields.Many2one(
        'service.booking',
        string='Service Booking',
        required=True,
        ondelete='cascade',
    )
    technician_id = fields.Many2one(
        'res.users',
        string='Technician',
        required=True,
        domain=[('share', '=', False)], # Only internal users
        help="Select the technician for this service booking."
    )

    def assign_technician_action(self):
        self.ensure_one()
        if not self.technician_id:
            raise UserError(_("Please select a technician."))

        self.booking_id.write({
            'assigned_technician_id': self.technician_id.id,
            'assigned_datetime': fields.Datetime.now(),
            'state': 'assigned',
        })
        return {'type': 'ir.actions.act_window_close'}


class ServiceBookingCancelWizard(models.TransientModel):
    _name = 'service.booking.cancel.wizard'
    _description = 'Cancel Service Booking Wizard'

    booking_id = fields.Many2one(
        'service.booking',
        string='Service Booking',
        required=True,
        ondelete='cascade',
    )
    cancel_reason = fields.Text(
        string='Cancel Reason',
        required=True,
        help="Enter the reason for cancelling this service booking."
    )

    def cancel_booking_action(self):
        self.ensure_one()
        if not self.cancel_reason:
            raise UserError(_("Please provide a cancel reason."))

        self.booking_id.write({
            'cancel_reason': self.cancel_reason,
            'state': 'cancelled',
        })
        return {'type': 'ir.actions.act_window_close'}
