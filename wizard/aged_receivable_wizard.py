from odoo import models, fields


class CmsAgedReceivableWizard(models.TransientModel):
    _name = "cms_account_reports.aged_receivable_wizard"
    _inherit = "cms_account_reports.abstract_wizard"

    def get_report(self):
        data = self._prepare_report_data()
        return self.env.ref("cms_account_reports.report_aged_receivable").report_action(
            self, data=data
        )
