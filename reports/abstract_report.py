from odoo import models, api


class CmsAbstractReport(models.AbstractModel):
    _name = "report.cms_account_reports.abstract_report"
    _description = "Abstract Report"

    def _get_domain(self, data):
        domain = [
            ("state", "=", "posted"),
            # (
            #     "move_type",
            #     "in",
            #     ["out_invoice", "out_refund", "in_invoice", "in_refund"],
            # ),
            ("amount_residual_signed", "!=", 0),
            ("date", ">=", data["start_date"]),
            ("date", "<=", data["end_date"]),
        ]
        if data["partner_ids"]:
            domain += [("partner_id", "in", data["partner_ids"])]
        if data["journal_ids"]:
            domain += [("journal_id", "in", data["journal_ids"])]
        if data["physician_ids"]:
            domain += [("physician_id", "in", data["physician_ids"])]
        if data["patient_ids"]:
            domain += [("patient_id", "in", data["patient_ids"])]
        return domain
