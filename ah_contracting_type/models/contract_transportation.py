# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ContractHotel(models.Model):
    _rec_name = 'name_company'
    _name = 'contract.transportation'
    _description = 'Contract Transportation'

    name_contract = fields.Char(string="Contract Name", required=True)
    name_company = fields.Many2one('res.partner', string="Company Name", required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    currency_id = fields.Many2one('res.currency')
    exchange_rate = fields.Float(string="Exchange Rate")
    sales_tax = fields.Float(string="Sales Tax")
    discount = fields.Float(string="Disc.%")
    contract_attachment = fields.Binary(string="Contract Attachment")
    vehicles_id = fields.Many2one('type.vehicles', string="Type of Vehicles")
    route_service_id = fields.Many2one('route.services', string="Route-Services")
    route_by_id = fields.Many2one('route.by', string="Contract By Routes")
    rate = fields.Float(string="Rate")
    rate_by = fields.Float(string="Rate")
    currency_by = fields.Float(string="Currency")
    routes_by_id = fields.Many2one('car.van', string="Type of Vehicles")


class TypeOfVehicles(models.Model):
    _name = 'type.vehicles'

    name = fields.Char(string="Vehicle")
    type = fields.Selection([('van', 'Van'),
                             ('car', 'Car'),
                             ('bus', 'Bus')], string="Vehicle Type")
    seats = fields.Integer(string="Seats")


class RouteServices(models.Model):
    _name = 'route.services'

    name = fields.Char(string="Route")
    seats = fields.Integer(string="Seats")


class RouteBY(models.Model):
    _name = 'route.by'

    name = fields.Char(string="Route")
    seats = fields.Integer(string="Seats")


class CarAndVan(models.Model):
    _name = 'car.van'

    name = fields.Char(string="Rate")
    seats = fields.Integer(string="Seats")
