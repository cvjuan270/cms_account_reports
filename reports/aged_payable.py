from odoo import models, api, fields
from datetime import datetime


class CmsAgedPayable(models.AbstractModel):
    _name = "report.cms_account_reports.aged_payable"
    _inherit = "report.cms_account_reports.abstract_report"
    _description = "Report Aged Payable"

    def _get_domain(self, data):
        res = super(CmsAgedPayable, self)._get_domain(data)
        res += [("move_type", "in", ["in_invoice", "in_refund"])]
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        moves = self.env["account.move"].search(self._get_domain(data))
        today = fields.Date.context_today(self)
        invoices = []
        for move in moves:
            invoices.append(
                {
                    "partner_id": "%s-%s" % (move.partner_id.vat, move.partner_id.name),
                    "patient_id": move.patient_id.name if move.patient_id else None,
                    "physician_id": move.physician_id.name
                    if move.physician_id
                    else None,
                    "ref": self._get_ref(move, self.get_source_orders_purchase),
                    "entry_id": move.id,
                    "name": move.name or None,
                    "date": move.date.strftime("%d/%m/%Y"),
                    "invoice_date": move.invoice_date.strftime("%d/%m/%Y"),
                    "invoice_date_due": move.invoice_date_due.strftime("%d/%m/%Y"),
                    "total_signed": move.amount_total_signed,
                    "total": move.amount_total,
                    "residual": move.amount_residual_signed,
                    "dias_retraso": (today - move.invoice_date_due).days
                    if move.invoice_date_due
                    else 0,
                    "invoice_user_id": move.invoice_user_id.name,
                    "move_type": move.move_type,
                    "cms_a_r_operation_date": move.cms_a_r_operation_date.strftime(
                        "%d/%m/%Y"
                    )
                    if move.cms_a_r_operation_date
                    else None,
                },
            )

        return {
            "doc_ids": [data["wizard_id"]],
            "doc_model": "cms_account_reports.aged_payable_wizard",
            "docs": self.env["cms_account_reports.aged_payable_wizard"].browse(
                data["wizard_id"]
            ),
            "invoices": invoices,
        }
