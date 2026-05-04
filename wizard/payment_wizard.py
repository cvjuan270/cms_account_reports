import hashlib
from collections import defaultdict
from datetime import datetime

import pytz
from odoo import fields, models

pe_tz = pytz.timezone("America/Lima")


class PaymentWizard(models.TransientModel):
    _name = "payment.wizard"
    _description = "Asistente para Reporte de Pagos"

    user_id = fields.Many2one("res.users", "Cajero")
    start_date = fields.Date(
        string="Fecha de inicio",
        required=True,
        default=lambda self: fields.Date.today(),
    )
    end_date = fields.Date(
        string="Fecha final",
        required=True,
        default=lambda self: fields.Date.today(),
    )

    def search_item(self, lst, journal_id):
        for item in lst:
            if item["journal_id"] == journal_id:
                return item
        return False

    def _get_qr_and_hash(self, lst, amounts):
        rslt = {"qr": "", "hash": ""}
        qr = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
            self.env.user.name,
            str(datetime.now(pe_tz)),
            self.user_id.name,
            str(self.start_date) + "-" + str(self.end_date),
            amounts["sum_amount_cash_cf"],
            amounts["sum_amount_cash_sf"],
            amounts["sum_amount_cash_sc"],
            amounts["sum_amount_bank_cf"],
            amounts["sum_amount_bank_sf"],
            amounts["sum_amount_bank_sc"],
            sum(amounts.values()),
        )
        rslt["qr"] = qr
        rslt["hash"] = hashlib.sha256(qr.encode("utf-8")).hexdigest()
        return rslt

    def _classify_amount(self, item, amounts, signed_amount):
        """Clasifica el monto del pago dentro del cuadre cash/bank x CF/SF/SC."""
        bucket = None
        if item.journal_id.type == "cash":
            prefix = "sum_amount_cash"
        elif item.journal_id.type == "bank":
            prefix = "sum_amount_bank"
        else:
            return None

        if item.reconciled_invoice_ids:
            if item.reconciled_invoice_ids[0].journal_id.l10n_latam_use_documents:
                bucket = f"{prefix}_cf"
            else:
                bucket = f"{prefix}_sf"
        elif item.reconciled_bill_ids:
            if item.reconciled_bill_ids[0].journal_id.l10n_latam_use_documents:
                bucket = f"{prefix}_cf"
            else:
                bucket = f"{prefix}_sf"
        else:
            bucket = f"{prefix}_sc"

        amounts[bucket] += signed_amount
        return bucket

    def generate_report(self):
        lst = []
        amounts = {
            "sum_amount_cash_cf": 0.00,
            "sum_amount_cash_sf": 0.00,
            "sum_amount_cash_sc": 0.00,
            "sum_amount_bank_cf": 0.00,
            "sum_amount_bank_sf": 0.00,
            "sum_amount_bank_sc": 0.00,
        }
        # Conteo de operaciones por bucket (útil para auditoría)
        counts = {k.replace("sum_amount_", "count_"): 0 for k in amounts}

        domain = [
            ("state", "=", "paid"),
            ("create_uid", "=", self.user_id.id),
            ("date", ">=", self.start_date),
            ("date", "<=", self.end_date),
        ]
        payment_groups = self.env["account.payment"]._read_group(
            domain=domain,
            groupby=["journal_id"],
            aggregates=["amount:sum"],
        )

        # Acumuladores generales para el resumen ejecutivo
        total_inbound = 0.0
        total_outbound = 0.0
        count_inbound = 0
        count_outbound = 0
        total_cash = 0.0
        total_bank = 0.0
        count_cash = 0
        count_bank = 0
        partners_set = set()
        partner_totals = defaultdict(float)
        partner_counts = defaultdict(int)

        for journal, amount_sum in payment_groups:
            dict_payments = {
                "payments": [],
                "group_payment_journal": {
                    "journal_id": (journal.id, journal.display_name),
                    "amount": amount_sum,
                },
                "journal_type": journal.type,
                "journal_count": 0,
            }
            _payments = self.env["account.payment"].search(
                domain + [("journal_id", "=", journal.id)],
                order="date asc, id asc",
            )
            for item in _payments:
                signed = (
                    item.amount
                    if item.payment_type == "inbound"
                    else item.amount * -1
                )
                bucket = self._classify_amount(item, amounts, signed)
                if bucket:
                    counts[bucket.replace("sum_amount_", "count_")] += 1

                payment = {
                    "date": item.date,
                    "name": item.name,
                    "partner_id": (
                        item.partner_id.name if item.partner_id else ""
                    ),
                    "ref": item.memo,
                    "amount": signed,
                    "payment_type": item.payment_type,
                    "journal_type": item.journal_id.type,
                    "bucket": (
                        bucket.replace("sum_amount_", "") if bucket else ""
                    ),
                    "currency_id": item.currency_id.id,
                }
                dict_payments["payments"].append(payment)

                # Acumuladores ejecutivos
                if item.payment_type == "inbound":
                    total_inbound += item.amount
                    count_inbound += 1
                else:
                    total_outbound += item.amount
                    count_outbound += 1

                if item.journal_id.type == "cash":
                    total_cash += signed
                    count_cash += 1
                elif item.journal_id.type == "bank":
                    total_bank += signed
                    count_bank += 1

                if item.partner_id:
                    partners_set.add(item.partner_id.id)
                    partner_totals[item.partner_id.name] += signed
                    partner_counts[item.partner_id.name] += 1

            dict_payments["sum_amount_journal"] = sum(
                x["amount"] for x in dict_payments["payments"]
            )
            dict_payments["journal_count"] = len(dict_payments["payments"])
            lst.append(dict_payments)

        count_total = count_inbound + count_outbound
        net_total = total_inbound - total_outbound
        avg_amount = (net_total / count_total) if count_total else 0.0

        top_partners = sorted(
            (
                {"name": name, "amount": amt, "count": partner_counts[name]}
                for name, amt in partner_totals.items()
            ),
            key=lambda x: abs(x["amount"]),
            reverse=True,
        )[:5]

        summary = {
            "count_total": count_total,
            "count_inbound": count_inbound,
            "count_outbound": count_outbound,
            "total_inbound": total_inbound,
            "total_outbound": total_outbound,
            "net_total": net_total,
            "total_cash": total_cash,
            "total_bank": total_bank,
            "count_cash": count_cash,
            "count_bank": count_bank,
            "unique_partners": len(partners_set),
            "avg_amount": avg_amount,
            "pct_cash": (total_cash / net_total * 100) if net_total else 0.0,
            "pct_bank": (total_bank / net_total * 100) if net_total else 0.0,
        }

        data = {
            "user_id": self.user_id.name,
            "user_login": self.user_id.login or "",
            "start_date": fields.Date.to_string(self.start_date),
            "end_date": fields.Date.to_string(self.end_date),
            "report_user": self.env.user.name,
            "report_datetime": datetime.now(pe_tz).strftime("%Y-%m-%d %H:%M:%S"),
            "lst_payments": lst,
            "amounts": amounts,
            "counts": counts,
            "summary": summary,
            "top_partners": top_partners,
            "res_company": self.env.company,
            "qr_and_hash": self._get_qr_and_hash(lst, amounts),
        }

        report = (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", "cms_account_reports.payments")], limit=1
            )
            .report_action(self, data=data)
        )
        return report
