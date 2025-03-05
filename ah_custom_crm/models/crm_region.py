from odoo import fields,api,models

class CrmRegion(models.Model):
    _name = 'crm.region'

    name = fields.Char('Name')