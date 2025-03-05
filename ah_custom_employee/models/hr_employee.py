from odoo import fields, api, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    acting_charge_held2 = fields.Many2one('hr.job', relation='acting_charge_held2', string='Acting Charge Held')
    additional_charge_held = fields.Many2one('hr.job',  relation='additional_charge_held', string='Additional Charge Held')