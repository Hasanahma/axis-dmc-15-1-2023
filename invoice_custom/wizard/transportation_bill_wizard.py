from odoo import fields, models, api


class HotelBillWizard(models.TransientModel):
    _name = "transportation.bill.wizard"

    def _get_some_default(self):
        parent_id = self.env.context.get('active_id')
        parent_model = self.env['res.partner'].browse(int(self.env['transportation'].browse(parent_id).name))
        default_value = parent_model
        return default_value

    name_of_transportation = fields.Many2one('res.partner', string="Name Of Hotel", default=_get_some_default, readonly=True)
    transportation_ids = fields.Many2many('transportation')

    def button_create_transportation_bill(self):
        list_of_date_from = []
        for transportation_id in self.transportation_ids:
            list_of_date_from.append(transportation_id.date_from)
        if self.transportation_ids.filtered(lambda l: l.date_from == min(list_of_date_from)):
            transportation_id_with_minimum_date = self.transportation_ids.filtered(lambda l: l.date_from == min(list_of_date_from))[0]


        invoice_line_ids_list = []
        for transportation_id in self.transportation_ids:
            invoice_line_ids_list.append(
                {'product_id': transportation_id.product_id,
                 'is_sale_order': True,
                 'sale_order_id': transportation_id.sale_order_id,
                 'expense_type_id': transportation_id.expense_type_id,
                 'price_unit': transportation_id.actual_price,
                 }
            )

        vals = {
            'partner_id': transportation_id_with_minimum_date.name,
            'ref': transportation_id_with_minimum_date.invoice_number,
            'invoice_date': transportation_id_with_minimum_date.invoice_date,
            'payment_reference': transportation_id_with_minimum_date.sale_order_id.name,
            'date': transportation_id_with_minimum_date.date_from,
            'invoice_date_due': transportation_id_with_minimum_date.date_from,
            'move_type': 'in_invoice',
            'posted_before': False,
            'payment_state': 'not_paid',
            'ref': transportation_id_with_minimum_date.invoice_number,
            'invoice_line_ids': invoice_line_ids_list

        }
        created_bill_id = self.env['account.move'].create(vals)
        for transportation_id in self.transportation_ids:
            transportation_id.is_created_bill = True
            transportation_id.bill_id = created_bill_id
            transportation_id.is_received_invoice = True

    @api.onchange('name_of_transportation')
    def onchange_name_of_transportation(self):
        parent_id = self.env.context.get('active_id')
        default_value = int(self.env['transportation'].browse(parent_id).sale_order_id)
        for rec in self:
            return {
                'domain': {'transportation_ids': [('sale_order_id', '=', default_value), ('name', '=', rec.name_of_transportation.id)]}}