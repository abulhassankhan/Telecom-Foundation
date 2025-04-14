from odoo import fields,models,api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_default_user_ids(self):
        default_users = self.env['project.default.users'].search([])
        return default_users.mapped('user_id')

    kra_type_ids = fields.Many2one(comodel_name='kra.type', string="Department", required=True)
    default_user_ids = fields.Many2many('res.users', string='Default Users', default=_get_default_user_ids)
    user_ids = fields.Many2many('res.users', string='Users', default=_get_default_user_ids, relation='project_user_rel')
    progress_count = fields.Float('Progress Count', compute='_compute_progress_count')
    task_weightage_count = fields.Float('Task Weightage Count', compute='_compute_task_weightage_count')
    project_owner_id = fields.Many2one('hr.employee', 'Project Owner')

    def _compute_progress_count(self):
        for rec in self:
            completed_tasks = self.env['project.task'].sudo().search([
                ('project_id','=',rec.id),
                ('stage_id', '=', 32)
            ])
            if not completed_tasks:
                rec.progress_count = 0
            else:
                total_tasks = self.env['project.task'].sudo().search([
                    ('project_id','=',rec.id)
                ])
                rec.progress_count = (len(completed_tasks) / len(total_tasks)) * 100


    def _compute_task_weightage_count(self):
        for rec in self:
            tasks = self.env['project.task'].sudo().search([
                ('project_id','=',rec.id)
            ])
            if not tasks:
                rec.task_weightage_count = 0
            else:
                total_task_weightage = sum(tasks.mapped('task_weightage'))
                rec.task_weightage_count = total_task_weightage


    @api.onchange('kra_type_ids')
    def onchange_kra_type_ids(self):
        if self.kra_type_ids:
            hod = self.kra_type_ids.hr_department.manager_id
            self.manager = hod.id






