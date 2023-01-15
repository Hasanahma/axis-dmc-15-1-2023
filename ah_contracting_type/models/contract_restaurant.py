# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ContractRestaurants(models.Model):
    _rec_name = 'name_restaurant'
    _name = 'contract.restaurant'
    _description = 'Contract Restaurants'

    # name = fields.Char(string="Name", required=True)
    name_contract = fields.Char(string="Contract Name", required=True)
    name_restaurant = fields.Many2one('res.partner', string="Restaurant Name", required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    currency_id = fields.Many2one('res.currency')
    exchange_rate = fields.Float(string="Exchange Rate")
    sales_tax = fields.Float(string="Sales Tax")
    service_tax = fields.Float(string="Service Tax")
    rate_per_person = fields.Integer(string="Per Person")
    soft_drink_per_person = fields.Integer(string="Soft Drink Per Person")
    contract_attachment = fields.Binary(string="Contract Attachment")
