from odoo import fields, api, models
from odoo.exceptions import ValidationError

class HrJobCase(models.Model):
    _inherit = 'hr.job.case'

    @api.onchange('start_date', 'end_date')
    def onchange_start_date(self):
        if self.start_date and self.start_date < fields.Date.today():
            raise ValidationError('Start date could not be less than today\'s date')
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('End date could not be less than start date')
