from odoo import fields, models, api


class TransportationReservationFormReportWizard(models.TransientModel):
    _name = "transportation.reservation.form"

    def _get_transportation_default(self):
        parent_id = self.env.context.get('active_id')
        parent_model = self.env['res.partner'].browse(int(self.env['transportation'].browse(parent_id).name))
        default_value = parent_model.id

        return default_value

    name_of_transportation = fields.Many2one('res.partner', string="Name Of Transportation", default=_get_transportation_default, readonly=True)
    show_reservation = fields.Boolean(string="Transportation Reservation", required=True)
    show_voucher = fields.Boolean(string="Transportation Voucher",  required=True)
    show_note = fields.Boolean(string="Show Note")
    show_add_note = fields.Boolean(string="Show ADD. Note")
    transportation_ids = fields.Many2many('transportation',)

    @api.onchange('name_of_transportation')
    def onchange_name_of_transportation(self):
        parent_id = self.env.context.get('active_id')
        default_value = int(self.env['transportation'].browse(parent_id).sale_order_id)
        for rec in self:
            print(rec.name_of_transportation)
            return {'domain': {'transportation_ids': [('sale_order_id', '=', default_value), ('name', '=', rec.name_of_transportation.id)]}}

    def button_print_transportation_reservation_form(self):
        # get id of restaurant
        id_of_transportation = self.env.context.get('active_id')
        print(id_of_transportation)
        # get id of sale order
        id_of_sale_order = int(self.env['transportation'].search([('id','=',id_of_transportation)]).sale_order_id)
        # get data of sale order
        sale_order_id = self.env['sale.order'].search_read([('id','=',id_of_sale_order)])
        # print('id_of_transportation',id_of_transportation,'id_of_sale_order',id_of_sale_order,'sale_order_id'.sale_order_id)
        data = {
            'transportation_ids': self.transportation_ids.read(),
            'sale_order_id': sale_order_id,
            'selected_transportation': self.transportation_ids.read(),
            'selected_show_reservation': self.show_reservation,
            'selected_show_voucher': self.show_voucher,
            'show_note': self.show_note,
            'show_add_note': self.show_add_note,
        }

        report_action = self.env.ref('invoice_custom.action_transportation_reservation_form_report').report_action(self, data=data)
        report_action['close_on_report_download'] = True
        return report_action



class ReportTransportation(models.AbstractModel):
    _name = 'report.invoice_custom.transportation_reservation_view'
    _description = 'transportation Reservation Form Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # get id of hotel
        id_of_transportation = self.env.context.get('active_id')
        # get data of hotel (object)
        transportations_id = self.env['transportation'].search([('id', '=', id_of_transportation)])
        # get id of sale order
        id_of_sale_order = int(self.env['transportation'].search([('id', '=', id_of_transportation)]).sale_order_id)
        # get data of sale order (object)
        sale_order_id = self.env['sale.order'].search([('id', '=', id_of_sale_order)])
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'transportations_id': transportations_id,
            'sale_order_id': sale_order_id,
        }
