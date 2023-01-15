from odoo import fields, models, api
from itertools import groupby
import logging

_logger = logging.getLogger(__name__)


class ConfirmationLetterWizard(models.TransientModel):
    _name = "expenses.sheet.wizard"

    deposit = fields.Float(string="Deposit")
    is_locked = fields.Boolean(string="is locked")
    account_id = fields.Many2one('res.partner', string='Account')
    guide_or_transportation = fields.Selection([
        ('guide', 'Guide'),
        ('transportation', 'Transportation'), ], string="Select From")

    def _get_default_itinerary(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.itineraries_expense_ids:
            return True
        else:
            return False

    def button_print_expenses_sheet(self):

        sale_order_id = self.env.context.get('active_id')

        data = {
            'sale_order_id': sale_order_id,

        }
        report_action = self.env.ref('invoice_custom.expenses_reservation_form_report_view').report_action(self,
                                                                                                           data=data)
        report_action['close_on_report_download'] = True
        return report_action

    @api.onchange('guide_or_transportation')
    def _onchange_guide_or_transportation(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if self.guide_or_transportation == 'guide':
            return {'domain': {'account_id': [('id', 'in', object_sale_order.guide_expense_ids.name.ids)]}}
        if self.guide_or_transportation == 'transportation':
            return {'domain': {'account_id': [('id', 'in', object_sale_order.transportation_expense_ids.name.ids)]}}
        else:
            return {'domain': {'account_id': [('id', 'in', [])]}}

    def button_close_expenses_sheet(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        _logger.info('Get Sale Order ID')
        # make entrance locked
        for entrance_record in object_sale_order.entrance_expense_ids:
            if entrance_record.is_received_invoice != True:
                entrance_record.button_close_entrance()
        # make extras locked
        for extra_record in object_sale_order.extras_expense_ids:
            if extra_record.is_received_invoice != True:
                extra_record.button_close_extras()
        # make guide locked
        for guide_record in object_sale_order.guide_expense_ids:
            if guide_record.is_received_invoice != True:
                guide_record.button_close_guide()
        # make transportation locked
        for transportation_record in object_sale_order.transportation_expense_ids:
            if transportation_record.is_received_invoice != True:
                transportation_record.button_close_transportation()
        # make restaurant locked
        for restaurant_record in object_sale_order.resturnats_expense_ids:
            if restaurant_record.is_received_invoice != True:
                restaurant_record.button_close_restaurant()
        # print the report after locked
        data = {
            'sale_order_id': sale_order_id,
        }
        report_action = self.env.ref('invoice_custom.expenses_reservation_form_report_view').report_action(self,
                                                                                                           data=data)
        report_action['close_on_report_download'] = True
        return report_action


class ReportBomStructure(models.AbstractModel):
    _name = 'report.invoice_custom.actual_guide_expense_sheet'
    _description = 'Expenses Reservation Form Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # itineraries_expense_ids = self.env['itineraries'].search([('id', '=',)])
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        object_expenses_sheet_wizard = self.env['expenses.sheet.wizard'].search([])[-1]
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            # 'itineraries_expense_ids': itineraries_expense_ids,
            'sale_order_id': object_sale_order,
            'object_expenses_sheet_wizard': object_expenses_sheet_wizard,
        }
