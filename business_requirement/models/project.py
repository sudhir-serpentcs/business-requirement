# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class Project(models.Model):
    _inherit = "project.project"

    br_ids = fields.One2many(
        comodel_name='business.requirement',
        inverse_name='project_id',
        string='Business Requirements',
        copy=False,
    )
