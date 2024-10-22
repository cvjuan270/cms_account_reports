from collections import defaultdict
from datetime import datetime
from odoo import models, fields, api


class ReportAged(models.AbstractModel):
    _name = "report.cms_account_reports.report_aged_view"

    def _get_domain(self, data):
        domain = [
            ("state", "=", "posted"),
            (
                "move_type",
                "in",
                ["out_invoice", "out_refund", "in_invoice", "in_refund"],
            ),
            ("amount_residual_signed", "!=", 0),
            ("date", ">=", data["start_date"]),
            ("date", "<=", data["end_date"]),
            # ("company_id", "in", data["allowed_company_ids"]),
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

    @api.model
    def _get_report_values(self, docids, data=None):
        print(data)
        moves = self.env["account.move"].search(self._get_domain(data))
        invoices = []
        for move in moves:
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
                },
            )

        i_aged_payment = []
        i_aged_receive = []
        for i in invoices:
            if i["move_type"] in ["in_invoice", "in_refund"]:
                i_aged_payment.append(i)
            if i["move_type"] in ["out_invoice", "out_refund"]:
                i_aged_receive.append(i)
        # for i_p in i_aged_payment:
        #     i_p["residual"] = abs(i_p["residual"])

        wizard_id = data["wizard_id"]
        return {
            "doc_ids": [wizard_id],
            "doc_model": "aged.wizard",
            "docs": self.env["aged.wizard"].browse(wizard_id),
            "invoices": invoices,
            "i_aged_receive": i_aged_receive,
            "i_aged_payment": i_aged_payment,
        }
