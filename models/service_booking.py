import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

_logger = logging.getLogger(__name__)


class ServiceBooking(models.Model):
    _name = "service.booking"
    _description = "Service Booking Header"
    _rec_name = "name"
    ordering = "plan_service_date desc"

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
        help="Choose vehicle brand",
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

    supervisor_user_id = fields.Many2one(
        "service.supervisor.user", string="Supervisor", help="Select supervisor user"
    )

    assigned_technician_id = fields.Many2one(
        "res.users", string="Assigned Technician", help="Select the technician assigned to this service"
    )
    assigned_datetime = fields.Datetime(string="Assigned Time", readonly=True)
    in_progress_datetime = fields.Datetime(string="In Progress Time", readonly=True)
    completed_datetime = fields.Datetime(string="Completed Time", readonly=True)
    cancel_reason = fields.Text(string="Cancel Reason")

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
    sale_order_count = fields.Integer(compute='_compute_order_count', string='Sale Order Count')
    delivery_order_count = fields.Integer(compute='_compute_order_count', string='Delivery Order Count')
    invoice_count = fields.Integer(compute='_compute_order_count', string='Invoice Count')
         
    def _compute_order_count(self):
        for rec in self:
            rec.sale_order_count = 1 if rec.sale_order_id else 0
            rec.delivery_order_count = 1 if rec.stock_picking_id else 0
            rec.invoice_count = 1 if rec.invoice_id else 0
    def action_view_sale_order(self):
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def action_view_delivery_order(self):
        return {
            'name': _('Delivery Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.stock_picking_id.id,
            'target': 'current',
        }

    def action_view_invoice(self):
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    @api.depends("spare_part_line_ids.subtotal", "service_line_ids.subtotal")
    def _compute_totals(self):
        for record in self:
            record.total_sparepart = sum(record.spare_part_line_ids.mapped("subtotal"))
            record.total_service_fee = sum(record.service_line_ids.mapped("subtotal"))
            record.total_amount = record.total_sparepart + record.total_service_fee

    error_msg = fields.Text(string="Error Message")

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

    is_checklist_readonly = fields.Boolean(
        string="Is Checklist Readonly",
        compute="_compute_is_checklist_readonly",
        store=False,
    )

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

    def write(self, vals):
        if "plat_number" in vals and vals["plat_number"]:
            vals["plat_number"] = vals["plat_number"].upper()
        res = super().write(vals)
        self._populate_inspection_checklist()
        return res

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
