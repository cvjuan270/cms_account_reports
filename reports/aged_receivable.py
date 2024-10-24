from odoo import models, api, fields
from datetime import datetime


class CmsAgedReceivable(models.AbstractModel):
    _name = "report.cms_account_reports.aged_receivable"
    _inherit = "report.cms_account_reports.abstract_report"
    _description = "Report Aged Receivable"

    def _get_domain(self, data):
        res = super(CmsAgedReceivable, self)._get_domain(data)
        res += [("move_type", "in", ["out_invoice", "out_refund"])]
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        print(data)
        moves = self.env["account.move"].search(self._get_domain(data))
        invoices = []
        for move in moves:
            print(move.name)
            invoices.append(
                {
                    "partner_id": "%s-%s" % (move.partner_id.vat, move.partner_id.name),
                    "patient_id": move.patient_id.name if move.patient_id else None,
                    "physician_id": move.physician_id.name
                    if move.physician_id
                    else None,
                    "ref": move.ref or None,
                    "entry_id": move.id,
                    "name": move.name or None,
                    "date": move.date.strftime("%d/%m/%Y"),
                    "total_signed": move.amount_total_signed,
                    "total": move.amount_total,
                    "residual": move.amount_residual_signed,
                    "dias_retraso": (
                        fields.Date.from_string(fields.Date.today())
                        - move.invoice_date_due
                    ).days,
                    "invoice_user_id": move.invoice_user_id.name,
                    "move_type": move.move_type,
                    "cms_a_r_operation_date": move.cms_a_r_operation_date.strftime(
                        "%d/%m/%Y"
                    )
                    if move.cms_a_r_operation_date
                    else None,
                },
            )

        wizard_id = data["wizard_id"]
        return {
            "doc_ids": [wizard_id],
            "doc_model": "aged.wizard",
            "docs": self.env["aged.wizard"].browse(wizard_id),
            "invoices": invoices,
        }
