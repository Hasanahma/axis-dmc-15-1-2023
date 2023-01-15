from odoo import fields, models, api, _
from itertools import groupby


class HotelReservationFormReportWizard(models.TransientModel):
    _name = "hotel.reservation.form.report.wizard"

    def _get_some_default(self):
        parent_id = self.env.context.get('active_id')
        parent_model = self.env['res.partner'].browse(int(self.env['hotels'].browse(parent_id).name))
        default_value = parent_model
        print(default_value)
        return default_value

    def _get_default_sale_order(self):
        hotel_id = self.env.context.get('active_id')
        hotel_object = self.env['hotels'].browse(hotel_id)
        object_sale_order = hotel_object.sale_order_id
        return object_sale_order

    def _get_default_email_from(self):
        return self.env.user

    name_of_hotel = fields.Many2one('res.partner', string="Name Of Hotel", default=_get_some_default, readonly=True)
    show_reservation = fields.Boolean(string="Hotel Reservation", required=True)
    show_voucher = fields.Boolean(string="Hotel Voucher", required=True)
    show_note = fields.Boolean(string="Show Note")
    show_add_note = fields.Boolean(string="Show ADD. Note")
    show_client = fields.Boolean(string="Show Client")
    hotel_ids = fields.Many2many('hotels')
    object_sale_order = fields.Many2one('sale.order', string="Sale Order Id", default=_get_default_sale_order)
    email_from = fields.Many2one('res.users', string='Email From', default=_get_default_email_from)

    @api.onchange('name_of_hotel')
    def onchange_name_of_hotel(self):
        parent_id = self.env.context.get('active_id')
        default_value = int(self.env['hotels'].browse(parent_id).sale_order_id)
        for rec in self:
            return {
                'domain': {'hotel_ids': [('sale_order_id', '=', default_value), ('name', '=', rec.name_of_hotel.id)]}}

    def button_print_hotel_reservation_form(self):
        # get id of hotel
        id_of_hotel = self.env.context.get('active_id')
        # get id of sale order
        id_of_sale_order = int(self.env['hotels'].search([('id', '=', id_of_hotel)]).sale_order_id)
        # get data of sale order
        sale_order_id = self.env['sale.order'].search_read([('id', '=', id_of_sale_order)])
        data = {
            'hotel_ids': self.hotel_ids.read(),
            'sale_order_id': sale_order_id,
            'selected_hotels': self.hotel_ids.read(),
            'selected_show_reservation': self.show_reservation,
            'selected_show_voucher': self.show_voucher,
            'show_note': self.show_note,
            'show_add_note': self.show_add_note,
            'show_client': self.show_client,
        }

        report_action = self.env.ref('invoice_custom.action_hotel_reservation_form_report').report_action(self,
                                                                                                          data=data)
        report_action['close_on_report_download'] = True
        return report_action


    def button_send_email_hotels(self):
        template_id = self.env.ref('invoice_custom.hotel_email').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        sale_order_id = self.env['hotel.reservation.form.report.wizard'].search([])[-1].object_sale_order
        INFO = self.env['clients'].search_read([('sale_order_id', '=', sale_order_id.id)])
        list2 = []
        for i in INFO:
            i['rn_room_type'] = str(i['rn']) + i['room_type_id'][1]
            list2.append(i)

        def key_func(k):
            return k['rn_room_type']
        list2 = sorted(list2, key=key_func)
        listOfRooms = []
        for key, value in groupby(list2, key_func):
            # print(key, value)
            listOfRooms.append(list(value))

        roomsList=[]
        for room in listOfRooms:
            updated_room = list(filter(lambda x: x['show'], room))
            if len(updated_room) > 0:
                roomsList.append({
                   'number': updated_room[0]['rn'],
                   'type': updated_room[0]['room_type_id'][1],
                   'clients': list(map(lambda client: {'name': client['name'], 'comment': client['note']}, updated_room)),
                   'len_of_clients': len(updated_room),
                })
        counter_sgl = 0
        counter_dbl = 0
        counter_twn = 0
        counter_trp = 0
        for room in roomsList:
            if room['type'] == 'SGL':
                counter_sgl += 1
            if room['type'] == 'DBL':
                counter_dbl += 1
            if room['type'] == 'TWN':
                counter_twn += 1
            if room['type'] == 'TRP':
                counter_trp += 1
        counter_total = counter_sgl + counter_dbl + counter_twn + counter_trp

        ctx = {
            'default_model': 'hotel.reservation.form.report.wizard',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'rooms_list': sorted(roomsList, key=lambda d: d['number']),
            'counter_sgl': counter_sgl,
            'counter_dbl': counter_dbl,
            'counter_twn': counter_twn,
            'counter_trp': counter_trp,
            'counter_total': counter_total,
            'sale_order_id': sale_order_id,
            'subject': sale_order_id.name + ' ' + self.name_of_hotel.name

        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class ReportBomStructure(models.AbstractModel):
    _name = 'report.invoice_custom.hotel_reservation_form_report_view'
    _description = 'Hotel Reservation Form Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # get id of hotel
        id_of_hotel = self.env.context.get('active_id')
        # get data of hotel (object)
        # hotels_id = self.env['hotels'].search([('id', '=', id_of_hotel)])
        # get id of sale order
        id_of_sale_order = int(self.env['hotels'].search([('id', '=', id_of_hotel)]).sale_order_id)
        # get data of sale order (object)
        sale_order_id = self.env['hotel.reservation.form.report.wizard'].search([])[-1].object_sale_order
        # get object wizard
        object_hotel_reservation_form_report_wizard = self.env['hotel.reservation.form.report.wizard'].search([])[-1]
        hotels_id = object_hotel_reservation_form_report_wizard.name_of_hotel

        INFO = self.env['clients'].search_read([('sale_order_id', '=', sale_order_id.id)])
        list2 = []
        for i in INFO:
            i['rn_room_type'] = str(i['rn']) + i['room_type_id'][1]
            list2.append(i)

        def key_func(k):
            return k['rn_room_type']
        list2 = sorted(list2, key=key_func)
        listOfRooms = []
        for key, value in groupby(list2, key_func):
            # print(key, value)
            listOfRooms.append(list(value))

        roomsList=[]
        for room in listOfRooms:

            updated_room = list(filter(lambda x: x['show'], room))

            if len(updated_room) > 0:
                roomsList.append({
                   'number': updated_room[0]['rn'],
                   'type': updated_room[0]['room_type_id'][1],
                   'clients': list(map(lambda client: {'name': client['name'], 'comment': client['note']}, updated_room)),
                   'len_of_clients': len(updated_room),
                })
        counter_sgl = 0
        counter_dbl = 0
        counter_twn = 0
        counter_trp = 0
        for room in roomsList:
            if room['type'] == 'SGL':
                counter_sgl += 1
            if room['type'] == 'DBL':
                counter_dbl += 1
            if room['type'] == 'TWN':
                counter_twn += 1
            if room['type'] == 'TRP':
                counter_trp += 1
        counter_total = counter_sgl + counter_dbl + counter_twn + counter_trp






        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'hotels_id': hotels_id,
            'sale_order_id': sale_order_id,
            'object_hotel_reservation_form_report_wizard': object_hotel_reservation_form_report_wizard,
            'rooms_list': roomsList,
            'counter_sgl': counter_sgl,
            'counter_dbl': counter_dbl,
            'counter_twn': counter_twn,
            'counter_trp': counter_trp,
            'counter_total': counter_total,
        }
