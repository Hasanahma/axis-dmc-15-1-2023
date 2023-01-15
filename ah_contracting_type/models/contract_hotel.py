# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ContractHotel(models.Model):
    _rec_name = 'name_hotel'
    _name = 'contract.hotel'
    _description = 'Contract Hotel'

    name_contract = fields.Char(string="Contract Name")
    name_hotel = fields.Many2one('res.partner', string="Hotel Name", required=True)
    date_from = fields.Date(string="Date From")
    date_from_low = fields.Date(string="Date From")
    date_from_high = fields.Date(string="Date From")
    date_from_peak = fields.Date(string="Date From")
    date_from_black_out = fields.Date(string="Date From")
    date_from_promotion = fields.Date(string="Date From")
    date_from_holiday = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    date_to_low = fields.Date(string="Date To")
    date_to_high = fields.Date(string="Date To")
    date_to_peak = fields.Date(string="Date To")
    date_to_black_out = fields.Date(string="Date To")
    date_to_promotion = fields.Date(string="Date To")
    date_to_holiday = fields.Date(string="Date To")
    currency_id = fields.Many2one('res.currency')
    exchange_rate = fields.Float(string="Exchange Rate")
    contract_attachment = fields.Binary(string="Contract Attachment")
    sales_tax = fields.Float(string="Sales Tax")
    service_tax = fields.Float(string="Service Tax")
    low_season = fields.Date(string="Low Season")
    rate_per_person_Low = fields.Char(string="Rate Per Person ")
    rate_per_person_hb_Low = fields.Char(string="Rate Per Person HB ")
    single_supplement_Low = fields.Char(string="Single Supplement ")
    extra_bed_supplement_Low = fields.Char(string="Extra Bed Supplement ")
    extra_meal_supplement_Low = fields.Char(string="Extra Meal Supplement")
    rate_per_person_high = fields.Char(string="rate per person high")
    rate_per_person_hb_high = fields.Char(string="rate per person hb high")
    single_supplement_high = fields.Char(string="single supplement high")
    extra_bed_supplement_high = fields.Char(string="extra bed supplement high")
    extra_meal_supplement_high = fields.Char(string="extra meal supplement high")
    rate_per_person_peak = fields.Char(string="rate_per_person_peak")
    rate_per_person_hb_peak = fields.Char(string="rate per person hb peak")
    single_supplement_peak = fields.Char(string="single supplement peak")
    extra_bed_supplement_peak = fields.Char(string="extra bed supplement peak")
    extra_meal_supplement_peak = fields.Char(string="extra meal supplement peak")

    date_from_black_out = fields.Date(string="Date From")
    date_to_black_out = fields.Date(string="Date To")

    high_season = fields.Date(string="High Season")
    peak_season = fields.Date(string="Peak Season")
    room_type = fields.Many2one('room.category', string="Rooming Type")
    rate_per_room = fields.Integer(string="Rate Per Room")
    seasonality_lines = fields.One2many('seasonality.lines', 'contract_hotel_id', string="Seasonality Lines")
    promotion_lines = fields.One2many('promotion.lines', 'contract_hotel_id', string="Promotion Lines")
    rates_lines = fields.One2many('rates.lines', 'contract_hotel_id', string="Rates Lines")


class RoomCategory(models.Model):
    _name = 'room.category'
    _description = 'Room Category'

    name = fields.Char(string="Name")
