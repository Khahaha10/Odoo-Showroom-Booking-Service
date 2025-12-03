import logging
from odoo import models, fields, api
from datetime import date

_logger = logging.getLogger(__name__)

class ServiceShowroomDashboard(models.TransientModel):
    _name = "service.showroom.dashboard"
    _description = "Service and Showroom Dashboard"

    today_service_bookings_count = fields.Integer(
        string="Today's Service Bookings",
        compute="_compute_counts"
    )

    today_service_bookings_in_progress_count = fields.Integer(
        string="Service In Progress",
        compute="_compute_counts"
    )
    today_service_bookings_completed_count = fields.Integer(
        string="Service Completed",
        compute="_compute_counts"
    )
    today_service_bookings_booking_count = fields.Integer(
        string="Service Booked",
        compute="_compute_counts"
    )
    today_service_bookings_assigned_count = fields.Integer(
        string="Service Assigned",
        compute="_compute_counts"
    )
    today_service_bookings_cancelled_count = fields.Integer(
        string="Service Cancelled",
        compute="_compute_counts"
    )
    today_showroom_visits_count = fields.Integer(
        string="Today's Showroom Visits",
        compute="_compute_counts"
    )

    @api.depends()
    def _compute_counts(self):
        today = date.today()
        _logger.info("Computing dashboard counts for date: %s", today)
        for record in self:
            service_bookings = self.env['service.booking'].search([
                ('plan_service_date', '=', today)
            ])
            _logger.info("Found %d service bookings for today.", len(service_bookings))
            record.today_service_bookings_count = len(service_bookings)
            record.today_service_bookings_booking_count = len(service_bookings.filtered(lambda b: b.state == 'booking'))
            record.today_service_bookings_assigned_count = len(service_bookings.filtered(lambda b: b.state == 'assigned'))
            record.today_service_bookings_in_progress_count = len(service_bookings.filtered(lambda b: b.state == 'in_progress'))
            record.today_service_bookings_completed_count = len(service_bookings.filtered(lambda b: b.state == 'completed'))
            record.today_service_bookings_cancelled_count = len(service_bookings.filtered(lambda b: b.state == 'cancelled'))

            showroom_leads = self.env['crm.lead'].search([
                ('visit_date', '=', today)
            ])
            _logger.info("Found %d showroom leads for today.", len(showroom_leads))
            record.today_showroom_visits_count = len(showroom_leads)

    def get_today_service_bookings_action(self):
        today = date.today()
        return {
            'name': "Today's Service Bookings",
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'list,form',
            'domain': [('plan_service_date', '=', today)],
            'target': 'current',
        }

    def get_service_bookings_booking_action(self):
        today = date.today()
        return {
            'name': "Service Bookings Booked",
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'list,form',
            'domain': [('plan_service_date', '=', today), ('state', '=', 'booking')],
            'target': 'current',
        }

    def get_service_bookings_assigned_action(self):
        today = date.today()
        return {
            'name': "Service Bookings Assigned",
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'list,form',
            'domain': [('plan_service_date', '=', today), ('state', '=', 'assigned')],
            'target': 'current',
        }

    def get_service_bookings_cancelled_action(self):
        today = date.today()
        return {
            'name': "Service Bookings Cancelled",
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'list,form',
            'domain': [('plan_service_date', '=', today), ('state', '=', 'cancelled')],
            'target': 'current',
        }
    
    def get_service_bookings_in_progress_action(self):
        today = date.today()
        return {
            'name': "Service Bookings In Progress",
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'list,form',
            'domain': [('plan_service_date', '=', today), ('state', '=', 'in_progress')],
            'target': 'current',
        }
    
    def get_service_bookings_completed_action(self):
        today = date.today()
        return {
            'name': "Service Bookings Completed",
            'type': 'ir.actions.act_window',
            'res_model': 'service.booking',
            'view_mode': 'list,form',
            'domain': [('plan_service_date', '=', today), ('state', '=', 'completed')],
            'target': 'current',
        }

    def get_today_showroom_visits_action(self):
        today = date.today()
        return {
            'name': "Today's Showroom Visits",
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'list,form',
            'domain': [('visit_date', '=', today)],
            'target': 'current',
        }
