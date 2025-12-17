from odoo import http
from odoo.http import request
import base64


class WebsiteServiceBooking(http.Controller):

    @http.route(["/service-booking/new"], type="http", auth="public", website=True)
    def service_booking_form(self, **kwargs):
        brands = request.env["service.vehicle.brand"].sudo().search([])
        models = request.env["service.vehicle.model"].sudo().search([])
        service_types = request.env["service.type"].sudo().search([])
        
        user = request.env.user
        customer_vehicles = []
        customer_name = ""
        customer_email = ""
        customer_phone = ""

        if user.sudo().partner_id != request.env.ref('base.public_partner'):
            customer = user.sudo().partner_id
            customer_name = customer.name
            customer_email = customer.email
            customer_phone = customer.phone
            customer_vehicles = request.env["service.customer.vehicle"].sudo().search([('customer_id', '=', customer.id)])

        return request.render(
            "infinys_service_showroom.service_booking_form_template",
            {
                "brands": brands, 
                "models": models, 
                "service_types": service_types,
                "customer_vehicles": customer_vehicles,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
            },
        )

    @http.route(
        ["/service_booking/submit"], type="http", auth="public", website=True, csrf=True
    )
    def service_booking_submit(self, **post):
        partner = (
            request.env["res.partner"]
            .sudo()
            .search([("name", "=", post.get("customer_name"))], limit=1)
        )
        if not partner:
            partner = (
                request.env["res.partner"]
                .sudo()
                .create(
                    {
                        "name": post.get("customer_name"),
                        "phone": post.get("contact_number"),
                        "email": post.get("contact_email"),
                    }
                )
            )
        else:
            partner.sudo().write(
                {
                    "phone": post.get("contact_number"),
                    "email": post.get("contact_email"),
                }
            )

        appointment_vals = {
            "customer_name": partner.id,
            "contact_number": post.get("contact_number"),
            "contact_email": post.get("contact_email"),
            "plat_number": post.get("plat_number"),
            "vehicle_brand": int(post.get("vehicle_brand")),
            "vehicle_model": int(post.get("vehicle_model")),
            "vehicle_year_manufacture": int(post.get("vehicle_year_manufacture")) if post.get("vehicle_year_manufacture") else False,
            "kilometers": int(post.get("kilometers")) if post.get("kilometers") else False,
            "plan_service_date": post.get("plan_service_date"),
            "service_type": int(post.get("service_type")),
            "complaint_issue": post.get("complaint_issue"),
        }

        appointment = request.env["service.appointment"].sudo().create(appointment_vals)

        if 'media_document' in request.params:
            attachment_ids = []
            for c_file in request.httprequest.files.getlist('media_document'):
                attachment_vals = {
                    "name": c_file.filename,
                    "datas": base64.b64encode(c_file.read()).decode("utf-8"),
                    "res_model": "service.appointment",
                    "res_id": appointment.id,
                }
                new_attachment = request.env["ir.attachment"].sudo().create(attachment_vals)
                attachment_ids.append(new_attachment.id)

            if attachment_ids:
                appointment.sudo().write({'media_document': [(6, 0, attachment_ids)]})

        return request.render(
            "infinys_service_showroom.service_booking_success_template",
            {"appointment": appointment}
        )
