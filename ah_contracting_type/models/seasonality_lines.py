# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SeasonalityLines(models.Model):
    _name = 'seasonality.lines'
    _rec_name = 'name'
    _description = 'Seasonality Lines'

    name = fields.Many2one('hotel.season', string="Seasonality Name")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    contract_hotel_id = fields.Many2one('contract.hotel', string='Contract Hotel ID')
