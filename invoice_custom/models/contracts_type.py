# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AphasiaCase(models.Model):
    _name = 'contracts.type'
    _description = 'Contracts Type'

    name = fields.Char(string="Name", required=True)
