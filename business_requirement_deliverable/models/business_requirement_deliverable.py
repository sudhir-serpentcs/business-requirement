# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class BusinessRequirementDeliverable(models.Model):
    _name = "business.requirement.deliverable"
    _description = "Business Requirement Deliverable"

    sequence = fields.Integer('Sequence')
    name = fields.Text('Name', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        domain=[('sale_ok', '=', True)],
        required=False
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        required=True
    )
    qty = fields.Float(
        string='Quantity',
        store=True,
        default=1,
    )
    resource_ids = fields.One2many(
        comodel_name='business.requirement.resource',
        inverse_name='business_requirement_deliverable_id',
        string='Business Requirement Resource',
        copy=True,
    )
    business_requirement_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Requirement',
        ondelete='cascade'
    )
    unit_price = fields.Float(
        string='Sales Price'
    )
    price_total = fields.Float(
        compute='_compute_get_price_total',
        string='Total revenue',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        readonly=True,
        compute='_compute_get_currency',
    )

    @api.multi
    @api.depends('business_requirement_id.partner_id')
    def _compute_get_currency(self):
        for brd in self:
            partner_id = brd.business_requirement_id.partner_id
            currency_id = partner_id.property_product_pricelist.currency_id
            if currency_id:
                brd.currency_id = currency_id

    @api.multi
    def _get_pricelist(self):
        for brd in self:
            partner_id = False
            if brd.business_requirement_id and (
                brd.business_requirement_id.partner_id
            ):
                partner_id = brd.business_requirement_id.partner_id
            if partner_id and partner_id.property_product_pricelist:
                return partner_id.property_product_pricelist
            return partner_id

    @api.multi
    @api.depends('unit_price', 'qty')
    def _compute_get_price_total(self):
        for brd in self:
            brd.price_total = brd.unit_price * brd.qty

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        description = ''
        uom_id = False
        product = self.product_id

        if product:
            description = product.name_get()[0][1]
            uom_id = product.uom_id.id

        if product.description_sale:
            description += '\n' + product.description_sale

        unit_price = self.product_id.list_price
        pricelist = self._get_pricelist()

        if pricelist:
            product = self.product_id.with_context(
                lang=self.business_requirement_id.partner_id.lang,
                partner=self.business_requirement_id.partner_id.id,
                quantity=self.qty,
                pricelist=pricelist.id,
                uom=self.uom_id.id,
            )
            unit_price = product.price

        self.name = description
        self.uom_id = uom_id
        self.unit_price = unit_price

    @api.onchange('uom_id', 'qty')
    def product_uom_change(self):
        if not self.uom_id:
            self.price_unit = 0.0
            return
        qty_uom = 0
        unit_price = self.product_id.list_price
        pricelist = self._get_pricelist()
        product_uom = self.env['product.uom']

        if self.qty != 0:
            qty_uom = product_uom._compute_qty(
                self.uom_id.id, self.qty, self.product_id.uom_id.id) / self.qty

        if pricelist:
            product = self.product_id.with_context(
                lang=self.business_requirement_id.partner_id.lang,
                partner=self.business_requirement_id.partner_id.id,
                quantity=self.qty,
                pricelist=pricelist.id,
                uom=self.uom_id.id,
            )
            unit_price = product.price

        self.unit_price = unit_price * qty_uom
