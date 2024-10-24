from odoo import models


class CmsAgedPayableWizard(models.TransientModel):
    _name = "cms_account_reports.aged_payable_wizard"
    _inherit = "cms_account_reports.abstract_wizard"

    def get_report(self):
        data = self._prepare_report_data()
        return self.env.ref("cms_account_reports.report_aged_payable").report_action(
            self, data=data
        )
