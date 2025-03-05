from odoo import fields,api,models

class AccountMove(models.Model):
    _inherit = 'account.move'

    cheque_number = fields.Char('Cheque Number')
    bpv_number = fields.Char('BPV/CPV Number')

    ref = fields.Char(string='Narration', copy=False, tracking=True)

    is_entry_reversed = fields.Boolean('Is Entry Reversed', default=False)
