from collections import namedtuple

from odoo import fields, models

TYPES = [
    # ("group_run_down_by_arrival_date", "Group run down by arrival date"),
    ("entrance_fees_run_down", "Entrance fees run down"),
    ("nationalities_run_down", "Nationalities run down"),
    ("restaurant_run_down", "Restaurant run down"),
    ("itineraries_run_down", "Itineraries run down"),
    ("guide_run_down", "Guide run down"),
    ("transportation_run_down", "Transportation run down"),
    ("extras_run_down", "Extras run down"),
    ("hotel_run_down", "Hotel run down"),
    ("Arr_Dep", "Group run down Arr/Dep"),
]


class SaleCustomReportWizard(models.TransientModel):
    _name = "sale.custom.report.wizard"

    report_type = fields.Selection(TYPES, string="Type")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    file_no = fields.Char(string="File Number")
    restaurant_id = fields.Many2one('res.partner', string="Restaurant")
    transportation_id = fields.Many2one('res.partner', string="Transportation Name")
    supplier_id = fields.Many2one('res.partner', string="Supplier Name")
    nationality_id = fields.Many2one('res.country', string="Nationality")
    entrance_id = fields.Many2one('entrances.type', string="Entrance")
    guide_id = fields.Many2one('res.partner', string="Guide")
    hotel_id = fields.Many2one('res.partner', string="Hotel")
    border_id = fields.Many2one('borders', string="Border")
    vehicles_id = fields.Many2one('type.vehicles', string="Type of Vehicles")
    language = fields.Many2one('guide.language', string="Language")
    exclude_agent_ids = fields.Many2many('res.partner', string="Exclude Agent")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    date_filter = fields.Selection([("from_date", "Check In"), ("to_date", "Check Out")], string="Date Filter",
                                   default='from_date')
    status_id = fields.Many2one('hotel.status', string="Status")
    all_status = fields.Boolean(string="All Status")
    by_group = fields.Selection([("arrival", "Arrival"), ("departure", "Departure"), ("both", "Both")], string="By",
                                default='both')
    show_file = fields.Selection(
        [("show_cancel_file", "Show Cancel File"), ("do_not_show_cancel_file", "Don't Show Cancel File"),
         ("both", "Both")], string="Show",
        default='both')
    by_state = fields.Many2one('res.country.state', string="Location")
    by_star_number = fields.Selection([
        ('0 Star', '0 Star'),
        ('1 Star', '1 Star'),
        ('2 Stars', '2 Stars'),
        ('3 Stars', '3 Stars'),
        ('4 Stars', '4 Stars'),
        ('5 Stars', '5 Stars'),
    ])

    def button_print_report(self):
        if self.report_type == 'group_run_down_by_arrival_date':
            res = self.env["sale.order"].search_read(
                [("date_order", ">=", self.from_date), ("date_order", "<=", self.to_date)], )
            data = {
                'form': self.read(),
                'orders': res
            }
            return self.env.ref("invoice_custom.action_report_groups_run_down_by_arrival_date").report_action(self,
                                                                                                              data=data)
        elif self.report_type == "entrance_fees_run_down":
            if self.entrance_id:
                search_filter = [("date", ">=", self.from_date),
                                 ("date", "<=", self.to_date), ("name", "=", self.entrance_id.id),
                                 ("sale_order_id", "!=", None)]

            else:
                search_filter = [("date", ">=", self.from_date),
                                 ("date", "<=", self.to_date), ("sale_order_id", "!=", None)]

            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass

            res = self.env["entrance"].search_read(search_filter)

            for item in res:
                sale_order = self.env['sale.order'].search([('id', '=', item['sale_order_id'][0])])
                item['name'] = sale_order.name
                item['nationality_id'] = sale_order.nationality_id.name
                item['date_order'] = sale_order.date_order
                item['customer'] = sale_order.customer
                item['total_pax'] = sale_order.total_pax
                item['partner_id'] = sale_order.partner_id.name
                item['state'] = sale_order.state
            data = {
                'form': self.read(),
                'orders': res
            }
            return self.env.ref("invoice_custom.action_report_entrance_fees_run_down").report_action(self, data=data)

        elif self.report_type == "nationalities_run_down":
            if self.nationality_id:
                search_filter = [("date_order", ">=", self.from_date), ("date_order", "<=", self.to_date),
                                 ("nationality_id", "=", self.nationality_id.id)]
            else:
                search_filter = [("date_order", ">=", self.from_date), ("date_order", "<=", self.to_date),
                                 ('nationality_id', '!=', None)]

            if self.status_id and self.all_status == False:
                search_filter.append(('state', '=', self.status_id.id))

            if self.show_file == 'show_cancel_file':
                search_filter.append(("state", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("state", "!=", 'cancel'))
            else:
                pass

            res = self.env["sale.order"].search_read(
                search_filter
            )

            data = {
                'form': self.read(),
                'orders': res
            }
            return self.env.ref("invoice_custom.action_report_nationalities_run_down").report_action(self, data=data)

        elif self.report_type == "restaurant_run_down":
            res = []
            if self.restaurant_id:
                search_filter = [("date", ">=", self.from_date),
                                 ("date", "<=", self.to_date), ("name", "=", self.restaurant_id.id),
                                 ("sale_order_id", "!=", None)]

            if not self.restaurant_id:
                search_filter = [("date", ">=", self.from_date),
                                 ("date", "<=", self.to_date),
                                 ("sale_order_id", "!=", None)]

            if self.status_id and self.all_status == False:
                search_filter.append(('status_id', '=', self.status_id.id))

            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass

            restaurants = self.env["restaurants"].search(search_filter)

            for item in restaurants:
                sale_order = self.env['sale.order'].search([('id', '=', item.sale_order_id.id)])
                res_dic = item.read()[0]
                res_dic['file_no'] = sale_order.name
                res_dic['restaurant'] = item.name.name
                # res_dic['mobile'] = item.guide_id.number
                res_dic['customer'] = sale_order.customer
                res_dic['meal'] = item.meal_id.name
                res_dic['pax'] = item.pax
                res_dic["status"] = item.sale_order_id.state
                res_dic["mobile"] = item.guide_id2.mobile
                res_dic["phone"] = item.guide_id2.phone
                guideList = []
                for guide in item.guide_ids:
                    guideList.append({
                        'name': guide.name,
                        'phone': guide.phone,
                        'mobile': guide.mobile,
                    })
                res_dic['guide'] = guideList
                res.append(res_dic)

            # query = """select s.name as file_no,customer, date_order, g.name, g.number as mobile,res.name as guide, m.name as meal,r.pax from sale_order as s
            #         left join restaurants as r on s.id = r.sale_order_id
            #         left join guide as g on s.id = g.sale_order_id
            #         left join restaurants_meals as m on r.meal_id = m.id
            #         left join res_partner as res on g.name = res.id
            #         where r.id = '%s' and s.date_order >= '%s' and s.date_order <= '%s'
            #        """ % (self.restaurant_id.id, self.from_date, self.to_date)
            # self.env.cr.execute(query)
            # res = self.env.cr.dictfetchall()
            data = {
                'form': self.read(),
                'orders': res
            }
            print(data['orders'])

            return self.env.ref("invoice_custom.action_report_restaurant_run_down").report_action(self, data=data)






        elif self.report_type == "itineraries_run_down":
            res = []
            search_filter = [("from_date", ">=", self.from_date), ("from_date", "<=", self.to_date),
                             ("sale_order_id", "!=", None)]

            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass

            itineraries = self.env["itineraries"].search(search_filter)

            for item in itineraries:
                sale_order = self.env['sale.order'].search([('id', '=', item.sale_order_id.id)])
                res_dic = item.read()[0]
                res_dic['file_no'] = sale_order.name
                res_dic['total_pax'] = sale_order.total_pax
                res_dic['customer'] = sale_order.customer
                res_dic['nationality'] = item.sale_order_id.nationality_id.name
                res_dic['status'] = item.sale_order_id.state

                res.append(res_dic)

            # query = """select s.name as file_no,customer,p.from_date as date,total_pax,nationality_id, res.name as nationality, p.name as description from sale_order as s
            #                     left join itineraries as p on s.id = p.sale_order_id
            #                     left join res_country as res on nationality_id = res.id
            #                     where s.date_order >= '%s' and s.date_order <= '%s'
            #                    """ % (self.from_date, self.to_date)
            # self.env.cr.execute(query)
            # res = self.env.cr.dictfetchall()
            data = {
                'form': self.read(),
                'orders': res
            }
            return self.env.ref("invoice_custom.action_report_itineraries_run_down").report_action(self, data=data)

        elif self.report_type == "guide_run_down":
            res = []
            if self.date_filter == 'from_date':
                search_filter = [("date_from", ">=", self.from_date), ("date_from", "<=", self.to_date),
                                 ("name", "!=", None)]

            else:
                search_filter = [("date_to", ">=", self.from_date), ("date_to", "<=", self.to_date),
                                 ("name", "!=", None)]

            if self.guide_id:
                search_filter.append(("name", "=", self.guide_id.id))
            if self.status_id and self.all_status == False:
                search_filter.append(('status_id', '=', self.status_id.id))

            if self.language:
                search_filter.append(('language_id', '=', self.language.id))

            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass

            guides = self.env["guide"].search(search_filter)
            print(guides)
            for item in guides:
                sale_order = self.env['sale.order'].search([('id', '=', item.sale_order_id.id)])
                res_dic = item.read()[0]
                res_dic['file_no'] = sale_order.name
                res_dic['guide'] = item.name.name
                res_dic['language'] = item.language_id.name
                res_dic['customer'] = sale_order.customer
                res_dic['nationality'] = item.sale_order_id.nationality_id.name
                res_dic["status"] = item.sale_order_id.state
                res_dic["pax"] = item.sale_order_id.total_pax

                res.append(res_dic)

            # if not self.guide_id:
            #     query = """select s.name as file_no,customer,total_pax, g.name, res.name as guide, g.id , lan.name as language,
            #             g.date_from , g.date_to, g.days  from sale_order as s
            #                     left join guide as g on s.id = g.sale_order_id
            #                     left join guide_language as lan on g.language_id = lan.id
            #                     left join res_partner as res on g.name = res.id
            #                     where s.date_order >= '%s' and s.date_order <= '%s' and g.sale_order_id is not null
            #                    """ % (self.from_date, self.to_date)
            # else:
            #     query = """select s.name as file_no,customer,total_pax, g.name, res.name as guide, g.id , lan.name as language,
            #                             g.date_from , g.date_to, g.days  from sale_order as s
            #                                     left join guide as g on s.id = g.sale_order_id
            #                                     left join guide_language as lan on g.language_id = lan.id
            #                                     left join res_partner as res on g.name = res.id
            #                                     where s.date_order >= '%s' and s.date_order <= '%s'
            #                                     and g.sale_order_id is not null  and g.id = '%s';
            #                                    """ % (self.from_date, self.to_date, self.guide_id.id)
            #
            # self.env.cr.execute(query)
            # res = self.env.cr.dictfetchall()
            # print(res)
            data = {
                'form': self.read(),
                'orders': res
            }

            return self.env.ref("invoice_custom.action_report_guide_run_down").report_action(self, data=data)

        elif self.report_type == "transportation_run_down":
            res = []
            if self.date_filter == 'from_date':
                search_filter = [("date_from", ">=", self.from_date), ("date_from", "<=", self.to_date), ]

            elif self.date_filter == 'to_date':
                search_filter = [("date_to", ">=", self.from_date), ("date_to", "<=", self.to_date), ]

            if self.status_id and self.all_status == False:
                search_filter.append(('status_id', '=', self.status_id.id))

            if self.transportation_id:
                search_filter.append(("name", "=", self.transportation_id.id))

            if self.vehicles_id:
                search_filter.append(("vehicles_id", "=", self.vehicles_id.id))

            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass

            transportations = self.env["transportation"].search(search_filter)

            for item in transportations:
                sale_order = self.env['sale.order'].search([('id', '=', item.sale_order_id.id)])
                res_dic = item.read()[0]
                res_dic['file_no'] = sale_order.name
                res_dic['transportation_name'] = item.name.name
                res_dic['type_Vehicle'] = item.vehicles_id.name
                res_dic['nationality'] = item.sale_order_id.nationality_id.name
                res_dic["status"] = item.sale_order_id.state,
                res.append(res_dic)

            # query = """select s.name as file_no,customer, t.date_from, t.date_to,t.pax,t.note,v.type from sale_order as s
            #                     left join transportation as t on s.id = t.sale_order_id
            #                     left join type_vehicles as v on t.vehicles_id = v.id
            #                     where t.id = '%s' and s.date_order >= '%s' and s.date_order <= '%s'
            #                    """ % (self.transportation_id.id, self.from_date, self.to_date)
            # self.env.cr.execute(query)
            # res = self.env.cr.dictfetchall()
            data = {
                'form': self.read(),
                'orders': res
            }

            return self.env.ref("invoice_custom.action_report_transportation_run_down").report_action(self, data=data)

        elif self.report_type == "extras_run_down":
            res = []
            if self.supplier_id:
                search_filter = [("date", ">=", self.from_date),
                                 ("date", "<=", self.to_date), ("supplier_id", "=", self.supplier_id.id),
                                 ("sale_order_id", "!=", None)]
            if not self.supplier_id:
                search_filter = [("date", ">=", self.from_date),
                                 ("date", "<=", self.to_date),
                                 ("sale_order_id", "!=", None)]


            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass

            extras = self.env["extras"].search(search_filter)
            for item in extras:
                sale_order = self.env['sale.order'].search([('id', '=', item.sale_order_id.id)])
                res_dic = item.read()[0]
                res_dic['file_no'] = sale_order.name
                res_dic['supplier_name'] = item.supplier_id.name
                res_dic['customer'] = sale_order.customer
                res_dic['name'] = item.name.name
                res_dic["status"] = item.sale_order_id.state,

                res.append(res_dic)

            # query = """select s.name as file_no,customer,date_order, ex.name,e.pax, e.note  from sale_order as s
            #                         left join extras as e on s.id = e.sale_order_id
            #                         left join expense_type as ex on e.name = ex.id
            #                         where e.supplier_id = '%s' and s.date_order >= '%s' and s.date_order <= '%s'
            #                        """ % (self.supplier_id.id, self.from_date, self.to_date)
            #     self.env.cr.execute(query)
            #     res = self.env.cr.dictfetchall()
            data = {
                'form': self.read(),
                'orders': res
            }
            print(data)
            return self.env.ref("invoice_custom.action_report_extras_run_down").report_action(self, data=data)

        elif self.report_type == "hotel_run_down":

            if self.date_filter == 'from_date':
                search_filter = [("date_from", ">=", self.from_date), ("date_from", "<=", self.to_date),
                                 ("sale_order_id", "!=", None)]
            else:
                search_filter = [("date_to", ">=", self.from_date), ("date_to", "<=", self.to_date),
                                 ("sale_order_id", "!=", None)]
            if self.hotel_id:
                search_filter.append(('name', '=', self.hotel_id.id))

            if self.status_id and self.all_status == False:
                search_filter.append(('status_id', '=', self.status_id.id))

            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass
            if self.by_state:
                search_filter.append(("by_state", "=", self.by_state.id))

            if self.by_star_number:
                if self.by_star_number == '0 Star':
                    search_filter.append(("priority", "=", '0'))
                elif self.by_star_number == '1 Star':
                    search_filter.append(("priority", "=", '1'))
                elif self.by_star_number == '2 Star':
                    search_filter.append(("priority", "=", '2'))
                elif self.by_star_number == '3 Star':
                    search_filter.append(("priority", "=", '3'))
                elif self.by_star_number == '4 Star':
                    search_filter.append(("priority", "=", '4'))
                elif self.by_star_number == '5 Star':
                    search_filter.append(("priority", "=", '5'))

            hotels = self.env['hotels'].search(search_filter)

            hotel_group_list = {}
            for hotel in hotels:
                line_dict = {
                    "name": hotel.name.name,
                    "file_no": hotel.sale_order_id.name,
                    "customer": hotel.sale_order_id.customer,
                    "date_from": hotel.date_from,
                    "date_to": hotel.date_to,
                    "meal": hotel.meal_id.name,
                    "pax": hotel.pax,
                    "sgl_room": hotel.sgl_room,
                    "dbl_room": hotel.dbl_room,
                    "trp_room": hotel.trp_room,
                    "twin_room": hotel.twin_room,
                    "note": hotel.note,
                    "nights": hotel.nights,
                    "trn": hotel.trn,
                    "room_type": hotel.room_category_id.name,
                    "status": hotel.sale_order_id.state,
                }
                if not hotel.name.name in hotel_group_list.keys():
                    hotel_group_list[hotel.name.name] = [line_dict]
                else:
                    hotel_group_list[hotel.name.name].append(line_dict)

            hotels = [hotel_group_list[line] for line in hotel_group_list]
            data = {
                'form': self.read(),
                'orders': hotels
            }
            # print(data['form'][0])
            return self.env.ref("invoice_custom.action_report_hotel_run_down").report_action(self, data=data)

        elif self.report_type == "Arr_Dep":
            res = []
            search_filter = [("date", ">=", self.from_date), ("date", "<=", self.to_date),
                             ("sale_order_id", "!=", None)]
            if self.border_id:
                search_filter.append(('border', '=', self.border_id.id))



            if self.show_file == 'show_cancel_file':
                search_filter.append(("status_of_sale_order", "=", 'cancel'))
            elif self.show_file == "do_not_show_cancel_file":
                search_filter.append(("status_of_sale_order", "!=", 'cancel'))
            else:
                pass


            arr_dep = self.env["arrival.departure.expense"].search(search_filter, order='date')

            for item in arr_dep:
                if item.sale_order_id.partner_id.id not in self.exclude_agent_ids.ids:
                    hotel_name_list = []
                    sale_order = self.env['sale.order'].search([('id', '=', item.sale_order_id.id)])
                    res_dic = item.read()[0]
                    res_dic['file_no'] = sale_order.name
                    res_dic['customer'] = sale_order.customer
                    res_dic['agent'] = sale_order.partner_id.name
                    res_dic['nationality'] = sale_order.nationality_id.name
                    res_dic['border'] = item.border.name
                    res_dic['transportation'] = item.transportation_id.name.name
                    res_dic['guide'] = item.guide_id.name.name
                    res_dic['meet'] = item.meet_by.name
                    res_dic['driver_name'] = item.transportation_id.driver_name
                    res_dic["status"] = item.sale_order_id.state
                    if item.name == 'ARR':
                        for hotels in item.sale_order_id.hotels_expense_ids:
                            if item.date == hotels.date_from:
                                hotel_name_list.append(hotels.name.name)
                                res_dic['hotel'] = hotel_name_list
                    if item.name == 'DEP':
                        for hotels in item.sale_order_id.hotels_expense_ids:
                            if item.date == hotels.date_to:
                                hotel_name_list.append(hotels.name.name)
                                res_dic['hotel'] = hotel_name_list

                    res.append(res_dic)

            data = {
                'form': self.read(),
                'orders': res
            }

            return self.env.ref("invoice_custom.action_report_arr_dep").report_action(self, data=data)

        elif self.report_type == "profit_loss":
            if self.sale_order_id:
                order_dic = self.sale_order_id.read()
                move_ids = self.sale_order_id.mapped('order_line.invoice_lines.move_id')
                invoice_total = 0
                payment_states = []
                for move in move_ids:
                    invoice_total += move.amount_total
                    payment_states.append(move.payment_state)

                if payment_states.__contains__('paid') and ['not_paid', 'partial'] not in payment_states:
                    res_status = 'Paid'
                elif ['paid', 'not_paid'] in payment_states or ['paid', 'partial'] in payment_states:
                    res_status = 'Partially Paid'
                else:
                    res_status = "Not Paid"

                order_dic[0]['invoice_total'] = invoice_total
                order_dic[0]['payment_state'] = res_status
            else:
                order_dic = []
                if self.date_filter == 'order':
                    search_filter = [('date_order', '>=', self.from_date), ('date_order', '<=', self.to_date)]
                elif self.date_filter == "arrival":
                    search_filter = [('arrival_date', '>=', self.from_date), ('arrival_date', '<=', self.to_date)]
                else:
                    search_filter = [('departure_date', '>=', self.from_date), ('departure_date', '<=', self.to_date)]

                orders = self.env['sale.order'].search(search_filter)

                for order in orders:
                    order_obj = order.read()
                    move_ids = order.mapped('order_line.invoice_lines.move_id')
                    invoice_total = 0
                    payment_states = []
                    for move in move_ids:
                        invoice_total += move.amount_total
                        payment_states.append(move.payment_state)

                    if payment_states.__contains__('paid') and ['not_paid', 'partial'] not in payment_states:
                        res_status = 'Paid'
                    elif ['paid', 'not_paid'] in payment_states or ['paid', 'partial'] in payment_states:
                        res_status = 'Partially Paid'
                    else:
                        res_status = "Not Paid"

                    order_obj[0]['invoice_total'] = invoice_total
                    order_obj[0]['payment_state'] = res_status
                    order_dic.append(*order_obj)
            print(order_dic)

            data = {
                'form': self.read(),
                'orders': order_dic,
                'invoice_lines': self.sale_order_id.order_line.invoice_lines.read(),
                'cost_lines': self.sale_order_id.actual_expense_ids.read()
            }

            return self.env.ref("invoice_custom.action_report_axis_profit_loss").report_action(self, data=data)
