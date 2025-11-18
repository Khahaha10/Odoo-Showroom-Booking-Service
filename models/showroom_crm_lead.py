# infinys_car_showroom/models/crm_lead.py
from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    vehicle_id = fields.Many2one(
        "showroom.car.vehicle",
        string="Vehicle",
    )
    visit_date = fields.Date("Visit Date")
    visit_time = fields.Char("Visit Time")
    visit_purpose = fields.Selection(
        [
            ("test_drive", "Test Drive"),
            ("inspection", "Car Inspection"),
            ("negotiation", "Price Negotiation"),
            ("service", "Service Appointment"),
            ("other", "Other"),
        ],
        string="Visit Purpose",
    )
