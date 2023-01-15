# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class RatesLines(models.Model):
    _name = 'rates.lines'
    _rec_name = 'name'
    _description = 'Rates Lines'

    name = fields.Many2one('hotel.season', string="Seasonality Name")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    rate_per_person_Low = fields.Char(string="Rate Per Person")
    rate_per_person_hb_Low = fields.Char(string="Rate Per Person HB")
    single_supplement_Low = fields.Char(string="Single Supplement")
    extra_bed_supplement_Low = fields.Char(string="Extra Bed Supplement")
    extra_meal_supplement_Low = fields.Char(string="Extra Meal Supplement")
    contract_hotel_id = fields.Many2one('contract.hotel', string='Contract Hotel ID')
