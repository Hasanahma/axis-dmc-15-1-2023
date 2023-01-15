# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PromotionLines(models.Model):
    _name = 'promotion.lines'
    _rec_name = 'name'
    _description = 'Promotion Lines'

    name = fields.Many2one('hotel.promotion', string="Promotion Name")
    date_from_black_out = fields.Date(string="Date From")
    date_to_black_out = fields.Date(string="Date To")
    contract_hotel_id = fields.Many2one('contract.hotel', string='Contract Hotel ID')
