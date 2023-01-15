import base64
from copy import copy
from locale import currency

import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime


class SaleOrderCustom(models.Model):
    _inherit = 'sale.order'

    def print_visa_list(self):
        return self.env.ref('invoice_custom.action_visa_list').report_action(self)

    def calculate_total_pax(self):
        all_sale_order = self.env['sale.order'].search([])
        for record in all_sale_order:
            record.total_pax = record.adult_number + record.child_number + record.inf_number

    def action_confirm(self):
        super(SaleOrderCustom, self).action_confirm()
        self.state = 'sale'

    @api.depends('adult_number', 'child_number', 'inf_number')
    def _compute_total_pax(self):
        for rec in self:
            total = 0
            if rec.adult_number:
                total += rec.adult_number
            if rec.child_number:
                total += rec.child_number
            if rec.inf_number:
                total += rec.inf_number
            rec.total_pax = total

    @api.depends('hotels_expense_ids.pax')
    def _compute_pax_reservation(self):
        total_reservation = 0
        for rec in self:
            for hotel in rec.hotels_expense_ids:
                total_reservation += hotel.pax
            rec.reservation_pax = total_reservation
            rec.remaining_pax = rec.total_pax - total_reservation

    customer = fields.Char(string='Customer', required=True)
    arrival_date = fields.Date(string='Arrival Date ')
    departure_date = fields.Date(string="Departure Date")
    file_no = fields.Char(string='Agent ref.')
    accommodation_id = fields.Many2one('accommodation')
    actual_expense_ids = fields.One2many('account.move.line', 'sale_order_id', string="Actual Expense")
    total_actual_expense = fields.Float(compute='_compute_total_actual_expense', string='Total', store=True)
    actual_expense_total = fields.Float(string='Total')
    estimate_expense_ids = fields.One2many('estimate.expense', 'sale_order_id', string="Estimate Expense")
    total_estimate_expense = fields.Float(compute='_compute_total_estimate_expense', string='Total', store=True)
    other_currency_id = fields.Many2one('res.currency', string="Currency")
    converging_rate = fields.Float("Converging rate")
    total_other_currency = fields.Float("Total Other Currency")
    adult_number = fields.Integer("Adult")
    child_number = fields.Integer("Child")
    inf_number = fields.Integer("Inf.")
    total_pax = fields.Integer(string="Total Pax", compute='_compute_total_pax', store=True)
    reservation_pax = fields.Integer("Reservation Pax", compute='_compute_pax_reservation', store=True)
    remaining_pax = fields.Integer("Remaining Pax", compute='_compute_pax_reservation', store=True)
    nationality_id = fields.Many2one('res.country', string="Nationality")
    general_note_visibility = fields.Boolean(string="General Note Visibility")
    general_note = fields.Text(string="General Note")
    arrival_departure_expense_ids = fields.One2many('arrival.departure.expense', 'sale_order_id', string="Arr/Dep",
                                                    copy=True)
    hotels_expense_ids = fields.One2many('hotels', 'sale_order_id', string="Hotels", copy=True)
    itineraries_expense_ids = fields.One2many('itineraries', 'sale_order_id', string="Program / Itinerary", copy=True)
    resturnats_expense_ids = fields.One2many('restaurants', 'sale_order_id', string="Restaurants", copy=True)
    transportation_expense_ids = fields.One2many('transportation', 'sale_order_id', string="Transportation", copy=True)
    guide_expense_ids = fields.One2many('guide', 'sale_order_id', string="Guide", copy=True)
    clients_expense_ids = fields.One2many('clients', 'sale_order_id', string="Clients", copy=False)
    clients_passport_ids = fields.One2many('clients.passport', 'sale_order_id', string="Clients", copy=False)
    entrance_expense_ids = fields.One2many('entrance', 'sale_order_id', string="Entrance", copy=True)
    extras_expense_ids = fields.One2many('extras', 'sale_order_id', string="Extras", copy=True)
    inclusions_expense_ids = fields.One2many('inclusions', 'sale_order_id', string="Inclusions", copy=True)
    cost_status = fields.Selection([('close', 'Closed'), ('pending', 'Pending')], default='pending', copy=False)
    excel_file = fields.Binary(string='Import Excel')
    revenue_ids = fields.One2many('sales.revenue', 'sale_order_id', string='Revenue Lines')
    last_calculated_time = fields.Datetime('Last Update On')
    invoiced_amount = fields.Float('Revenue', digits=(12, 3))
    profit_loss = fields.Float('Profit/Loss', digits=(12, 3))
    net_profit_margin = fields.Float('Net Profit Margin', digits=(12, 3))
    additional_note = fields.Text(string="Add. Note")
    details_ids = fields.One2many('details', 'sale_order_id', string="Details", copy=False)
    delegate_name = fields.Char('Representative name', copy=False)
    delegate_number = fields.Char('Representative  number', copy=False)
    guide_id = fields.Many2one('res.partner', string="Guide Name", copy=False)
    transportation_id = fields.Many2one('transportation', string="Transportation name", copy=False)
    age = fields.Selection([('ADT', 'ADT'), ('CHD', 'CHD'), ('INF.', 'INF.')], string="Age", copy=False)
    room_type_id = fields.Many2one('room.types', string="Room Type", copy=False)
    rn = fields.Integer(string="Room#", copy=False)
    manifest_excel_file = fields.Binary(string='Import Excel')

    def action_calculate_all_profit_loss(self):
        for record in self:
            record.calculate_profit_loss()

    def change_selected(self):
        for record in self.clients_expense_ids:
            if record.select == True:
                if self.age:
                    record.age = self.age
                if self.room_type_id:
                    record.room_type_id = self.room_type_id
                if self.rn:
                    record.rn = self.rn

        for record in self.clients_expense_ids:
            record.select = False

    def select_all_rooming_list(self):
        for record in self.clients_expense_ids:
            record.select = True

    def un_select_all_rooming_list(self):
        for record in self.clients_expense_ids:
            record.select = False

    def select_all_manifest(self):
        for record in self.clients_passport_ids:
            record.select = True

    def un_select_all_manifest(self):
        for record in self.clients_passport_ids:
            record.select = False

    def delete_selected_rooming_list(self):
        for record in self.clients_expense_ids:
            if record.select == True:
                record.unlink()

    def delete_selected_manifest(self):
        for record in self.clients_passport_ids:
            if record.select == True:
                record.unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({'invoiced_amount': 0, 'profit_loss': 0, 'actual_expense_total': 0, 'net_profit_margin': 0})
        return super(SaleOrderCustom, self).copy(default)

    def calculate_profit_loss(self):

        revenue_obj = self.env['sales.revenue']
        revenue_obj.search([('sale_order_id', '=', self.id)]).unlink()

        for order in self:
            sale_order_invoices = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
        total_amount = 0
        for invoices in sale_order_invoices:
            revenue_obj.create({
                'sale_order_id': self.id,
                'label': invoices.name,
                'amount': invoices.amount_total_signed,
            })
            total_amount += invoices.amount_total_signed

        total_cost = 0
        for cost_total in self.env['account.move.line'].search([('sale_order_id', '=', self.id)]):
            total_cost += cost_total.debit

        self.invoiced_amount = total_amount
        self.actual_expense_total = total_cost
        self.profit_loss = self.invoiced_amount - self.actual_expense_total
        if self.invoiced_amount == 0:
            self.net_profit_margin = 0
        else:
            self.net_profit_margin = self.profit_loss / self.invoiced_amount
        self.last_calculated_time = datetime.now()

        # move_ids = self.mapped('order_line.invoice_lines.move_id')
        # total_amount = 0
        # for move in move_ids:
        #     for item in move.line_ids:
        #         total_amount += item.debit
        #         revenue_obj.create({
        #             'sale_order_id': self.id,
        #             'label': item.name,
        #             'amount' : item.debit
        #         })
        # sum_of_cost_total = 0
        # for cost_total in self.env['account.move.line'].search([('sale_order_id', '=', self.id)]):
        #     sum_of_cost_total += cost_total.debit

        # select
        # debit
        # from account_move_line where
        # sale_order_id = 719;

    def compute_other_currency(self):
        self.total_other_currency = self.amount_total * self.converging_rate

    @api.depends('estimate_expense_ids.amount')
    def _compute_total_estimate_expense(self):
        items = self.env['estimate.expense']
        for rec in self:
            total = 0
            items_ids = items.search([('sale_order_id', '=', rec.id)])
            if items_ids:
                for line in items_ids:
                    total += line.amount
                rec.total_estimate_expense = total

    def get_from_rooming_list(self):
        for line in self.clients_expense_ids:
            self.env['clients.passport'].create({
                'sale_order_id': self.id,
                'name': line.name
            })

    def get_from_manifest(self):
        for line in self.clients_passport_ids:
            self.env['clients'].create({
                'sale_order_id': self.id,
                'name': line.name
            })

    def import_manifest_from_excel(self):
        try:
            wb = xlrd.open_workbook(
                file_contents=base64.decodebytes(self.manifest_excel_file))
            sheet = wb.sheet_by_index(0)
            row_number = 0

            for row in range(sheet.nrows):
                if row == 0:
                    continue

                if sheet.cell(row, 2).value != '':
                    if isinstance(sheet.cell(row, 2).value, float):
                        birth_date = datetime(*xlrd.xldate_as_tuple(sheet.cell(row, 2).value, wb.datemode))
                    elif isinstance(sheet.cell(row, 2).value, str):
                        birth_date = datetime.strptime(sheet.cell(row, 2).value, '%d/%m/%Y')
                else:
                    birth_date = None

                if sheet.cell(row, 3).value != '':
                    if isinstance(sheet.cell(row, 3).value, float):
                        issue_date = datetime(*xlrd.xldate_as_tuple(sheet.cell(row, 3).value, wb.datemode))
                    elif isinstance(sheet.cell(row, 3).value, str):
                        issue_date = datetime.strptime(sheet.cell(row, 3).value, '%d/%m/%Y')
                else:
                    issue_date = None

                if sheet.cell(row, 4).value != '':
                    if isinstance(sheet.cell(row, 4).value, float):
                        expiry_date = datetime(*xlrd.xldate_as_tuple(sheet.cell(row, 4).value, wb.datemode))
                    elif isinstance(sheet.cell(row, 4).value, str):
                        expiry_date = datetime.strptime(sheet.cell(row, 4).value, '%d/%m/%Y')
                else:
                    expiry_date = None

                dic = {
                    'sale_order_id': self.id,
                    'name': sheet.cell(row, 0).value,
                    'passport_number': sheet.cell(row, 1).value if sheet.cell(row, 1).value != '' else None,
                    'birth_date': birth_date,
                    'issue_date': issue_date,
                    'expiry_date': expiry_date,
                    'nationality_id': self.env['res.country'].search(
                        [('name', 'ilike', sheet.cell(row, 5).value)]).id if sheet.cell(row, 5).value != '' else None,
                }

                self.write({'clients_passport_ids': [(0, 0, dic)]})
            self.manifest_excel_file = False;
        except Exception as e:
            raise UserError(
                _("Sorry, Your excel file does not match with our format " + str(e)))

    def import_from_excel(self):
        try:
            wb = xlrd.open_workbook(
                file_contents=base64.decodebytes(self.excel_file))
            sheet = wb.sheet_by_index(0)
            row_number = 0

            for row in range(sheet.nrows):
                if row == 0:
                    continue

                dic = {
                    'sale_order_id': self.id,
                    'name': sheet.cell(row, 0).value,
                    'age': sheet.cell(row, 1).value if sheet.cell(row, 1).value != '' else None,
                    'room_type_id': self.env['room.types'].search(
                        [('name', 'ilike', sheet.cell(row, 2).value)]).id if sheet.cell(row, 2).value != '' else None,
                    'rn': sheet.cell(row, 3).value if sheet.cell(row, 3).value != '' else None,
                    'note': sheet.cell(row, 4).value,
                }

                self.write({'clients_expense_ids': [(0, 0, dic)]})
            self.excel_file = False;
        except Exception as e:
            raise UserError(
                _("Sorry, Your excel file does not match with our format " + str(e)))

    def change_cost_status(self):
        if self.cost_status == 'close':
            self.cost_status = 'pending'
            self.state = 'sale'
        else:
            self.cost_status = 'close'
            self.state = 'done'

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderCustom, self)._prepare_invoice()
        invoice_vals['customer'] = self.customer
        invoice_vals['other_currency_id'] = self.other_currency_id.id
        invoice_vals['converging_rate'] = self.converging_rate
        invoice_vals['total_other_currency'] = self.total_other_currency
        invoice_vals['arrival_date'] = self.arrival_date
        invoice_vals['departure_date'] = self.departure_date
        invoice_vals['nationality_id'] = self.nationality_id
        invoice_vals['adult_number'] = self.adult_number
        invoice_vals['child_number'] = self.child_number
        invoice_vals['inf_number'] = self.inf_number
        invoice_vals['general_note_visibility'] = self.general_note_visibility
        invoice_vals['general_note'] = self.general_note
        return invoice_vals


class AccountMoveCustom(models.Model):
    _inherit = 'account.move'

    def button_cancel(self):
        self.env['hotels'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['hotels'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['restaurants'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['restaurants'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['transportation'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['transportation'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['guide'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['guide'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['extras'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['extras'].search([('bill_id', '=', self.id)]).bill_id = None
        return super(AccountMoveCustom, self).button_cancel()

    def unlink(self):
        self.env['hotels'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['hotels'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['restaurants'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['restaurants'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['transportation'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['transportation'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['guide'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['guide'].search([('bill_id', '=', self.id)]).bill_id = None
        self.env['extras'].search([('bill_id', '=', self.id)]).is_created_bill = False
        self.env['extras'].search([('bill_id', '=', self.id)]).bill_id = None
        return super(AccountMoveCustom, self).unlink()

    @api.depends('adult_number', 'child_number', 'inf_number')
    def _compute_total_pax(self):
        for rec in self:
            total = 0
            if rec.adult_number:
                total += rec.adult_number
            if rec.child_number:
                total += rec.child_number
            if rec.inf_number:
                total += rec.inf_number
            rec.total_pax = total

    customer = fields.Char(string='Customer')
    arrival_date = fields.Date(string='Arrival Date ')
    departure_date = fields.Date(string="Departure Date")
    file_no = fields.Char(string='Agent ref.')
    accommodation_id = fields.Many2one('accommodation')
    other_currency_id = fields.Many2one('res.currency', string="Currency")
    converging_rate = fields.Float("Converging rate")
    total_other_currency = fields.Float("Total Other Currency")
    adult_number = fields.Integer("Adult")
    child_number = fields.Integer("Child")
    inf_number = fields.Integer("Inf.")
    total_pax = fields.Integer(string="Total Pax", compute='_compute_total_pax', store=True)
    nationality_id = fields.Many2one('res.country', string="Nationality")
    general_note_visibility = fields.Boolean(string="General Note Visibility")
    general_note = fields.Text(string="General Note")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_sale_order = fields.Boolean("Is SO")
    sale_order_id = fields.Many2one('sale.order', "SO")
    expense_type_id = fields.Many2one('expense.type')

    @api.onchange('is_sale_order')
    def onchange_is_sale(self):
        if not self.is_sale_order:
            self.sale_order_id = False

    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        if not self.is_sale_order:
            self.sale_order_id = False

    def unlink(self):
        if self.sale_order_id:
            sale_order_id = self.sale_order_id
            res = super(AccountMoveLine, self).unlink()
            items_ids = self.env['account.move.line'].search([('sale_order_id', 'in', sale_order_id.ids)])
            total = 0
            if items_ids:
                for line in items_ids:
                    total += line.price_subtotal
                order_id = self.env['sale.order'].search([('id', 'in', sale_order_id.ids)])
                order_id.write({
                    "actual_expense_total": total
                })
            else:
                order_id = self.env['sale.order'].search([('id', 'in', sale_order_id.ids)])
                order_id.write({

                    "actual_expense_total": total
                })
        else:
            res = super(AccountMoveLine, self).unlink()

        return res

    def write(self, vals):
        if 'sale_order_id' in vals:
            sale_order_id = vals['sale_order_id']
            if sale_order_id != False:
                res = super(AccountMoveLine, self).write(vals)
                items_ids = self.env['account.move.line'].search([('sale_order_id', '=', sale_order_id)])
                total = 0
                if items_ids:
                    for line in items_ids:
                        total += line.price_subtotal
                    order_id = self.env['sale.order'].search([('id', '=', sale_order_id)])
                    order_id.write({
                        "actual_expense_total": total
                    })
                else:
                    order_id = self.env['sale.order'].search([('id', '=', sale_order_id)])
                    order_id.write({
                        "actual_expense_total": total
                    })
            else:
                sale_order_id = self.sale_order_id.id
                res = super(AccountMoveLine, self).write(vals)
                items_ids = self.env['account.move.line'].search([('sale_order_id', '=', sale_order_id)])
                total = 0
                if items_ids:
                    for line in items_ids:
                        total += line.price_subtotal
                    order_id = self.env['sale.order'].search([('id', '=', sale_order_id)])
                    order_id.write({
                        "actual_expense_total": total
                    })
                else:
                    order_id = self.env['sale.order'].search([('id', '=', sale_order_id)])
                    order_id.write({
                        "actual_expense_total": total
                    })
        else:
            for sale_order_id in self.sale_order_id:
                items_ids = self.env['account.move.line'].search([('sale_order_id', '=', sale_order_id.id)])
                total = 0
                if items_ids:
                    for line in items_ids:
                        total += line.price_subtotal
                    order_id = self.env['sale.order'].search([('id', '=', sale_order_id.id)])
                    order_id.write({
                        "actual_expense_total": total
                    })
                else:
                    order_id = self.env['sale.order'].search([('id', '=', sale_order_id.id)])
                    order_id.write({
                        "actual_expense_total": total
                    })
            res = super(AccountMoveLine, self).write(vals)
        return res


class Accommodation(models.Model):
    _name = 'accommodation'

    name = fields.Char(string="Accommodation")


class ExpenseType(models.Model):
    _name = 'expense.type'

    name = fields.Char(string="Expense", required=True)


class EstimateExpense(models.Model):
    _name = 'estimate.expense'

    name = fields.Char(string="Description", required=True)
    sale_order_id = fields.Many2one('sale.order', "SO")
    expense_type_id = fields.Many2one('expense.type', string="Cost Type", required=True)
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    date_from = fields.Date("Date from")
    date_to = fields.Date("Date to")
    currency_id = fields.Many2one('res.currency', string="Currency", default=93)
    currency_rate = fields.Float("Converging rate")

    unit_cost = fields.Float("Unit Cost")
    pax = fields.Integer("PAX")
    amount = fields.Float("Total", compute='_compute_total_amount', store=True)
    total_other_currency = fields.Float("Total Other Currency")

    @api.onchange('currency_id')
    def onhcnage_currency_id(self):
        if self.currency_id:
            self.currency_rate = self.currency_id.rate

    @api.depends('unit_cost', 'pax', 'currency_rate', 'currency_id')
    def _compute_total_amount(self):
        for record in self:
            record.amount = record.unit_cost * record.pax
            record.total_other_currency = record.amount * record.currency_rate


class ResPartner(models.Model):
    _inherit = 'res.partner'

    expense_partner_ids = fields.Many2many('expense.type', 'expense_type_res_partner_rel', 'expens_type_id',
                                           'res_partner_id', 'Expense Type')
    estimate_expense_ids = fields.One2many('estimate.expense', 'vendor_id', string="Estimate Cost")
    language_ids = fields.Many2many("guide.language", string="Language")
    priority = fields.Selection([
        ('0', '0 Star'),
        ('1', '1 Star'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ], string="Priority")


class ArrivalDepartureExpense(models.Model):
    _name = 'arrival.departure.expense'

    name = fields.Selection([('ARR', 'ARR'),
                             ('DEP', 'DEP')], string="Type", required=True, default='ARR')
    sale_order_id = fields.Many2one('sale.order', "SO")
    date = fields.Date(string="Date")
    border = fields.Many2one('borders', string="Border")
    flight = fields.Char(string="Flight")
    time = fields.Float(string="Time")
    str_time = fields.Char("Time")
    pax = fields.Integer("Pax")
    meet_by = fields.Many2one('res.partner')
    notes = fields.Char(string="Notes")
    unit_cost = fields.Float("Unit Cost")
    amount = fields.Float("Total", compute='_compute_total_amount', store=True)
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    hotel_id = fields.Many2one('hotels', string='Hotel')
    guide_id = fields.Many2one('guide', 'Guide')
    transportation_id = fields.Many2one('transportation', 'Transportation')
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    copy = fields.Char(string='copy', )
    show = fields.Boolean(string="Show", default=True)

    @api.onchange('time')
    def _onchange_time(self):
        for rec in self:
            str_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.time * 60, 60))
            rec.str_time = str_time

    def duplicate_action(self):
        vals = {
            'name': self.name,
            'sale_order_id': self.sale_order_id.id,
            'date': self.date,
            'border': self.border.id,
            'flight': self.flight,
            'time': self.time,
            'str_time': self.str_time,
            'pax': self.pax,
            'meet_by': self.meet_by.id,
            'notes': self.notes,
            'unit_cost': self.unit_cost,
            'amount': self.amount,
            'customer': self.customer,
            'partner_id': self.partner_id.id,
            'hotel_id': self.hotel_id.id,
            'guide_id': self.guide_id.id,
            'transportation_id': self.transportation_id.id,
            'status_of_sale_order': self.status_of_sale_order,
            'copy': 'copy',
        }
        self.env['arrival.departure.expense'].create(vals)

    def write(self, vals):
        vals['copy'] = 'no'
        result = super(ArrivalDepartureExpense, self).write(vals)
        return result

    @api.depends('unit_cost', 'pax')
    def _compute_total_amount(self):
        for record in self:
            record.amount = record.unit_cost * record.pax


class Borders(models.Model):
    _name = 'borders'

    name = fields.Char(string="Name", required=True)


class Hotels(models.Model):
    _name = 'hotels'
    _description = 'Hotels'

    @api.depends('date_from', 'date_to')
    def compute_nights(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                nights = datetime.strptime(str(rec.date_to), "%Y-%m-%d") - datetime.strptime(str(rec.date_from),
                                                                                             "%Y-%m-%d")
                rec.nights = nights.days
            else:
                rec.nights = 0.0

    @api.depends('sgl_room', 'dbl_room', 'trp_room', 'twin_room', 'oth_room', 'nights')
    def compute_trn(self):
        for rec in self:
            rec.trn = (rec.sgl_room + rec.dbl_room + rec.trp_room + rec.twin_room + rec.oth_room) * rec.nights
            rec.pax = rec.sgl_room + (rec.dbl_room * 2) + (rec.trp_room * 3) + (rec.twin_room * 2)

    sale_order_id = fields.Many2one('sale.order', "SO")
    name = fields.Many2one('res.partner', string="Hotel")
    date_from = fields.Date(string="Check in")
    date_to = fields.Date(string="Check out")
    nights = fields.Float(string="Nights", compute='compute_nights', store=True)
    trn = fields.Float(string="T.R.N", compute='compute_trn', store=True)
    note = fields.Text(string="Notes")
    special_rates = fields.Float(string="Special rates")
    room_type_id = fields.Many2one('room.types', string="Room Type")
    room_category_id = fields.Many2one('room.category', string="Room Category")
    meal_id = fields.Many2one('hotel.meals', string="Meals")
    status_id = fields.Many2one('hotel.status', string="Status")
    is_received_invoice = fields.Boolean(string="Received invoice", copy=False)
    invoice_date = fields.Date(string="Invoice Date", copy=False)
    invoice_number = fields.Char(string="Invoice #", copy=False)
    pax = fields.Integer(string="Pax", compute='compute_trn', store=True)
    estimated_price = fields.Float(string="Estimated price")
    actual_price = fields.Float(string="Actual price", copy=False)
    sgl_room = fields.Integer("SGL")
    dbl_room = fields.Integer("DBL")
    trp_room = fields.Integer("TRP")
    twin_room = fields.Integer("TWIN")
    oth_room = fields.Integer("OTH")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    copy = fields.Char(string='copy', )
    additional_note = fields.Text(string="Add. Note")
    per_pax = fields.Boolean('Per Pax')
    per_room = fields.Boolean('Per Room')
    per_person = fields.Float(string='P.P')
    single_supp = fields.Float(string='SGL.Supp')
    third_person = fields.Float(string='3rd Person')
    dbl_room_rate = fields.Float(string='DBL')
    sgl_room_rate = fields.Float(string='SGL')
    trp_room_rate = fields.Float(string='TRP')
    sgl_rate = fields.Float('SGL Rate')
    dbl_rate = fields.Float('DBL Rate')
    trp_rate = fields.Float('TRP Rate')
    twin_rate = fields.Float('TWIN Rate')
    oth_rate = fields.Float('OTH Rate')
    currency_id = fields.Many2one('res.currency', string='Currency')
    expense_type_id = fields.Many2one('expense.type', string="Expense Type", copy=False)
    is_created_bill = fields.Boolean('Created Bill', default=False, copy=False)
    bill_id = fields.Many2one('account.move', string="bill id", copy=False)
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict', copy=False)
    by_state = fields.Many2one('res.country.state', string="Location", related="name.state_id")
    show = fields.Boolean(string="Show", default=True)
    priority = fields.Selection([
        ('0', '0 Star'),
        ('1', '1 Star'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ], string="Priority", related="name.priority")
    foc_sgl = fields.Float('FOC SGL')
    foc_dbl = fields.Float('FOC DBL')
    foc_trp = fields.Float('FOC TRP')
    foc_twin = fields.Float('FOC TWIN')
    total_sgl = fields.Float('TOTAL SGL')
    total_dbl = fields.Float('TOTAL DBL')
    total_trp = fields.Float('TOTAL TRP')
    total_twin = fields.Float('TOTAL TWIN')
    net_estimated_price = fields.Float(string="Net Estimated price")

    @api.onchange('per_room', 'per_pax', 'sgl_rate', 'foc_sgl', 'dbl_rate', 'foc_dbl', 'trp_rate', 'foc_trp',
                  'twin_rate', 'foc_twin', 'per_person', 'sgl_room_rate', 'dbl_room_rate', 'trp_room_rate',
                  'dbl_room_rate')
    def _onchange_total_foc(self):
        if self.per_pax:
            self.total_sgl = self.sgl_rate - (self.foc_sgl * self.per_person)
            self.total_dbl = self.dbl_rate - (self.foc_dbl * self.per_person)
            self.total_trp = self.trp_rate - (self.foc_trp * self.per_person)
            self.total_twin = self.twin_rate - (self.foc_twin * self.per_person)
        elif self.per_room:
            self.total_sgl = self.sgl_rate - (self.foc_sgl * self.sgl_room_rate)
            self.total_dbl = self.dbl_rate - (self.foc_dbl * self.dbl_room_rate)
            self.total_trp = self.trp_rate - (self.foc_trp * self.trp_room_rate)
            self.total_twin = self.twin_rate - (self.foc_twin * self.dbl_room_rate)
        else:
            self.total_sgl = 0
            self.total_dbl = 0
            self.total_trp = 0
            self.total_twin = 0

    def button_open_hotel(self):
        self.is_received_invoice = False

    def button_close_hotel(self):
        self.is_received_invoice = True

    def button_go_to_hotel_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.bill_id.id,
            # 'name': self.employee_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }

    def button_create_hotel_bill(self):
        pass
        # vals = {
        #     'partner_id': self.name,
        #     'ref': self.invoice_number,
        #     'invoice_date': self.invoice_date,
        #     'payment_reference': self.sale_order_id.name,
        #     'date': self.date_from,
        #     'invoice_date_due': self.date_from,
        #     'move_type': 'in_invoice',
        #     'posted_before': False,
        #     'payment_state': 'not_paid',
        #     'ref': self.invoice_number,
        #     'invoice_line_ids': [
        #         {'product_id': self.product_id,
        #          'is_sale_order': True,
        #          'sale_order_id': self.sale_order_id,
        #          'expense_type_id': self.expense_type_id,
        #          'price_unit': self.actual_price,
        #          }]
        #
        # }
        # created_bill_id = self.env['account.move'].create(vals)
        # self.is_created_bill = True
        # self.bill_id = created_bill_id
        # self.is_received_invoice = True

    @api.onchange('per_person', 'single_supp', 'sgl_room', 'nights', 'per_pax', 'dbl_room', 'trp_room', 'twin_room',
                  'sgl_room_rate', 'dbl_room_rate', 'trp_room_rate', 'dbl_room_rate')
    def _onchange_sgl_rate(self):
        if self.per_pax:
            self.sgl_rate = (self.per_person + self.single_supp) * self.sgl_room * self.nights
            self.dbl_rate = self.per_person * 2 * self.dbl_room * self.nights
            self.trp_rate = ((self.per_person * 2) + self.third_person) * self.nights * self.trp_room
            self.twin_rate = self.per_person * 2 * self.twin_room * self.nights

        if self.per_room:
            self.sgl_rate = self.sgl_room * self.nights * self.sgl_room_rate
            self.dbl_rate = self.dbl_room * self.nights * self.dbl_room_rate
            self.trp_rate = self.trp_room * self.nights * self.trp_room_rate
            self.twin_rate = self.twin_room * self.nights * self.dbl_room_rate

    @api.onchange('sgl_rate', 'dbl_rate', 'trp_rate', 'twin_rate')
    def _onchange_estimated_price(self):
        self.estimated_price = self.sgl_rate + self.dbl_rate + self.trp_rate + self.twin_rate

    @api.onchange('total_sgl', 'total_dbl', 'total_trp', 'total_twin')
    def _onchange_net_estimated_price(self):
        self.net_estimated_price = self.total_sgl + self.total_dbl + self.total_trp + self.total_twin

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s %s' % (rec.date_from, rec.name.name)))
        return res

    def print_voucher_action(self):
        pass

    def duplicate_action(self):
        vals = {
            'sale_order_id': self.sale_order_id.id,
            'name': self.name.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'nights': self.nights,
            'trn': self.trn,
            'note': self.note,
            'additional_note': self.additional_note,
            'special_rates': self.special_rates,
            'room_type_id': self.room_type_id.id,
            'room_category_id': self.room_category_id.id,
            'meal_id': self.meal_id.id,
            'status_id': self.status_id.id,
            'is_received_invoice': self.is_received_invoice,
            'invoice_date': None,
            'invoice_number': None,
            'pax': self.pax,
            'estimated_price': self.estimated_price,
            'actual_price': None,
            'sgl_room': self.sgl_room,
            'dbl_room': self.dbl_room,
            'trp_room': self.trp_room,
            'twin_room': self.twin_room,
            'oth_room': self.oth_room,
            'customer': self.customer,
            'partner_id': self.partner_id.id,
            'status_of_sale_order': self.status_of_sale_order,
            'per_pax': self.per_pax,
            'per_room': self.per_room,
            'per_person': self.per_person,
            'single_supp': self.single_supp,
            'third_person': self.third_person,
            'sgl_room_rate': self.sgl_room_rate,
            'dbl_room_rate': self.dbl_room_rate,
            'trp_room_rate': self.trp_room_rate,
            'currency_id': self.currency_id.id,
            'expense_type_id': None,
            'sgl_rate': self.sgl_rate,
            'dbl_rate': self.dbl_rate,
            'trp_rate': self.trp_rate,
            'twin_rate': self.twin_rate,
            'estimated_price': self.estimated_price,
            'is_received_invoice': False,
            'copy': 'copy',
        }

        self.env['hotels'].create(vals)

    def write(self, vals):
        vals['copy'] = 'no'
        result = super(Hotels, self).write(vals)
        return result

    @api.onchange('sgl_room', 'dbl_room', 'trp_room', 'twin_room')
    def onchange_room_pax(self):
        total_pax = 0
        if self.sgl_room > 0:
            total_pax += self.sgl_room * 1

        if self.dbl_room > 0:
            total_pax += self.dbl_room * 2

        if self.trp_room > 0:
            total_pax += self.trp_room * 3

        if self.twin_room > 0:
            total_pax += self.twin_room * 2

        self.pax = total_pax


class RoomType(models.Model):
    _name = 'room.types'
    _description = 'RoomType'

    name = fields.Char(string="Room Name")
    code = fields.Char(string="Room Code")
    pax = fields.Integer(string="# Pax")


class RoomCategory(models.Model):
    _name = 'room.category'
    _description = 'Room Category'

    name = fields.Char(string="Name")


class HotelMeals(models.Model):
    _name = 'hotel.meals'
    _description = 'Hotel Meals'

    name = fields.Char(string="Meal Code")


class Status(models.Model):
    _name = 'hotel.status'

    name = fields.Char(string="Status Code")
    status_name = fields.Char(string="Status Name")


class ProgramItinerary(models.Model):
    _name = 'itineraries'

    sale_order_id = fields.Many2one('sale.order', "SO")
    from_date = fields.Date(string="Date", required=True)
    days = fields.Char(compute='days_from_date', string="Day", store=True)
    name = fields.Char(string="Program")
    type_service_id = fields.Many2one('transportation.services', string="Type Of Service")
    guide_name_id = fields.Many2one('res.partner', string="Guide Name")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    show = fields.Boolean(string="Show", default=True)

    @api.depends('from_date')
    def days_from_date(self):
        for record in self:
            from_date = record.from_date
            if from_date:
                record.days = str(from_date.strftime("%A"))


class TransportationServices(models.Model):
    _name = 'transportation.services'

    name = fields.Char(string="Type of service")
    km = fields.Float(string="K.M")
    extra_mil = fields.Boolean(string="Extra Mileage")


class Restaurants(models.Model):
    _name = 'restaurants'
    _rec_name = 'name'

    sale_order_id = fields.Many2one('sale.order', "SO")
    name = fields.Many2one('res.partner', string="Restaurant Name")
    meal_id = fields.Many2one('restaurants.meals', string="Meals")
    note = fields.Text(string="Notes")
    special_rates = fields.Float(string="Special rates")
    pax = fields.Integer(string="Pax")
    estimated_price = fields.Float(string="Estimated price")
    actual_price = fields.Float(string="Actual price")
    date = fields.Date(string="Date", required=True, )
    status_id = fields.Many2one('hotel.status', string="Status")
    is_received_invoice = fields.Boolean(string="Received invoice", copy=False)
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Char(string="Invoice #")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    guide_id = fields.Many2one('guide', string="Guide")
    guide_id2 = fields.Many2one('res.partner', string="Guide")
    guide_ids = fields.Many2many('res.partner', string="Guides", compute='_get_guide_ids', store=True)
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    copy = fields.Char(string='copy', )
    additional_note = fields.Text(string="Add. Note")
    currency_id = fields.Many2one('res.currency', string="Currency")
    expense_type_id = fields.Many2one('expense.type', string="Expense Type")
    is_created_bill = fields.Boolean('Created Bill', default=False, copy=False)
    bill_id = fields.Many2one('account.move', string="bill id", copy=False)
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    show = fields.Boolean(string="Show", default=True)
    account_id = fields.Many2one('res.partner', string='Account', )
    guide_or_transportation = fields.Selection([
        ('guide', 'Guide'),
        ('transportation', 'Transportation'), ], string="Select From")
    deposit = fields.Float(string="Deposit")

    @api.onchange('guide_or_transportation')
    def _onchange_guide_or_transportation(self):
        if self.guide_or_transportation == 'guide':
            return {'domain': {'account_id': [('id', 'in', self.sale_order_id.guide_expense_ids.name.ids)]}}
        if self.guide_or_transportation == 'transportation':
            return {'domain': {'account_id': [('id', 'in', self.sale_order_id.transportation_expense_ids.name.ids)]}}
        else:
            return {'domain': {'account_id': [('id', 'in', [])]}}

    def fix_guide_ids(self):
        all_restaurant = self.env['restaurants'].search([])
        for record in all_restaurant:
            list_of_ids = []
            for guide in record.sale_order_id.guide_expense_ids:
                if record.date and guide.date_from and guide.date_to:
                    if record.date >= guide.date_from and record.date <= guide.date_to:
                        list_of_ids.append(guide.name.id)
            all_guide = self.env['res.partner'].browse(list_of_ids).ids
            record.guide_ids = all_guide

    @api.depends('sale_order_id', 'sale_order_id.guide_expense_ids', 'sale_order_id.guide_expense_ids.name', )
    def _get_guide_ids(self):

        for record in self:
            list_of_ids = []
            for guide in self.sale_order_id.guide_expense_ids:
                if record.date and guide.date_from and guide.date_to:
                    if record.date >= guide.date_from and record.date <= guide.date_to:
                        list_of_ids.append(guide.name.id)
                all_guide = self.env['res.partner'].browse(list_of_ids).ids
                record.guide_ids = all_guide

    def button_open_restaurant(self):
        self.is_received_invoice = False

    def button_close_restaurant(self):
        self.is_received_invoice = True

    def button_go_to_restaurant_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.bill_id.id,
            # 'name': self.employee_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }

    def button_create_restaurant_bill(self):
        vals = {
            'partner_id': self.name,
            'ref': self.invoice_number,
            'invoice_date': self.invoice_date,
            'payment_reference': self.sale_order_id.name,
            'date': self.date,
            'invoice_date_due': self.date,
            'move_type': 'in_invoice',
            'posted_before': False,
            'payment_state': 'not_paid',
            'ref': self.invoice_number,
            'invoice_line_ids': [
                {'product_id': self.product_id,
                 'is_sale_order': True,
                 'sale_order_id': self.sale_order_id,
                 'expense_type_id': self.expense_type_id,
                 'price_unit': self.actual_price,
                 }]

        }
        created_bill_id = self.env['account.move'].create(vals)
        self.is_created_bill = True
        self.bill_id = created_bill_id
        self.is_received_invoice = True

    @api.onchange('special_rates', 'pax')
    def _onchange_estimated_price(self):
        self.estimated_price = self.special_rates * self.pax

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s %s' % (rec.date, rec.name.name)))
        return res

    def duplicate_action(self):
        vals = {
            'sale_order_id': self.sale_order_id.id,
            'name': self.name.id,
            'meal_id': self.meal_id.id,
            'note': self.note,
            'special_rates': self.special_rates,
            'pax': self.pax,
            'estimated_price': self.estimated_price,
            'actual_price': self.actual_price,
            'date': self.date,
            'status_id': self.status_id.id,
            'is_received_invoice': self.is_received_invoice,
            'invoice_date': self.invoice_date,
            'invoice_number': self.invoice_number,
            'customer': self.customer,
            'partner_id': self.partner_id.id,
            'guide_id': self.guide_id.id,
            'status_of_sale_order': self.status_of_sale_order,
            'is_received_invoice': False,
            'copy': 'copy',
        }
        self.env['restaurants'].create(vals)

    def write(self, vals):
        vals['copy'] = 'no'
        result = super(Restaurants, self).write(vals)
        return result


class restaurantsMeals(models.Model):
    _name = 'restaurants.meals'
    _description = 'restaurants Meals'

    name = fields.Char(string="Meal")


class Transportation(models.Model):
    _name = 'transportation'

    sale_order_id = fields.Many2one('sale.order', "SO")
    name = fields.Many2one('res.partner', string="Transportation Company")
    vehicles_id = fields.Many2one('type.vehicles', string="Type of Vehicles")
    note = fields.Text(string="Notes")
    special_rates = fields.Float(string="Special rates")
    pax = fields.Integer(string="Pax")
    estimated_price = fields.Float(string="Estimated price")
    actual_price = fields.Float(string="Actual price")
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    status_id = fields.Many2one('hotel.status', string="Status")
    is_received_invoice = fields.Boolean(string="Received invoice", copy=False)
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Char(string="Invoice #")
    driver_name = fields.Char('Driver Name')
    driver_number = fields.Char('Driver Number')
    palte_number = fields.Char('Palte Number')
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    copy = fields.Char(string='copy', )
    additional_note = fields.Text(string="Add. Note")
    currency_id = fields.Many2one('res.currency', string="Currency")
    is_created_bill = fields.Boolean('Created Bill', default=False, copy=False)
    expense_type_id = fields.Many2one('expense.type', string="Expense Type")
    bill_id = fields.Many2one('account.move', string="bill id", copy=False)
    product_id = fields.Many2one('product.product', string='Product')
    show = fields.Boolean(string="Show", default=True)

    def button_create_transportation_bill(self):
        vals = {
            'partner_id': self.name,
            'ref': self.invoice_number,
            'invoice_date': self.invoice_date,
            'payment_reference': self.sale_order_id.name,
            'date': self.date_from,
            'invoice_date_due': self.date_from,
            'move_type': 'in_invoice',
            'posted_before': False,
            'payment_state': 'not_paid',
            'ref': self.invoice_number,
            'invoice_line_ids': [
                {'product_id': self.product_id,
                 'is_sale_order': True,
                 'sale_order_id': self.sale_order_id,
                 'expense_type_id': self.expense_type_id,
                 'price_unit': self.actual_price,
                 }]

        }
        created_bill_id = self.env['account.move'].create(vals)
        self.is_created_bill = True
        self.bill_id = created_bill_id
        self.is_received_invoice = True

    def button_go_to_transportation_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.bill_id.id,
            # 'name': self.employee_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }

    def button_open_transportation(self):
        self.is_received_invoice = False

    def button_close_transportation(self):
        self.is_received_invoice = True

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s %s' % (rec.date_from, rec.name.name)))
        return res

    def duplicate_action(self):
        vals = {
            'sale_order_id': self.sale_order_id.id,
            'name': self.name.id,
            'vehicles_id': self.vehicles_id.id,
            'note': self.note,
            'special_rates': self.special_rates,
            'pax': self.pax,
            'estimated_price': self.estimated_price,
            'actual_price': self.actual_price,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'status_id': self.status_id.id,
            'is_received_invoice': self.is_received_invoice,
            'invoice_date': self.invoice_date,
            'invoice_number': self.invoice_number,
            'driver_name': self.driver_name,
            'customer': self.customer,
            'partner_id': self.partner_id.id,
            'status_of_sale_order': self.status_of_sale_order,
            'is_received_invoice': False,
            'copy': 'copy'
        }
        self.env['transportation'].create(vals)

    def write(self, vals):
        vals['copy'] = 'no'
        result = super(Transportation, self).write(vals)
        return result


class TypeOfVehicles(models.Model):
    _name = 'type.vehicles'

    name = fields.Char(string="Vehicle")
    type = fields.Selection([('van', 'Van'),
                             ('car', 'Car'),
                             ('bus', 'Bus')], string="Vehicle Type")
    seats = fields.Integer(string="Seats")


class Guide(models.Model):
    _name = 'guide'
    _description = 'Guide'

    @api.depends('date_from', 'date_to')
    def compute_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                days = datetime.strptime(str(rec.date_to), "%Y-%m-%d") - datetime.strptime(str(rec.date_from),
                                                                                           "%Y-%m-%d")
                rec.days = days.days + 1
            else:
                rec.days = 0.0

    sale_order_id = fields.Many2one('sale.order', "SO")
    name = fields.Many2one('res.partner', string="Guide")
    guide_number = fields.Char(string="Phone / Mobile", compute="_compute_guide_number", store=True)
    language_id = fields.Many2one('guide.language', string="Language")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    days = fields.Float(string="Guide Fees Per Day", compute='compute_days', store=True)
    overnights = fields.Float(string="Overnights")
    note = fields.Text(string="Notes")
    special_rates = fields.Float(string="Special rates")
    status_id = fields.Many2one('hotel.status', string="Status")
    is_received_invoice = fields.Boolean(string="Received invoice", copy=False)
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Char(string="Invoice #")
    pax = fields.Integer(string="Pax")
    estimated_price = fields.Float(string="Estimated price")
    actual_price = fields.Float(string="Actual price")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    additional_note = fields.Text(string="Add. Note")
    guide_cost = fields.Float('cost')
    overnight_cost = fields.Float('cost')
    guide_total = fields.Float(' Total Guide Fess')
    overnight_total = fields.Float('Total Overnight ')
    is_created_bill = fields.Boolean('Created Bill', default=False, copy=False)
    expense_type_id = fields.Many2one('expense.type', string="Expense Type")
    bill_id = fields.Many2one('account.move', string="bill id", copy=False)
    product_id = fields.Many2one('product.product', string='Product', )
    show = fields.Boolean(string="Show", default=True)
    show_day = fields.Boolean(string="Show Guide Fees Per Day", default=True)
    copy = fields.Char(string='copy')

    def duplicate_action(self):
        vals = {
            'show': self.show,
            'sale_order_id': self.sale_order_id.id,
            'name': self.name.id,
            'guide_number': self.guide_number,
            'language_id': self.language_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'note': self.note,
            'additional_note': self.additional_note,
            'days': self.days,
            'overnights': self.overnights,
            'guide_cost': self.guide_cost,
            'overnight_cost': self.overnight_cost,
            'guide_total': self.guide_total,
            'overnight_total': self.overnight_total,
            'status_id': self.status_id.id,
            'is_received_invoice': self.is_received_invoice,
            'invoice_date': self.invoice_date,
            'invoice_number': self.invoice_number,
            'expense_type_id': self.expense_type_id.id,
            'estimated_price': self.estimated_price,
            'actual_price': self.actual_price,
            'product_id': self.product_id.id,
            'copy': 'copy',
        }

        self.env['guide'].create(vals)

    def write(self, vals):
        vals['copy'] = 'no'
        result = super(Guide, self).write(vals)
        return result

    def fix_guide_number(self):
        all_record_guide = self.env['guide'].search([])
        for record in all_record_guide:
            if record.name.phone and record.name.mobile:
                record.guide_number = record.name.phone + ' / ' + record.name.mobile
            elif record.name.phone:
                record.guide_number = record.name.phone
            elif record.name.mobile:
                record.guide_number = record.name.mobile

    @api.depends('name.mobile', 'name.phone')
    def _compute_guide_number(self):
        for record in self:
            if record.name.phone and record.name.mobile:
                record.guide_number = record.name.phone + ' / ' + record.name.mobile
            elif record.name.phone:
                record.guide_number = record.name.phone
            elif record.name.mobile:
                record.guide_number = record.name.mobile
            else:
                record.guide_number = None

    def button_create_guide_bill(self):
        vals = {
            'partner_id': self.name,
            'ref': self.invoice_number,
            'invoice_date': self.invoice_date,
            'payment_reference': self.sale_order_id.name,
            'date': self.date_from,
            'invoice_date_due': self.date_from,
            'move_type': 'in_invoice',
            'posted_before': False,
            'payment_state': 'not_paid',
            'ref': self.invoice_number,
            'invoice_line_ids': [
                {'product_id': self.product_id,
                 'is_sale_order': True,
                 'sale_order_id': self.sale_order_id,
                 'expense_type_id': self.expense_type_id,
                 'price_unit': self.actual_price,
                 }]

        }
        created_bill_id = self.env['account.move'].create(vals)
        self.is_created_bill = True
        self.bill_id = created_bill_id
        self.is_received_invoice = True

    def button_go_to_guide_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.bill_id.id,
            # 'name': self.employee_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }

    def button_open_guide(self):
        self.is_received_invoice = False

    def button_close_guide(self):
        self.is_received_invoice = True

    @api.onchange('guide_total', 'overnight_total')
    def _onchange_estimate_price(self):
        self.estimated_price = self.guide_total + self.overnight_total

    @api.onchange('guide_cost', 'days')
    def _onchange_guide_total(self):
        self.guide_total = self.guide_cost * self.days

    @api.onchange('overnight_cost', 'overnights')
    def _onchange_overnight_total(self):
        self.overnight_total = self.overnights * self.overnight_cost

    # @api.onchange('name')
    # def onchange_name(self):
    #     if self.name:
    #         self.number = self.name.mobile
    #     else:
    #         self.number = False


class Clients(models.Model):
    _name = 'clients'

    sale_order_id = fields.Many2one('sale.order', "SO")
    show = fields.Boolean(string="Show", default=True)
    name = fields.Char(string="Name")
    age = fields.Selection([('ADT', 'ADT'), ('CHD', 'CHD'), ('INF.', 'INF.')], string="Age")
    room_type_id = fields.Many2one('room.types', string="Room Type")
    rn = fields.Integer(string="Room#")
    note = fields.Text(string="Comments")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    select = fields.Boolean(string='select', default="True")


class ClientsPassport(models.Model):
    _name = 'clients.passport'

    sale_order_id = fields.Many2one('sale.order', "SO")
    show = fields.Boolean(string="Show", default=True)
    name = fields.Char(string="Name")
    passport_number = fields.Char(string="Passport#")
    birth_date = fields.Date(string="Birth Date")
    issue_date = fields.Date(string="Issue Date")
    expiry_date = fields.Date(string="Expiry Date")
    nationality_id = fields.Many2one('res.country', string="Nationality")
    note = fields.Text(string="Comments")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    select = fields.Boolean(string='select', default="True")


class Entrance(models.Model):
    _name = 'entrance'

    # @api.model
    # def _getPartnerId(self):
    #     print(self.env.context.get('active_ids'))
    #     my_self = self.env['entrance'].search([],limit=1)
    #     partner_ids = my_self.sale_order_id.transportation_expense_ids.name + my_self.sale_order_id.guide_expense_ids.name
    #     print(partner_ids.ids)
    #     return [('account_id', 'in', partner_ids.ids)]

    sale_order_id = fields.Many2one('sale.order', "SO")
    name = fields.Many2one('entrances.type', string="Entrance name")
    date = fields.Date(string="Date")
    child = fields.Integer(string="Child", )
    adult = fields.Integer(string="Adult", )
    note = fields.Text(string="Notes")
    rate = fields.Float(string="Rate")
    is_received_invoice = fields.Boolean(string="Received invoice")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Char(string="Invoice #")
    estimated_price = fields.Float(string="Estimated price")
    actual_price = fields.Float(string="Actual price")
    cheke_availability_note = fields.Char("Cheke Availability")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    copy = fields.Char(string='copy', )
    adult_cost = fields.Float(string='Adult Cost')
    child_cost = fields.Float(string='Child Cost')
    currency_id = fields.Many2one('res.currency', string='Currency')
    total = fields.Float(string='Total Cost', readonly=True)
    account_id = fields.Many2one('res.partner', string='Account', )
    show = fields.Boolean(string="Show", default=True)
    guide_or_transportation = fields.Selection([
        ('guide', 'Guide'),
        ('transportation', 'Transportation'), ], string="Select From")
    deposit = fields.Float("Deposit")
    number_of_jeep = fields.Integer("Number Of Jeep")

    @api.onchange('adult', 'child')
    def _get_number_of_jeep(self):
        for rec in self:
            rec.number_of_jeep = (rec.adult + rec.child) / 6

    def button_open_entrance(self):
        self.is_received_invoice = False

    def button_close_entrance(self):
        self.is_received_invoice = True

    @api.onchange('guide_or_transportation')
    def _onchange_guide_or_transportation(self):
        if self.guide_or_transportation == 'guide':
            return {'domain': {'account_id': [('id', 'in', self.sale_order_id.guide_expense_ids.name.ids)]}}
        if self.guide_or_transportation == 'transportation':
            return {'domain': {'account_id': [('id', 'in', self.sale_order_id.transportation_expense_ids.name.ids)]}}
        else:
            return {'domain': {'account_id': [('id', 'in', [])]}}

    @api.onchange('total')
    def _get_estimated_price(self):
        self.estimated_price = self.total

    @api.onchange('adult', 'adult_cost', 'child', 'child_cost')
    def _get_total(self):
        for rec in self:
            rec.total = (rec.adult * rec.adult_cost) + (rec.child * rec.child_cost)

    @api.onchange('name')
    def _get_adult_cost_and_child_cost(self):
        for rec in self:
            rec.adult_cost = rec.name.adult
            rec.child_cost = rec.name.child

    def duplicate_action(self):
        vals = {
            'sale_order_id': self.sale_order_id.id,
            'name': self.name.id,
            'date': self.date,
            'child': self.child,
            'adult': self.adult,
            'note': self.note,
            'rate': self.rate,
            'is_received_invoice': self.is_received_invoice,
            'invoice_date': self.invoice_date,
            'invoice_number': self.invoice_number,
            'estimated_price': self.estimated_price,
            'actual_price': self.actual_price,
            'cheke_availability_note': self.cheke_availability_note,
            'customer': self.customer,
            'partner_id': self.partner_id.id,
            'status_of_sale_order': self.status_of_sale_order,
            'adult_cost': self.adult_cost,
            'child_cost': self.child_cost,
            'total': self.total,
            'is_received_invoice': False,
            'copy': 'copy'
        }
        self.env['entrance'].create(vals)

    def write(self, vals):
        vals['copy'] = 'no'
        result = super(Entrance, self).write(vals)
        return result

    def cheke_availability(self):
        if not self.name or not self.date:
            raise UserError(
                _("Please set Eniftrance name and date.")
            )
        else:
            name_of_day = datetime.strptime(str(self.date), "%Y-%m-%d").strftime("%a").lower()
            print(name_of_day)
            if name_of_day == 'mon':
                if not self.name.mon:
                    self.date = False
                    print(self.date)
                    self.cheke_availability_note = "Sorry the place is closed at this day."

                else:
                    self.cheke_availability_note = "the place is open at this day."

            if name_of_day == 'tue':
                if not self.name.tue:
                    self.date = False
                    print(self.date)
                    self.cheke_availability_note = "Sorry the place is closed at this day."
                else:
                    self.cheke_availability_note = "the place is open at this day."

            if name_of_day == 'wed':
                if not self.name.wed:
                    self.date = False
                    print(self.date)
                    self.cheke_availability_note = "Sorry the place is closed at this day."
                else:
                    self.cheke_availability_note = "the place is open at this day."

            if name_of_day == 'thu':
                if not self.name.thu:
                    self.date = False
                    print(self.date)
                    self.cheke_availability_note = "Sorry the place is closed at this day."
                else:
                    self.cheke_availability_note = "the place is open at this day."

            if name_of_day == 'fri':
                if not self.name.fri:
                    self.date = False
                    print(self.date)
                    self.cheke_availability_note = "Sorry the place is closed at this day."
                else:
                    self.cheke_availability_note = "the place is open at this day."

            if name_of_day == 'sat':
                if not self.name.sat:
                    self.date = False
                    print(self.date)
                    self.cheke_availability_note = "Sorry the place is closed at this day."
                else:
                    self.cheke_availability_note = "the place is open at this day."

            if name_of_day == 'sun':
                if not self.name.sun:
                    self.date = False
                    print(self.date)
                    self.cheke_availability_note = "Sorry the place is closed at this day."
                else:
                    self.cheke_availability_note = "the place is open at this day."

            self.rate = (self.adult * self.name.adult) + (self.child * self.name.child)


class Entrances(models.Model):
    _name = 'entrances.type'

    name = fields.Char(string="Location Name")
    city_id = fields.Many2one('cities', string="City")
    adult = fields.Float(string="Adult Rate")
    child = fields.Float(string="Child Rate")
    mon = fields.Boolean(string="Mon")
    tue = fields.Boolean(string="Tue")
    wed = fields.Boolean(string="Wed")
    thu = fields.Boolean(string="Thu")
    fri = fields.Boolean(string="Fri")
    sat = fields.Boolean(string="Sat")
    sun = fields.Boolean(string="Sun")
    open_hurs = fields.Char(string="Opening Hours")
    is_jeep = fields.Boolean(string="Is Jeep")


class Cities(models.Model):
    _name = 'cities'

    name = fields.Char(string="City Name")
    code = fields.Text(string="City Code")
    country_id = fields.Many2one('res.country', string="Country")


class Extra(models.Model):
    _name = 'extras'
    _description = 'Extras'

    sale_order_id = fields.Many2one('sale.order', "SO")
    name = fields.Many2one('expense.type', string="Services name")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    date = fields.Date(string="Date")
    pax = fields.Integer(string="Pax")
    child = fields.Integer(string="Child")
    adult = fields.Integer(string="Adult")
    note = fields.Text(string="Notes")
    is_received_invoice = fields.Boolean(string="Received invoice")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Char(string="Invoice #")
    estimated_price = fields.Float(string="Estimated price")
    actual_price = fields.Float(string="Actual price")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")
    status_of_sale_order = fields.Selection('sale.order', related='sale_order_id.state')
    copy = fields.Char(string='copy', )
    currency_id = fields.Many2one('res.currency', string='Currency')
    adult_rate = fields.Float(string="Adult Rate")
    child_rate = fields.Float(string="Child Rate")
    total = fields.Float(string="Total Cost", readonly=True)
    account_id = fields.Many2one('res.partner', string='Account', )
    show = fields.Boolean(string="Show", default=True)
    guide_or_transportation = fields.Selection([
        ('guide', 'Guide'),
        ('transportation', 'Transportation'), ], string="Select From")
    is_created_bill = fields.Boolean('Created Bill', default=False, copy=False)
    bill_id = fields.Many2one('account.move', string="bill id", copy=False)
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict', copy=False)
    expense_type_id = fields.Many2one('expense.type', string="Expense Type", copy=False)

    def button_open_extras(self):
        self.is_received_invoice = False

    def button_close_extras(self):
        self.is_received_invoice = True

    def button_go_to_extras_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.bill_id.id,
            # 'name': self.employee_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }

    def button_create_extras_bill(self):
        vals = {
            'partner_id': self.supplier_id.id,
            'ref': self.invoice_number,
            'invoice_date': self.invoice_date,
            'payment_reference': self.sale_order_id.name,
            'date': self.date,
            'invoice_date_due': self.date,
            'move_type': 'in_invoice',
            'posted_before': False,
            'payment_state': 'not_paid',
            'ref': self.invoice_number,
            'invoice_line_ids': [
                {'product_id': self.product_id,
                 'is_sale_order': True,
                 'sale_order_id': self.sale_order_id,
                 'expense_type_id': self.expense_type_id,
                 'price_unit': self.actual_price,
                 }]

        }
        created_bill_id = self.env['account.move'].create(vals)
        self.is_created_bill = True
        self.bill_id = created_bill_id
        self.is_received_invoice = True

    @api.onchange('guide_or_transportation')
    def _onchange_guide_or_transportation(self):
        if self.guide_or_transportation == 'guide':
            return {'domain': {'account_id': [('id', 'in', self.sale_order_id.guide_expense_ids.name.ids)]}}
        if self.guide_or_transportation == 'transportation':
            return {'domain': {'account_id': [('id', 'in', self.sale_order_id.transportation_expense_ids.name.ids)]}}
        else:
            return {'domain': {'account_id': [('id', 'in', [])]}}

    @api.onchange('total')
    def _get_estimated_price(self):
        self.estimated_price = self.total

    @api.onchange('adult', 'adult_rate', 'child', 'child_rate')
    def _get_total(self):
        for rec in self:
            rec.total = (rec.adult * rec.adult_rate) + (rec.child * rec.child_rate)

    def duplicate_action(self):
        vals = {
            'sale_order_id': self.sale_order_id.id,
            'name': self.name.id,
            'supplier_id': self.supplier_id.id,
            'date': self.date,
            'pax': self.pax,
            'child': self.child,
            'adult': self.adult,
            'adult_rate': self.adult_rate,
            'child_rate': self.child_rate,
            'total': self.total,
            'note': self.note,
            'is_received_invoice': self.is_received_invoice,
            'invoice_date': self.invoice_date,
            'invoice_number': self.invoice_number,
            'estimated_price': self.estimated_price,
            'actual_price': self.actual_price,
            'customer': self.customer,
            'partner_id': self.partner_id.id,
            'status_of_sale_order': self.status_of_sale_order,
            'is_received_invoice': False,
            'copy': 'copy',
        }
        self.env['extras'].create(vals)

    def write(self, vals):
        vals['copy'] = 'no'
        result = super(Extra, self).write(vals)
        return result


class Inclusions(models.Model):
    _name = 'inclusions'

    sale_order_id = fields.Many2one('sale.order', "SO")
    name = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Yes / No")
    inclusion_id = fields.Many2one('inclusion', string="Inclusions")
    customer = fields.Char(related='sale_order_id.customer')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id', string="Agent")


class Inclusion(models.Model):
    _name = 'inclusion'

    name = fields.Char(string="Name")


class GuideLanguage(models.Model):
    _name = 'guide.language'

    name = fields.Char(string="Name")


class Revenue(models.Model):
    _name = 'sales.revenue'

    sale_order_id = fields.Many2one('sale.order', string='SO')
    label = fields.Char('Label')
    amount = fields.Float('Amount', digits=(12, 3))


class Details(models.Model):
    _name = 'details'
    sale_order_id = fields.Many2one('sale.order', string="sale order id")
    date = fields.Date(string="Date")
    details = fields.Char('Details')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        pass

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        if self.product_id.name == 'FOC policy' or self.product_id.name == 'Discount':
            if self.price_unit > 0:
                self.price_unit = self.price_unit * -1
            else:
                self.price_unit = self.price_unit * 1
