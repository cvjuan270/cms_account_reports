from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class CmsAbstractWizard(models.AbstractModel):
    _name = "cms_account_reports.abstract_wizard"
    _description = "Cms Abstract Wizard"

    start_date = fields.Date(
        string="Fecha de Inicio",
        required=True,
        default=lambda self: fields.Date.to_string(datetime.now().replace(day=1)),
    )

    end_date = fields.Date(
        string="Fecha Final",
        required=True,
        default=lambda self: fields.Date.to_string(
            (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()
        ),
    )

    partner_ids = fields.Many2many(comodel_name="res.partner", string="Contacto")
    patient_ids = fields.Many2many(comodel_name="hms.patient", string="Pacientes")
    physician_ids = fields.Many2many(comodel_name="hms.physician", string="Medicos")
    journal_ids = fields.Many2many(comodel_name="account.journal")

    def _prepare_report_data(self):
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
