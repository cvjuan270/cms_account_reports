import io
from itertools import groupby
from odoo import models, fields, api
from odoo.exceptions import UserError


class PaymentWizard(models.TransientModel):
    _name = 'payment.wizard'
    _description = 'Asistente para Reporte de Pagos'

    user_id = fields.Many2one('res.users', 'Cajero')
    start_date = fields.Date(string='Fecha de inicio', required=True, default=lambda self: fields.datetime.now())
    end_date = fields.Date(string='Fecha final', required=True, default=lambda self: fields.datetime.now())

    @api.model
    def search_item(self, lst, journal_id):
        for item in lst:
            if item['journal_id'] == journal_id:
                return item
        return False

    def generate_report(self):
        lst = []
        amounts = {'sum_amount_cash_cf': 0.00,
                   'sum_amount_cash_sf': 0.00,
                   'sum_amount_cash_sc': 0.00,
                   'sum_amount_bank_cf': 0.00,
                   'sum_amount_bank_sf': 0.00,
                   'sum_amount_bank_sc': 0.00
                   }
        payments = self.env['account.payment'].read_group(
            domain=[
                ('state', '=', 'posted'),
                ('user_id', '=', self.user_id.id),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date)
            ],
            fields=['amount:sum'],
            groupby=['journal_id'],
            lazy=False
        )
        for payment_group in payments:
            dict_payments = {}

            dict_payments['payments'] = []
            dict_payments['group_payment_journal'] = payment_group
            _payments = self.env['account.payment'].search(payment_group['__domain'])
            for item in _payments:
                payment = {
                    'date': item.date,
                    'name': item.name,
                    'partner_id': item.partner_id.name if item.partner_id else '',
                    'ref': item.ref,
                    'amount': item.amount if item.payment_type == 'inbound' else item.amount * -1,
                    'currency_id': item.currency_id.id,
                }
                dict_payments['payments'].append(payment)

                if item.journal_id.type == 'cash':
                    if item.reconciled_invoice_ids:
                        if item.reconciled_invoice_ids[0].journal_id.l10n_latam_use_documents:
                            amounts['sum_amount_cash_cf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                        else:
                            amounts['sum_amount_cash_sf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                    else:
                        if item.reconciled_bill_ids:
                            if item.reconciled_bill_ids[0].journal_id.l10n_latam_use_documents:
                                amounts[
                                    'sum_amount_cash_cf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                            else:
                                amounts[
                                    'sum_amount_cash_sf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                        else:
                            amounts['sum_amount_cash_sc'] += item.amount if item.payment_type == 'inbound' else item.amount * -1

                if item.journal_id.type == 'bank':
                    if item.reconciled_invoice_ids:
                        if item.reconciled_invoice_ids[0].journal_id.l10n_latam_use_documents:
                            amounts[
                                'sum_amount_bank_cf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                        else:
                            amounts['sum_amount_bank_sf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                    else:
                        if item.reconciled_bill_ids:
                            if item.reconciled_bill_ids[0].journal_id.l10n_latam_use_documents:
                                amounts[
                                    'sum_amount_bank_cf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                            else:
                                amounts[
                                    'sum_amount_bank_sf'] += item.amount if item.payment_type == 'inbound' else item.amount * -1
                        else:
                            amounts['sum_amount_bank_sc'] += item.amount if item.payment_type == 'inbound' else item.amount * -1

            dict_payments['sum_amount_journal'] = sum(x['amount'] for x in dict_payments['payments'])

            lst.append(dict_payments)
        data = {
            'user_id': self.user_id.name,
            'lst_payments': lst,
            'amounts': amounts,
            # 'amount_invoices_sf': amount_invoices_sf,
            # 'amount_invoices_cf': amount_invoices_cf,
            # 'amount_invoices_sc': amount_invoices_sc,
            # 'amount_cash': sum(payment['amount'] for payment in payments if payment.journal_id.type == 'cash'),
            # 'amount_bank': sum(payment['amount'] for payment in payments if payment.journal_id.type == 'bank'),
            'res_company': self.env.company
        }

        report = self.env['ir.actions.report'].search([('report_name', '=', 'cms_account_reports.payments')],
                                                      limit=1).report_action(self, data=data)
        return report
