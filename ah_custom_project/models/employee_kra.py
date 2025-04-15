from odoo import models, api, fields

class EmployeeKra(models.Model):
    _inherit = 'employee.kra'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'