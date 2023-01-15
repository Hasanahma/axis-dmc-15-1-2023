# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HotelSeason(models.Model):
    _name = 'hotel.season'
    _rec_name = 'name'
    _description = 'Hotel Season'

    name = fields.Char(string="Name", required=True)
