import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CustomerVehicle(models.Model):
    _name = "service.customer.vehicle"
    _description = "Customer Vehicle"
    _rec_name = "name"
    ordering = "id desc, name asc"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        help="Select the customer who owns the vehicle",
    )

    vehicle_brand_id = fields.Many2one(
        "service.vehicle.brand",
        string="Vehicle Brand",
        required=True,
        help="Select the brand of the vehicle",
    )

    vehicle_model_id = fields.Many2one(
        "service.vehicle.model",
        string="Vehicle Model",
        required=True,
        help="Select the model of the vehicle",
    )

    vehicle_plate_no = fields.Char(
        string="Vehicle Plate No",
        required=True,
        help="Enter the plate number of the vehicle",
    )

    vehicle_year = fields.Integer(
        string="Vehicle Year", required=True, help="Enter the year of the vehicle"
    )

    @api.depends("vehicle_plate_no", "vehicle_model_id.name")
    def _compute_name(self):
        for record in self:
            name = record.vehicle_plate_no
            if record.vehicle_model_id:
                name = f"{record.vehicle_plate_no} - {record.vehicle_model_id.name}"
            record.name = name
