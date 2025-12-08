from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        service_booking_count = request.env["service.booking"].sudo().search_count([
            ("customer_name", "=", partner.id)
        ])
        values["service_booking_count"] = service_booking_count
        return values


class MyServiceBookings(http.Controller):

    _items_per_page = 10

    @http.route(
        ["/my/service-bookings", "/my/service-bookings/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_service_bookings(self, page=1, date_begin=None, date_end=None, search=None, search_in='content', **kw):
        response = request.render("infinys_service_showroom.my_service_bookings_list_template")
        values = self._prepare_portal_my_service_bookings_values(page, date_begin, date_end, search, search_in, **kw)
        return request.render("infinys_service_showroom.my_service_bookings_list_template", values)

    def _prepare_portal_my_service_bookings_values(self, page, date_begin, date_end, search=None, search_in='content', **kw):
        partner = request.env.user.partner_id
        ServiceBooking = request.env["service.booking"]

        domain = [
            ("customer_name", "=", partner.id),
        ]

        order = ServiceBooking._order

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search in Content')},
            'booking_number': {'input': 'booking_number', 'label': _('Search in Booking Number')},
            'plate_number': {'input': 'plate_number', 'label': _('Search in Plate Number')},
        }
        if not search_in:
            search_in = 'content'

        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([
                    search_domain,
                    [('name', 'ilike', search)],
                    [('plat_number', 'ilike', search)],
                    [('complaint_issue', 'ilike', search)],
                ])
            if search_in == 'booking_number':
                search_domain = OR([
                    search_domain,
                    [('name', 'ilike', search)],
                ])
            if search_in == 'plate_number':
                search_domain = OR([
                    search_domain,
                    [('plat_number', 'ilike', search)],
                ])
            domain += search_domain

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        service_booking_count = ServiceBooking.search_count(domain)
        pager = portal_pager(
            url="/my/service-bookings",
            total=service_booking_count,
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'search_in': search_in, 'search': search},
        )

        service_bookings = ServiceBooking.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )

        request.session['my_service_booking_history'] = service_bookings.ids[:100]

        values = {
            "date": date_begin,
            "service_bookings": service_bookings,
            "page_name": "service_booking",
            "pager": pager,
            "default_url": "/my/service-bookings",
            "searchbar_inputs": searchbar_inputs,
        }

    @http.route(
        ["/my/service-booking/<int:booking_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_service_booking_detail(self, booking_id, access_token=None, **kw):
        try:
            booking_sudo = self._document_check_access('service.booking', booking_id, access_token)
        except http.exceptions.AccessError:
            return request.redirect("/my")

        values = self._get_service_booking_detail_values(booking_sudo, access_token, **kw)
        return request.render("infinys_service_showroom.my_service_bookings_detail_template", values)
    
    def _get_service_booking_detail_values(self, booking_sudo, access_token, **kw):
        values = {
            'booking': booking_sudo,
            'page_name': 'service_booking_detail',
        }
        history = request.session.get('my_service_booking_history', [])
        values.update(get_records_pager(history, booking_sudo))
        return values

