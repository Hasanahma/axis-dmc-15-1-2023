from odoo import fields, models, api


class SaleCustomReportWizard(models.TransientModel):
    _name = "profit.loss.report.wizard"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    date_filter = fields.Selection(
        [("order", "Order Date"), ("arrival", "Arrival Date"), ("departure", "Departure Date")], string="Date Filter",
        default='order')
    agent_id = fields.Many2one('res.partner', string='Agent')
    currency = fields.Selection([('JOD', 'JOD'), ('USD', 'USD')], string='Currency', default='JOD', required=True)
    currency_rate = fields.Float('Converging Rate', default=1.41)
    show_file = fields.Selection(
        [("show_cancel_file", "Show Cancel File"), ("do_not_show_cancel_file", "Don't Show Cancel File"),
         ("both", "Both")], string="Show",
        default='both')

    def button_print_report(self):
        revenue_lines = []
        if self.sale_order_id:
            for revenue in self.sale_order_id.revenue_ids:
                revenue_lines.append({
                    'label': revenue.label,
                    'amount': revenue.amount
                })
            order_dic = self.sale_order_id.read(['state', 'name', 'partner_id', 'customer', 'cost_status', 'actual_expense_total', 'invoiced_amount', 'profit_loss', 'net_profit_margin'])
            move_ids = self.sale_order_id.mapped('order_line.invoice_lines.move_id')

            payment_states = []
            for move in move_ids:
                payment_states.append(move.payment_state)

            if payment_states.__contains__('paid') and ['not_paid', 'partial'] not in payment_states:
                res_status = 'Paid'
            elif ['paid', 'not_paid'] in payment_states or ['paid', 'partial'] in payment_states:
                res_status = 'Partially Paid'
            else:
                res_status = "Not Paid"

            order_dic[0]['payment_state'] = res_status
        else:
            order_dic = []
            if self.date_filter == 'order':
                search_filter = [('date_order', '>=', self.from_date), ('date_order', '<=', self.to_date)]
            elif self.date_filter == "arrival":
                search_filter = [('arrival_date', '>=', self.from_date), ('arrival_date', '<=', self.to_date)]
            else:
                search_filter = [('departure_date', '>=', self.from_date), ('departure_date', '<=', self.to_date)]

            if self.agent_id:
                search_filter.append(('partner_id', '=', self.agent_id.id))
            if self.show_file == 'show_cancel_file':
                search_filter.append(('state', '=', 'cancel'))
            if self.show_file == 'do_not_show_cancel_file':
                search_filter.append(('state', '!=', 'cancel'))
            if self.show_file == 'both':
                pass

            orders = self.env['sale.order'].search(search_filter)

            for order in orders:
                order_obj = order.read(['state', 'name', 'partner_id', 'customer', 'cost_status', 'actual_expense_total', 'invoiced_amount', 'profit_loss', 'profit_loss', 'net_profit_margin'])
                move_ids = order.mapped('order_line.invoice_lines.move_id')

                payment_states = []
                for move in move_ids:
                    payment_states.append(move.payment_state)

                if payment_states.__contains__('paid') and ['not_paid', 'partial'] not in payment_states:
                    res_status = 'Paid'
                elif ['paid', 'not_paid'] in payment_states or ['paid', 'partial'] in payment_states:
                    res_status = 'Partially Paid'
                else:
                    res_status = "Not Paid"


                order_obj[0]['payment_state'] = res_status
                order_dic.append(*order_obj)

        data = {
            'form': self.read(),
            'orders': order_dic,
            'invoice_lines': revenue_lines,
            'cost_lines': self.sale_order_id.actual_expense_ids.read(['name', 'move_name', 'expense_type_id', 'debit'])
        }


        return self.env.ref("invoice_custom.action_report_axis_profit_loss").report_action(self, data=data)


