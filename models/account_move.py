from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    cms_a_r_operation_date = fields.Date("Fecha Operativa")
