from odoo import fields,api,models

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    stage_lines = fields.One2many('crm.sub.stage', 'stage_id')

class CrmSubStage(models.Model):
    _name = 'crm.sub.stage'

    name = fields.Char('Name')
    stage_id = fields.Many2one('crm.stage', 'Stage ID')