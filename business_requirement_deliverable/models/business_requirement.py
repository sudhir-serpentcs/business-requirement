# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    deliverable_lines = fields.One2many(
        comodel_name='business.requirement.deliverable',
        inverse_name='business_requirement_id',
        string='Deliverable Lines',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    total_revenue = fields.Float(
        compute='_compute_deliverable_total',
        string='Total Revenue',
        store=False
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        readonly=True,
        compute='_compute_get_currency',
    )

    @api.multi
    @api.depends('partner_id')
    def _compute_get_currency(self):
        if self.partner_id and (
            self.partner_id.property_product_pricelist.currency_id
        ):
            self.currency_id = \
                self.partner_id.property_product_pricelist.currency_id

    @api.multi
    @api.onchange('partner_id')
    def partner_id_change(self):
        for record in self:
            if record.deliverable_lines:
                raise UserError(_(
                    'You are changing customer, on a business requirement'
                    'which already contains deliverable lines.'
                    'Pricelist could be different.'))

    @api.multi
    @api.depends(
        'deliverable_lines',
        'company_id.currency_id',
    )
    def _compute_deliverable_total(self):
        for br in self:
            if br.deliverable_lines:
                total_revenue_origin = sum(
                    line.price_total
                    for line in br.deliverable_lines
                )
                if br.partner_id.property_product_pricelist.currency_id:
                    br.total_revenue = \
                        br.partner_id.property_product_pricelist.currency_id\
                        .compute(
                            total_revenue_origin, br.company_id.currency_id)
                else:
                    br.total_revenue = total_revenue_origin
