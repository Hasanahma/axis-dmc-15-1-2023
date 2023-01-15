from odoo import fields, models, api


class HotelBillWizard(models.TransientModel):
    _name = "hotel.bill.wizard"

    def _get_some_default(self):
        parent_id = self.env.context.get('active_id')
        parent_model = self.env['res.partner'].browse(int(self.env['hotels'].browse(parent_id).name))
        default_value = parent_model
        print(default_value)
        return default_value

    name_of_hotel = fields.Many2one('res.partner', string="Name Of Hotel", default=_get_some_default, readonly=True)
    hotel_ids = fields.Many2many('hotels')

    def button_create_hotel_bill(self):
        list_of_date_from = []
        for hotel_id in self.hotel_ids:
            list_of_date_from.append(hotel_id.date_from)
        if self.hotel_ids.filtered(lambda l: l.date_from == min(list_of_date_from)):
            hotel_id_with_minimum_date = self.hotel_ids.filtered(lambda l: l.date_from == min(list_of_date_from))[0]


        invoice_line_ids_list = []
        for hotel_id in self.hotel_ids:
            invoice_line_ids_list.append(
                {'product_id': hotel_id.product_id,
                 'is_sale_order': True,
                 'sale_order_id': hotel_id.sale_order_id,
                 'expense_type_id': hotel_id.expense_type_id,
                 'price_unit': hotel_id.actual_price,
                 }
            )

        vals = {
            'partner_id': hotel_id_with_minimum_date.name,
            'ref': hotel_id_with_minimum_date.invoice_number,
            'invoice_date': hotel_id_with_minimum_date.invoice_date,
            'payment_reference': hotel_id_with_minimum_date.sale_order_id.name,
            'date': hotel_id_with_minimum_date.date_from,
            'invoice_date_due': hotel_id_with_minimum_date.date_from,
            'move_type': 'in_invoice',
            'posted_before': False,
            'payment_state': 'not_paid',
            'ref': hotel_id_with_minimum_date.invoice_number,
            'invoice_line_ids': invoice_line_ids_list

        }
        created_bill_id = self.env['account.move'].create(vals)
        for hotel_id in self.hotel_ids:
            hotel_id.is_created_bill = True
            hotel_id.bill_id = created_bill_id
            hotel_id.is_received_invoice = True

    @api.onchange('name_of_hotel')
    def onchange_name_of_hotel(self):
        parent_id = self.env.context.get('active_id')
        default_value = int(self.env['hotels'].browse(parent_id).sale_order_id)
        for rec in self:
            return {
                'domain': {'hotel_ids': [('sale_order_id', '=', default_value), ('name', '=', rec.name_of_hotel.id)]}}