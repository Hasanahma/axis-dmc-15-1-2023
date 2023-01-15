# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HotelRates(models.Model):
    _name = 'hotel.rates'
    _rec_name = 'name'
    _description = 'Hotel Rates'

    name = fields.Char(string="Name", required=True)
