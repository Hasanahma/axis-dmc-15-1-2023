# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HotelPromotion(models.Model):
    _name = 'hotel.promotion'
    _rec_name = 'name'
    _description = 'Hotel Promotion'

    name = fields.Char(string="Name", required=True)
