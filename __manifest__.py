# -*- coding: utf-8 -*-
{
    "name": "Reportes Contables CMS",
    "summary": """
        """,
    "description": """
        - Reporte de pagos por cajero y por intervalo de fechas (Solo para moneda PEN)
    """,
    "author": "Juan Collado Vassquez.",
    "website": "https://tagre.app",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Accounting/Localizations/Reporting",
    "version": "0.1",
    "license": "LGPL-3",
    # any module necessary for this one to work correctly
    "depends": ["base", "account", "l10n_pe", "l10n_latam_base"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "wizard/payment_wizard.xml",
        "wizard/report_aged_wizard.xml",
        "views/menuitems.xml",
        "views/account_move_views.xml",
        "reports/layouts.xml",
        "reports/reports.xml",
        "reports/payments.xml",
        "reports/report_aged.xml",
    ],
}
