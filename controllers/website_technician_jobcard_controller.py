from odoo import http, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
    get_records_pager,
)
from odoo.osv.expression import OR


class TechnicianJobCards(CustomerPortal):
    _items_per_page = 10

    @http.route(
        ["/my/technician-jobcards", "/my/technician-jobcards/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_technician_jobcards(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        search=None,
        search_in="content",
        **kw,
    ):
        if not request.env.user.has_group("base.group_user"):
            return request.redirect("/my")
        values = self._prepare_portal_my_technician_jobcards_values(
            page, date_begin, date_end, search, search_in, **kw
        )
        return request.render(
            "infinys_service_showroom.my_job_card_list_template", values
        )

    def _prepare_portal_my_technician_jobcards_values(
        self, page, date_begin, date_end, search=None, search_in="content", **kw
    ):
        partner = request.env.user.partner_id
        ServiceBooking = request.env["service.booking"]

        domain = [
            ("assigned_technician_id", "=", request.env.user.id),
        ]

        order = ServiceBooking._order

        searchbar_inputs = {
            "content": {"input": "content", "label": _("Search in Content")},
            "booking_number": {
                "input": "booking_number",
                "label": _("Search in Job Card Number"),
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

        service_bookings = ServiceBooking.with_context(from_technician_portal=True).search(domain, order=order)

        total_records = len(service_bookings)
        pager = portal_pager(
            url="/my/technician-jobcards",
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
        paginated_records = service_bookings[offset : offset + limit]

        values = {
            "date": date_begin,
            "job_cards": paginated_records,
            "page_name": "my_job_card",
            "pager": pager,
            "default_url": "/my/technician-jobcards",
            "searchbar_inputs": searchbar_inputs,
        }
        return values

    @http.route(
        ["/my/technician-jobcard/<int:booking_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_technician_jobcard_detail(self, booking_id, access_token=None, **kw):
        if not request.env.user.has_group("base.group_user"):
            return request.redirect("/my")

        try:
            job_card_sudo = request.env["service.booking"].sudo().with_context(from_technician_portal=True).browse(booking_id)
            if (
                not job_card_sudo.exists()
                or job_card_sudo.assigned_technician_id.id != request.env.user.id
            ):
                raise http.exceptions.AccessError(_("Access Denied!"))
        except http.exceptions.AccessError:
            return request.redirect("/my")

        values = self._get_technician_jobcard_detail_values(
            job_card_sudo, access_token, **kw
        )
        return request.render(
            "infinys_service_showroom.my_job_card_detail_template", values
        )

    def _get_technician_jobcard_detail_values(self, job_card_sudo, access_token, **kw):
        values = {
            "job_card": job_card_sudo,
            "page_name": "my_job_card_detail",
        }
        history = request.session.get("my_technician_job_card_history", [])
        values.update(get_records_pager(history, job_card_sudo))
        return values
