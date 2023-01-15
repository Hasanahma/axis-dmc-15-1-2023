# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ContractHotel(models.Model):
    _rec_name = 'name_guide'
    _name = 'contract.guide'
    _description = 'Contract Guide'

    name_contract = fields.Char(string="Contract Name", required=True)
    name_guide = fields.Many2one('res.partner', string="Guide Name", required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    currency_id = fields.Many2one('res.currency')
    exchange_rate = fields.Float(string="Exchange Rate")
    guide_fees_per_day = fields.Float(string="Guide Fees Per Day")
    overnights_per_day = fields.Float(string="Overnights Per Day")
