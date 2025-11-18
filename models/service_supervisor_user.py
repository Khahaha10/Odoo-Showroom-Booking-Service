import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SupervisorUser(models.Model):
    _name = "service.supervisor.user"

    name = fields.Char(string="Name", compute="_compute_user_title_name", store=False)
    user_id = fields.Many2one("res.users", string="User", required=True)
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("user_id_uniq", "unique (user_id)", "Supervisor User must be unique")
    ]

    user_email = fields.Char(
        string="Email",
        related="user_id.partner_id.email",
        store=False,
    )

    user_phone = fields.Char(
        string="Phone",
        related="user_id.partner_id.phone",
        store=False,
    )

    user_mobile = fields.Char(
        string="Mobile",
        related="user_id.partner_id.mobile",
        store=False,
    )

    user_title = fields.Char(
        string="Title",
        compute="_compute_user_title_name",
        store=False,
    )

    @api.depends("user_id")
    def _compute_user_title_name(self):
        for record in self:
            record.user_title = (
                record.user_id.partner_id.title.name
                if record.user_id.partner_id.title
                else ""
            )
            record.name = (
                record.user_id.partner_id.name if record.user_id.partner_id.name else ""
            )
