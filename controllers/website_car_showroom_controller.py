# infinys_service_showroom/controllers/main.py
from odoo import http
from odoo.http import request


class WebsiteCarShowroom(http.Controller):

    @http.route(["/cars"], type="http", auth="public", website=True)
    def cars_list(self, **kwargs):
        Car = request.env["showroom.car.vehicle"].sudo()
        domain = [("website_published", "=", True), ("active", "=", True)]

        brand_id = kwargs.get("brand_id")
        if brand_id:
            domain.append(("brand_id", "=", int(brand_id)))

        min_price = kwargs.get("min_price")
        if min_price:
            domain.append(("price", ">=", float(min_price)))

        max_price = kwargs.get("max_price")
        if max_price:
            domain.append(("price", "<=", float(max_price)))

        cars = Car.search(domain, order="name")

        brands = request.env["service.vehicle.brand"].sudo().search([])

        render_values = {
            "cars": cars,
            "brands": brands,
            "selected_brand_id": int(brand_id) if brand_id else None,
            "min_price": min_price,
            "max_price": max_price,
        }

        return request.render(
            "infinys_service_showroom.car_showroom_list", render_values
        )

    @http.route(
        ['/cars/<model("showroom.car.vehicle"):car>'],
        type="http",
        auth="public",
        website=True,
    )
    def car_detail(self, car, **kwargs):
        if not (car.website_published and car.active):
            return request.not_found()

        return request.render(
            "infinys_service_showroom.car_showroom_detail", {"car": car}
        )

    @http.route(["/visit-schedule"], type="http", auth="public", website=True)
    def visit_schedule(self, vehicle_id=None, **kwargs):
        Car = request.env["showroom.car.vehicle"].sudo()
        vehicle = None
        if vehicle_id:
            try:
                vehicle = Car.browse(int(vehicle_id))
                if not vehicle.exists():
                    vehicle = None
            except Exception:
                vehicle = None

        Lead = request.env["crm.lead"]
        visit_purpose_selection = Lead._fields["visit_purpose"].selection

        values = {
            "vehicle": vehicle,
            "visit_purpose_selection": visit_purpose_selection,
        }
        return request.render("infinys_service_showroom.car_visit_form", values)

    @http.route(
        ["/visit-schedule/submit"], type="http", auth="public", website=True, csrf=False
    )
    def visit_schedule_submit(self, **post):
        name = post.get("name")
        phone = post.get("phone")
        email = post.get("email")
        visit_date = post.get("visit_date")
        visit_time = post.get("visit_time")
        visit_purpose = post.get("visit_purpose")
        description = post.get("description")
        vehicle_id = post.get("vehicle_id")

        vehicle = None
        if vehicle_id:
            try:
                vehicle = (
                    request.env["showroom.car.vehicle"].sudo().browse(int(vehicle_id))
                )
                if not vehicle.exists():
                    vehicle = None
            except Exception:
                vehicle = None

        # Find or create res.partner
        partner = (
            request.env["res.partner"]
            .sudo()
            .search(
                [
                    ("name", "=", name),
                    "|",
                    ("email", "=", email),
                    ("phone", "=", phone),
                ],
                limit=1,
            )
        )
        if not partner:
            partner = (
                request.env["res.partner"]
                .sudo()
                .create(
                    {
                        "name": name,
                        "phone": phone,
                        "email": email,
                    }
                )
            )
        else:
            # Update partner's phone and email if they are different
            partner.sudo().write(
                {
                    "phone": phone,
                    "email": email,
                }
            )

        lead_vals = {
            "type": "lead",
            "contact_name": name,
            "phone": phone,
            "email_from": email,
            "description": description,
            "visit_date": visit_date or False,
            "visit_time": visit_time or False,
            "visit_purpose": visit_purpose or False,
            "partner_id": partner.id,  # Link to the created/found partner
        }

        if vehicle:
            lead_vals["vehicle_id"] = vehicle.id
            lead_vals["name"] = "Showroom visit - %s" % (vehicle.name,)
        else:
            lead_vals["name"] = "Showroom visit"

        request.env["crm.lead"].sudo().create(lead_vals)

        return request.render("infinys_service_showroom.car_visit_thanks", {})
