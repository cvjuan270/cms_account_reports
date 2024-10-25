from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    cms_a_r_operation_date = fields.Date("Fecha Operativa")
