from odoo import fields, models, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError

class ChangeDateWizard(models.TransientModel):
    _name = "change.date.wizard"
    _description = "Change Date"

    new_date = fields.Date('New Arrival Date')

    def button_change_date(self):
        sale_order_id = self.env.context.get('active_id')
        object_sale_order = self.env['sale.order'].browse(sale_order_id)
        if self.new_date:
            old_arrival_date = object_sale_order.arrival_date
            new_arrival_date = self.new_date
            # get difference between new arrival date and old arrival date:
            diff_date = (new_arrival_date - old_arrival_date).days

            # change old arrival date to new arrival date:
            object_sale_order.arrival_date = new_arrival_date

            object_sale_order.departure_date += timedelta(days=diff_date)
        else:
            raise ValidationError(_('Please Enter New Arrival DAte'))

        for arrival_departure_record in object_sale_order.arrival_departure_expense_ids:
            if arrival_departure_record.date:
                arrival_departure_record.date += timedelta(days=diff_date)

        for hotel_record in object_sale_order.hotels_expense_ids:
            if hotel_record.date_from:
                hotel_record.date_from += timedelta(days=diff_date)
            if hotel_record.date_to:
                hotel_record.date_to += timedelta(days=diff_date)

        for itineraries_record in object_sale_order.itineraries_expense_ids:
            if itineraries_record.from_date:
                itineraries_record.from_date += timedelta(days=diff_date)


        for restaurant_record in object_sale_order.resturnats_expense_ids:
            if restaurant_record.date:
                restaurant_record.date += timedelta(days=diff_date)


        for transportation_record in object_sale_order.transportation_expense_ids:
            if transportation_record.date_from:
                transportation_record.date_from += timedelta(days=diff_date)
            if transportation_record.date_to:
                transportation_record.date_to += timedelta(days=diff_date)


        for guide_record in object_sale_order.guide_expense_ids:
            if guide_record.date_from:
                guide_record.date_from += timedelta(days=diff_date)
            if guide_record.date_to:
                guide_record.date_to += timedelta(days=diff_date)


        for entrance_record in object_sale_order.entrance_expense_ids:
            if entrance_record.date:
                entrance_record.date += timedelta(days=diff_date)

        for extras_record in object_sale_order.extras_expense_ids:
            if extras_record.date:
                extras_record.date += timedelta(days=diff_date)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Change Date Successfully',
                'type': 'rainbow_man',}
            }