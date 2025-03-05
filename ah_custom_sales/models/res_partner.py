from odoo import fields, api, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_rent = fields.Boolean('Is Rent?')
    rent_per_month = fields.Float('Rent per Month')
    number_of_months = fields.Integer('Number of Months')
    total_rent = fields.Float('Total Rent')

    increase_in_rent = fields.Float('Increase In Rent %')
    total_rent_after_increase = fields.Float("Rent After Increase")

    remarks = fields.Char('Remarks')

    @api.onchange('rent_per_month', 'number_of_months', 'total_rent', 'increase_in_rent')
    def onchange_rent(self):
        self.total_rent = self.rent_per_month * self.number_of_months
        increase_amount = (self.total_rent / 100) * self.increase_in_rent
        self.total_rent_after_increase = self.total_rent + increase_amount