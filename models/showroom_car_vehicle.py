from odoo import models, fields, api


class CarVehicle(models.Model):
    _name = "showroom.car.vehicle"
    _description = "Showroom Vehicle"
    _order = "name"

    name = fields.Char("Car Name", required=True)
    active = fields.Boolean(default=True)
    website_published = fields.Boolean("Published on Website", default=False)

    brand_id = fields.Many2one(
        "service.vehicle.brand",
        string="Brand",
        required=True,
    )
    model_id = fields.Many2one(
        "service.vehicle.model",
        string="Model",
        required=True,
    )

    @api.onchange("model_id")
    def _onchange_model_id(self):
        if self.model_id:
            self.brand_id = self.model_id.vehicle_brand.id
            self.fuel_type_id = self.model_id.vehicle_fuel_type.id
            vehicle_type_ids = self.model_id.vehicle_type.ids
            if self.model_id.vehicle_type:
                self.type_id = self.model_id.vehicle_type[0].id
            else:
                self.type_id = False
            return {"domain": {"type_id": [("id", "in", vehicle_type_ids)]}}
        else:
            self.brand_id = False
            self.fuel_type_id = False
            self.type_id = False
            return {"domain": {"type_id": []}}

    type_id = fields.Many2one(
        "service.vehicle.type",
        string="Type",
        required=True,
    )
    fuel_type_id = fields.Many2one(
        "service.vehicle.fuel.type",
        string="Fuel Type",
        required=True,
    )

    year = fields.Char("Year")
    transmission = fields.Selection(
        [
            ("mt", "Manual"),
            ("at", "Automatic"),
        ],
        string="Transmission",
    )
    odometer = fields.Float("Odometer (km)")

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    price = fields.Monetary("Price", currency_field="currency_id")

    description = fields.Html("Description")

    main_image = fields.Image("Main Image")
    image_ids = fields.One2many(
        "showroom.car.vehicle.image",
        "vehicle_id",
        string="Gallery Images",
    )


class CarVehicleImage(models.Model):
    _name = "showroom.car.vehicle.image"
    _description = "Vehicle Gallery Image"
    _order = "id"

    name = fields.Char("Title")
    vehicle_id = fields.Many2one(
        "showroom.car.vehicle",
        string="Vehicle",
        required=True,
        ondelete="cascade",
    )
    image = fields.Image("Image", required=True)
