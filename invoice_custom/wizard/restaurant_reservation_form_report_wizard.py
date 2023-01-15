from odoo import fields, models, api


class RestaurantReservationFormReportWizard(models.TransientModel):
    _name = "restaurant.reservation.form.report.wizard"

    def _get_restaurant_default(self):
        parent_id = self.env.context.get('active_id')
        parent_model = self.env['res.partner'].browse(int(self.env['restaurants'].browse(parent_id).name))
        default_value = parent_model.id

        return default_value


    name_of_restaurant = fields.Many2one('res.partner', string="Name Of Restaurant", default=_get_restaurant_default, readonly=True)
    show_reservation = fields.Boolean(string="Restaurant Reservation", required=True)
    show_voucher = fields.Boolean(string="Restaurant Voucher",  required=True)
    show_note = fields.Boolean(string="Show Note")
    show_add_note = fields.Boolean(string="Show ADD. Note")
    restaurant_ids = fields.Many2many('restaurants')

    @api.onchange('name_of_restaurant')
    def onchange_name_of_restaurant(self):
        parent_id = self.env.context.get('active_id')
        default_value = int(self.env['restaurants'].browse(parent_id).sale_order_id)
        for rec in self:
            return {'domain': {'restaurant_ids': [('sale_order_id', '=', default_value), ('name', '=', rec.name_of_restaurant.id)]}}

    def button_print_restaurant_reservation_form(self):
        # get id of restaurant
        id_of_restaurant = self.env.context.get('active_id')
        # get id of sale order
        id_of_sale_order = int(self.env['hotels'].search([('id','=',id_of_restaurant)]).sale_order_id)
        # get data of sale order
        sale_order_id = self.env['sale.order'].search_read([('id','=',id_of_sale_order)])
        data = {
            'restaurant_ids': self.restaurant_ids.read(),
            'sale_order_id': sale_order_id,
            'selected_restaurants': self.restaurant_ids.read(),
            'selected_show_reservation': self.show_reservation,
            'selected_show_voucher': self.show_voucher,
            'show_note': self.show_note,
            'show_add_note': self.show_add_note,
        }

        report_action = self.env.ref('invoice_custom.action_restaurant_reservation_form_report').report_action(self, data=data)
        report_action['close_on_report_download'] = True
        return report_action



class ReportRestaurant(models.AbstractModel):
    _name = 'report.invoice_custom.restaurant_reservation_form_report_view'
    _description = 'restaurant Reservation Form Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # get id of hotel
        id_of_restaurant = self.env.context.get('active_id')
        # get data of hotel (object)
        restaurants_id = self.env['restaurants'].search([('id', '=', id_of_restaurant)])
        # get id of sale order
        id_of_sale_order = int(self.env['restaurants'].search([('id', '=', id_of_restaurant)]).sale_order_id)
        # get data of sale order (object)
        sale_order_id = self.env['sale.order'].search([('id', '=', id_of_sale_order)])
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'restaurants_id': restaurants_id,
            'sale_order_id': sale_order_id,
        }
