from dateutil.relativedelta import relativedelta

from odoo import models, fields


class AgedWizard(models.TransientModel):
    _name = "aged.wizard"
    _description = "Asistente Reporte de Vencidos"

    start_date = fields.Date(
        string="Fecha de Inicio",
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )

    end_date = fields.Date(
        string="Fecha Final",
        required=True,
        default=lambda self: (
            fields.Date.today() + relativedelta(months=+1, day=1, days=-1)
        ),
    )

    partner_ids = fields.Many2many(comodel_name="res.partner", string="Contacto")
    patient_ids = fields.Many2many(comodel_name="hms.patient", string="Pacientes")
    physician_ids = fields.Many2many(comodel_name="hms.physician", string="Medicos")
    journal_ids = fields.Many2many(comodel_name="account.journal")

    def _prepare_report_aged(self):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "partner_ids": self.partner_ids.ids or [],
            "journal_ids": self.journal_ids.ids or [],
            "patient_ids": self.patient_ids.ids or [],
            "physician_ids": self.physician_ids.ids or [],
        }

    def get_report(self):
        data = self._prepare_report_aged()
        return self.env.ref("cms_account_reports.report_aged_report").report_action(
            self, data=data
        )
