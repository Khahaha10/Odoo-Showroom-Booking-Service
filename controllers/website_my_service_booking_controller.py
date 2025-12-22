from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
    get_records_pager,
)
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        service_booking_count = (
            request.env["service.booking"]
            .sudo()
            .search_count([("customer_name", "=", partner.id)])
        )
        service_appointment_count = (
            request.env["service.appointment"]
            .sudo()
            .search_count([("customer_name", "=", partner.id), ("state", "=", "draft")])
        )
        values["service_booking_count"] = (
            service_booking_count + service_appointment_count
        )
        return values


class MyServiceBookings(CustomerPortal):
    _items_per_page = 10

    @http.route(
        ["/my/service-bookings", "/my/service-bookings/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_service_bookings(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        search=None,
        search_in="content",
        **kw,
    ):
        response = request.render(
            "infinys_service_showroom.my_service_bookings_list_template"
        )
        values = self._prepare_portal_my_service_bookings_values(
            page, date_begin, date_end, search, search_in, **kw
        )
        return request.render(
            "infinys_service_showroom.my_service_bookings_list_template", values
        )

    def _prepare_portal_my_service_bookings_values(
        self, page, date_begin, date_end, search=None, search_in="content", **kw
    ):
        partner = request.env.user.partner_id
        ServiceBooking = request.env["service.booking"]

        domain = [
            ("customer_name", "=", partner.id),
        ]

        order = ServiceBooking._order

        searchbar_inputs = {
            "content": {"input": "content", "label": _("Search in Content")},
            "booking_number": {
                "input": "booking_number",
                "label": _("Search in Booking Number"),
            },
            "plate_number": {
                "input": "plate_number",
                "label": _("Search in Plate Number"),
            },
        }
        if not search_in:
            search_in = "content"

        if search and search_in:
            search_domain = []
            if search_in == "content":
                search_domain = OR(
                    [
                        search_domain,
                        [("name", "ilike", search)],
                        [("plat_number", "ilike", search)],
                        [("complaint_issue", "ilike", search)],
                    ]
                )
            if search_in == "booking_number":
                search_domain = OR(
                    [
                        search_domain,
                        [("name", "ilike", search)],
                    ]
                )
            if search_in == "plate_number":
                search_domain = OR(
                    [
                        search_domain,
                        [("plat_number", "ilike", search)],
                    ]
                )
            domain += search_domain

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        ServiceAppointment = request.env["service.appointment"]

        booking_domain = list(domain)
        service_bookings = ServiceBooking.search(booking_domain)

        appointment_domain = list(domain)
        appointment_domain.append(("state", "in", ["draft", "cancelled"]))
        if search and search_in:
            if search_in == "content":
                appointment_search_domain = OR(
                    [
                        [("name", "ilike", search)],
                        [("plat_number", "ilike", search)],
                        [("complaint_issue", "ilike", search)],
                    ]
                )
                appointment_domain += appointment_search_domain
            elif search_in == "booking_number":
                appointment_search_domain = [("name", "ilike", search)]
                appointment_domain += appointment_search_domain
            elif search_in == "plate_number":
                appointment_search_domain = [("plat_number", "ilike", search)]
                appointment_domain += appointment_search_domain

        service_appointments = ServiceAppointment.search(appointment_domain)

        combined_records = []
        for booking in service_bookings:
            booking_data = type(
                "MockBooking",
                (object,),
                {
                    "id": booking.id,
                    "name": booking.name,
                    "customer_name": booking.customer_name,
                    "contact_number": booking.contact_number,
                    "contact_email": booking.contact_email,
                    "plat_number": booking.plat_number,
                    "vehicle_brand": booking.vehicle_brand,
                    "vehicle_model": booking.vehicle_model,
                    "plan_service_date": booking.plan_service_date,
                    "service_type": booking.service_type,
                    "complaint_issue": booking.complaint_issue,
                    "state": booking.state,
                    "record_type": "booking",
                    "get_portal_url": booking.get_portal_url,
                },
            )()
            combined_records.append(booking_data)
        for appointment in service_appointments:
            mock_booking = type(
                "MockBooking",
                (object,),
                {
                    "id": appointment.id,
                    "name": appointment.name,
                    "customer_name": appointment.customer_name,
                    "contact_number": appointment.contact_number,
                    "contact_email": appointment.contact_email,
                    "plat_number": appointment.plat_number,
                    "vehicle_brand": appointment.vehicle_brand,
                    "vehicle_model": appointment.vehicle_model,
                    "plan_service_date": appointment.plan_service_date,
                    "service_type": appointment.service_type,
                    "complaint_issue": appointment.complaint_issue,
                    "state": "waiting"
                    if appointment.state == "draft"
                    else appointment.state,
                    "record_type": "appointment",
                    "get_portal_url": lambda: "#",
                },
            )()
            combined_records.append(mock_booking)

        combined_records.sort(
            key=lambda r: (r.plan_service_date or fields.Date.today(), r.name or "")
        )

        total_records = len(combined_records)
        pager = portal_pager(
            url="/my/service-bookings",
            total=total_records,
            page=page,
            step=self._items_per_page,
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "search_in": search_in,
                "search": search,
            },
        )
        offset = pager["offset"]
        limit = self._items_per_page
        paginated_records = combined_records[offset : offset + limit]

        values = {
            "date": date_begin,
            "service_bookings": paginated_records,
            "page_name": "service_booking",
            "pager": pager,
            "default_url": "/my/service-bookings",
            "searchbar_inputs": searchbar_inputs,
        }
        return values

    @http.route(
        ["/my/service-booking/<int:booking_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_service_booking_detail(self, booking_id, access_token=None, **kw):
        try:
            booking_sudo = self._document_check_access(
                "service.booking", booking_id, access_token
            )
        except odoo.exceptions.AccessError:
            return request.redirect("/my")

        values = self._get_service_booking_detail_values(
            booking_sudo, access_token, **kw
        )
        return request.render(
            "infinys_service_showroom.my_service_bookings_detail_template", values
        )

    def _get_service_booking_detail_values(self, booking_sudo, access_token, **kw):
        values = {
            "booking": booking_sudo,
            "page_name": "service_booking_detail",
            "default_url": "/my/service-bookings",
        }
        history = request.session.get("my_service_booking_history", [])
        values.update(get_records_pager(history, booking_sudo))
        return values
