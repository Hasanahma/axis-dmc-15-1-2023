# -*- coding: utf-8 -*-
{
    'name': "Sale Order Custom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Sale order and account invoice custom
    """,

    'author': "Faris",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/hotel_mail_template.xml',
        'security/security.xml',
        'wizard/confirmation_letter_wizard_view.xml',
        'wizard/expenses_sheet_wizard_view.xml',
        'wizard/reports_wizard_view.xml',
        'wizard/profit_loss_report_wizard_view.xml',
        'wizard/hotel_reservation_form_report_wizard_view.xml',
        'wizard/restaurant_reservation_form_report_wizard_view.xml',
        'wizard/transportation_reservation_form_report_wizard_view.xml',
        'wizard/change_date_wizard_view.xml',
        'wizard/hotel_bill_wizard_view.xml',
        'wizard/transportation_bill_wizard_view.xml',
        'views/accommodation_view.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/expense_type_view.xml',
        'views/operation_module_view.xml',
        'views/client_view.xml',
        'report/invoice_report_inherit.xml',
        'report/groups_run_down_by_arrival_date_report.xml',
        'report/entrance_fees_run_down_report.xml',
        'report/nationalities_run_down_report.xml',
        'report/resturant_run_down_report.xml',
        'report/itineraries_run_down_report.xml',
        'report/guide_run_down_report.xml',
        'report/transportation_run_down_report.xml',
        'report/extras_run_down_report.xml',
        'report/hotel_run_down_report.xml',
        'report/arr_dep_report.xml',
        'report/hotel_reservation_form_report.xml',
        'report/restaurant_reservation_form_report.xml',
        'report/information_report.xml',
        'report/actual_guide_expense_sheet_report.xml',
        'report/profit_loss_report.xml',
        'report/transportation_reservation_form_report.xml',
        'report/confirmation_letter_report.xml',
        'report/visa_list_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

