# infinys_car_showroom/controllers/main.py
from odoo import http
from odoo.http import request


class WebsiteServiceBooking(http.Controller):

    @http.route(["/service-booking/new"], type="http", auth="public", website=True)
    def service_booking_form(self, **kwargs):
        brands = request.env["infinys.vehicle.brand"].sudo().search([])
        models = request.env["infinys.vehicle.model"].sudo().search([])
        return request.render(
            "infinys_service_showroom.service_booking_form_template",
            {"brands": brands, "models": models},
        )

    @http.route(
        ["/service_booking/submit"], type="http", auth="public", website=True, csrf=True
    )
    def service_booking_submit(self, **post):
        partner = (
            request.env["res.partner"]
            .sudo()
            .search([("name", "=", post.get("name"))], limit=1)
        )
        if not partner:
            partner = request.env["res.partner"].sudo().create(
                {
                    "name": post.get("name"),
                    "phone": post.get("phone"),
                    "email": post.get("email"),
                }
            )
        else:
            partner.sudo().write(
                {
                    "phone": post.get("phone"),
                    "email": post.get("email"),
                }
            )

        booking = (
            request.env["infinys.service.booking"]
            .sudo()
            .create(
                {
                    "partner_id": partner.id,
                    "plat_number": post.get("plat_number"),
                    "vehicle_brand": int(post.get("vehicle_brand_id")),
                    "vehicle_model": int(post.get("vehicle_model_id")),
                    "plan_service_date": post.get("plan_service_date"),
                    "service_type": post.get("service_type"),
                    "notes": post.get("notes"),
                    "total_amount": 0,  # Assuming 0 for now
                }
            )
        )
        return request.render(
            "infinys_service_showroom.service_booking_success_template"
        )