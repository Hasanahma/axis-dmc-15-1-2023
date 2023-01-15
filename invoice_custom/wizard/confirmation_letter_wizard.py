from odoo import fields, models, api
from itertools import groupby

class ConfirmationLetterWizard(models.TransientModel):
    _name = "confirmation.letter.wizard"

    def _get_default_show_arr_dep(self):
        sale_order_id = self.env.context.get('active_id')
        print(sale_order_id)
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.arrival_departure_expense_ids:
            return True
        else:
            return False

    def _get_default_show_hotels(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.hotels_expense_ids:
            return True
        else:
            return False

    def _get_default_show_restaurants(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.resturnats_expense_ids:
            return True
        else:
            return False

    def _get_default_show_itinerary(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.itineraries_expense_ids:
            return True
        else:
            return False

    def _get_default_show_transportations(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.transportation_expense_ids:
            return True
        else:
            return False

    def _get_default_show_guides(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.guide_expense_ids:
            return True
        else:
            return False

    def _get_default_show_rooming_list(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.clients_expense_ids:
            return True
        else:
            return False

    def _get_default_show_inclusions(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.inclusions_expense_ids:
            return True
        else:
            return False

    def _get_default_show_logo(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.inclusions_expense_ids:
            return True
        else:
            return False


    def _get_default_show_note(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.general_note:
            return True
        else:
            return False

    def get_default_show_agent(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.partner_id:
            return True
        else:
            return False

    def _get_default_show_agent(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.partner_id:
            return True
        else:
            return False

    def _get_default_sale_order(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        return object_sale_order

    def _get_default_show_extras(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if object_sale_order.extras_expense_ids:
            return True
        else:
            return False


    show_general_information = fields.Boolean(string="Show General Info", default=True)
    show_arr_dep = fields.Boolean(string="Show Arr/Dep", default=_get_default_show_arr_dep)
    show_hotels = fields.Boolean(string="Show Hotels", default=_get_default_show_hotels)
    show_restaurants = fields.Boolean(string="Show Restaurants", default=_get_default_show_restaurants)
    show_itinerary = fields.Boolean(string="Show Itinerary", default=_get_default_show_itinerary)
    show_transportations = fields.Boolean(string="Show Transportation", default=_get_default_show_transportations)
    show_guides = fields.Boolean(string="Show Guide", default=_get_default_show_guides)
    show_rooming_list = fields.Boolean(string="Show Rooming List", default=_get_default_show_rooming_list)
    show_inclusions = fields.Boolean(string="Show Inclusions", default=_get_default_show_inclusions)
    show_note = fields.Boolean(string="Show Note", default=_get_default_show_note)
    sale_order_id = fields.Many2one('sale.order', string='sale order id', default=_get_default_sale_order)
    show_agent = fields.Boolean(string="Show Agent", default=_get_default_show_agent)
    show_logo = fields.Boolean(string="Show Logo", default=_get_default_show_logo)
    show_extras = fields.Boolean(string="Show Extras", default=_get_default_show_extras)

    def btn_send_email(self):



        template_id = self.env.ref('invoice_custom.confirmation_letter_email').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


        # sale_order_id = self.env.context.get('active_id')
        # object_sale_order = self.env['sale.order'].browse(sale_order_id)
        # print(object_sale_order)
        #
        #
        #
        #
        # data = {
        #     'sale_order_id': object_sale_order,
        #     'show_general_information': self.show_general_information,
        #     'show_arr_dep': self.show_arr_dep,
        #     'show_hotels': self.show_hotels,
        #     'show_restaurants': self.show_restaurants,
        #     'show_itinerary': self.show_itinerary,
        #     'show_transportations': self.show_transportations,
        #     'show_guides': self.show_guides,
        #     'show_rooming_list': self.show_rooming_list,
        #     'show_inclusions': self.show_inclusions,
        #     'show_note': self.show_note,
        # }
        # # report_action = self.env.ref('invoice_custom.action_confirmation_letter_print').report_action(self, data=data)
        # # print(report_action)
        #
        # template_obj = self.env['mail.template'].sudo().search([('name', '=', 'Confirmation Letter Email')], limit=1)
        #
        # if template_obj:
        #     receipt_list = ['abdullah.almashaqbeh@flex-ops.com']
        #     email_cc = []
        #     for i in object_sale_order.transportation_expense_ids:
        #         print(i)
        #     body = template_obj.body_html
        #     body = body.replace('--department--','pppp')
        #     body = body.replace('--variable_holds_dynamic_data_1--', 'abood2')
        #     body = body.replace('--variable_holds_dynamic_data_2--', 'abood3')
        #     body = body.replace('--variable_holds_dynamic_data_3--', 'abood4')
        #     body = body.replace('--variable_holds_dynamic_data_4--', 'abood5')
        #     body = body.replace('--product_number_goes_here--', 'obood6')
        #     body = body.replace('--brach--', 'kkkkk')
        #
        #     mail_values = {
        #         'subject': template_obj.subject,
        #         'body_html': body,
        #         'email_to': ';'.join(map(lambda x: x, receipt_list)),
        #         'email_cc': ';'.join(map(lambda x: x, email_cc)),
        #         'email_from': template_obj.email_from,
        #     }
        #     create_and_send_email = self.env['mail.mail'].create(mail_values).send()

    def button_print_confirmation_letter(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)



        data = {
            'sale_order_id': object_sale_order,
            'show_general_information': self.show_general_information,
            'show_arr_dep': self.show_arr_dep,
            'show_hotels': self.show_hotels,
            'show_restaurants': self.show_restaurants,
            'show_itinerary': self.show_itinerary,
            'show_transportations': self.show_transportations,
            'show_guides': self.show_guides,
            'show_rooming_list': self.show_rooming_list,
            'show_inclusions': self.show_inclusions,
            'show_note': self.show_note,
            'show_agent': self.show_agent,
            'show_logo' : self.show_logo,
            'show_extras': self.show_extras,
        }
        report_action = self.env.ref('invoice_custom.action_confirmation_letter_print').report_action(self, data = data)
        report_action['close_on_report_download'] = True
        return report_action



class ConfirmationLetter(models.AbstractModel):
    _name = 'report.invoice_custom.confirmation_letter'
    _description = 'Confirmation Letter'

    @api.model
    def _get_report_values(self, docids, data=None):
        sale_order_id = self.env['confirmation.letter.wizard'].search([])[-1].sale_order_id
        print(sale_order_id)
        #object_sale_order = self.env['sale.order'].browse(sale_order_id)
        object_sale_order = self.env['confirmation.letter.wizard'].search([])[-1].sale_order_id
        object_confirmation_letter_wizard = self.env['confirmation.letter.wizard'].search([])[-1]
        print(object_sale_order.itineraries_expense_ids)
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

        roomsList = []
        for room in listOfRooms:

            updated_room = list(filter(lambda x: x['show'], room))

            if len(updated_room) > 0:
                roomsList.append({
                    'number': updated_room[0]['rn'],
                    'type': updated_room[0]['room_type_id'][1],
                    'clients': list(
                        map(lambda client: {'name': client['name'], 'comment': client['note']}, updated_room)),
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
            'sale_order_id': object_sale_order,
            'object_confirmation_letter_wizard': object_confirmation_letter_wizard,
            'rooms_list': roomsList,
            'counter_sgl': counter_sgl,
            'counter_dbl': counter_dbl,
            'counter_twn': counter_twn,
            'counter_trp': counter_trp,
            'counter_total': counter_total,
        }
