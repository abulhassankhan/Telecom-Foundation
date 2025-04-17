from odoo import fields,models,api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _get_default_user_ids(self):
        default_users = self.env['project.default.users'].search([])
        return default_users.mapped('user_id')

    kra_type_ids = fields.Many2one(comodel_name='kra.type', related="project_id.kra_type_ids", string="Type")
    kpi_description = fields.Text(string='KPI Description', related='kra_check_ids.description')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', store=True)
    create_user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    parent_task_id = fields.Many2one('project.task', 'Task', related='parent_id')
    show_user_ids = fields.Many2many('res.users', string='Users', default=_get_default_user_ids)
    is_readonly = fields.Boolean(compute='_compute_is_readonly', string='Is Read-Only')
    priority_check = fields.Selection(selection=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], string="Priority", required=False)
    presidents_priority = fields.Boolean(string="P&CEO Priority")
    end_date = fields.Datetime(string="End Date", tracking=True, required=True)



    @api.depends('user_id')
    def _compute_is_readonly(self):
        for record in self:
            record.is_readonly = record.user_id != self.env.user


    @api.onchange('start_date', 'end_date')
    def onchange_dates(self):
        if self.start_date and self.project_id.start_date:
            if self.start_date < self.project_id.start_date:
                raise ValidationError('Start date should be greater than project start date')
            if self.parent_id:
                if self.start_date < self.parent_id.start_date:
                    raise ValidationError('Start date should be greater than task start date')

            # Ensure end_date and project_id.end_date are valid datetime objects
        if self.end_date and self.project_id.end_date:
            if self.end_date > self.project_id.end_date:
                raise ValidationError('End date cannot be greater than project end date')
            if self.parent_id:
                if self.end_date > self.parent_id.end_date:
                    raise ValidationError('End date cannot be greater than task end date')


    @api.onchange('task_weightage')
    def onchange_task_weightage(self):
        print('tasks')
        # tasks = self.env['project.task'].search([
        #     ('project_id', '=', self.project_id.id)
        # ])
        # project_weightage = self.project_id.kra_weightage_id
        # tasks_weightage = sum(tasks.mapped('task_weightage'))
        # remaining_weightage = project_weightage - tasks_weightage
        # tasks_weightage = tasks_weightage + self.task_weightage
        tasks = self.env['project.task'].search([
            ('project_id', '=', self.project_id.id),
            ('employee_id', '=', self.employee_id.id)
        ])
        project_weightage = self.project_id.kra_weightage_id
        tasks_weightage = sum(tasks.mapped('task_weightage'))
        remaining_weightage = project_weightage - tasks_weightage
        tasks_weightage = tasks_weightage + self.task_weightage

        if tasks_weightage > project_weightage:
            raise ValidationError(f'Remaining weightage is {remaining_weightage}')

    @api.depends('marks')
    @api.constrains('marks')
    def constrains_marks(self):
        for record in self:
            # project_task = self.env['project.task'].sudo().search(
            #     [('project_id', '=', record.project_id.id), ('employee_id', '=', record.employee_id.id)])
            # marks_check = 0.0
            # for lines in project_task:
            #     marks_check += lines.marks
            # if marks_check > 100:
            #     raise ValidationError('The marks must exceed 100%. Please adjust it accordingly.')
            # if record.marks > 100:
            #     raise ValidationError('The marks must exceed 100%. Please adjust it accordingly.')
            if record.marks > 100:
                raise ValidationError('Marks could not be greater than 100')
            record.kpi_obtain_marks = ((record.marks / 100) * record.task_weightage)
            obtain_marks_total = 0.0
            kpi_weightage_total = 0.0
            project_task_check = self.env['project.task'].sudo().search(
                [('employee_id', '=', record.employee_id.id), ('kra_check', '=', record.kra_check.id)])
            for project_task in project_task_check:
                obtain_marks_total += project_task.kpi_obtain_marks
                kpi_weightage_total = project_task.kpi_weightage_check
            if kpi_weightage_total > 0:
                record.kpi_obtain_marks_of_out = obtain_marks_total / kpi_weightage_total
            else:
                record.kpi_obtain_marks_of_out = 0.0

    @api.ondelete(at_uninstall=False)
    def ondelete_project_task(self):
        for rec in self:
        # raise ValidationError('You cannot delete this task')
            if rec.create_uid != self.env.user:
                raise ValidationError('You cannot delete this task')

    @api.constrains('active')
    def onarchive_project_task(self):
        for rec in self:
            if rec.active != True and rec.create_uid != self.env.user:
                raise ValidationError('You cannot archive this task')

    @api.depends('start_date', 'end_date', 'stage_id')
    @api.constrains('start_date', 'end_date', 'stage_id')
    @api.onchange('start_date', 'end_date', 'stage_id')
    def compute_delayed_advanced_duration(self):
        current_date = datetime.now().date()
        project_task = self.env['project.task'].sudo().search([])
        for record in project_task:
            if record.start_date and record.end_date and record.actual_end_date:
                task_stage_name = record.stage_id.name.replace(" ", "").lower()
                if task_stage_name == 'completed':
                    record.delayed_advanced_duration = 0
                    if record.end_date and record.start_date:
                        if (record.end_date.date() - current_date).days > 0:
                            record.delayed_advanced_duration = f'{str(record.end_date.date() - record.actual_end_date.date())} Advanced'
                        else:
                            record.delayed_advanced_duration = f'{str(record.end_date.date() - record.actual_end_date.date())} Delayed'
                else:
                    record.delayed_advanced_duration = 0
                    if record.end_date and record.start_date:
                        if (record.end_date.date() - current_date).days > 0:
                            record.delayed_advanced_duration = f'{str(record.end_date.date() - current_date)} Advanced'
                        else:
                            record.delayed_advanced_duration = f'{str(record.end_date.date() - current_date)} Delayed'
            else:
                record.delayed_advanced_duration = False

    @api.constrains('project_task_hr_kra_ids', 'project_task_hr_kra_ids.kra_weightage')
    def check_constrains_kpis(self):
        print('Method (check_constrains_kpis) override')


    @api.constrains('employee_id')
    def compute_employee_id(self):
        for record in self:
            # project_task = self.env['project.task'].sudo().search(
            #     [('project_id', '=', record.project_id.id), ('employee_id', '=', record.employee_id.id)])
            # kra_weightage_check = 0.0
            # for task_lines in project_task:
            #     for lines in task_lines.project_task_hr_kra_ids:
            #         kra_weightage_check += lines.kra_weightage
            # if kra_weightage_check > 100:
            #     raise UserError(f'The total KRA weightage for the employee cannot exceed 100%. Current total: {kra_weightage_check}%')
            if not record.employee_id.user_id:
                raise UserError('The manager must have a user assigned. (Employee Form -> HR Settings Tab -> Related User Fields Is Null)')
            record.users_id = record.employee_id.user_id.id
            record.user_name = self.env.user.id

    @api.constrains('project_id')
    @api.onchange('project_id')
    def _onchange_project_id(self):
        for record in self:
            if record.project_id:
                employee_kra_question_ids = record.project_id.employee_kra_question_ids
                if employee_kra_question_ids:
                    employee_kra_question_id = employee_kra_question_ids[0]
                    project_task_hr_kra = self.env['project.task.hr.kra'].sudo().search(
                        [('project_task_id', '=', record.id)])
                    if project_task_hr_kra:
                        project_task_hr_kra.write({
                            'kra_question_id': employee_kra_question_id.id,
                            'kra_description': employee_kra_question_id.description,
                            'kra_weightage': employee_kra_question_id.kra_weightage,
                            'project_task_id': record.id,
                        })
                    else:
                        self.env['project.task.hr.kra'].sudo().create({
                            'kra_question_id': employee_kra_question_id.id,
                            'kra_description': employee_kra_question_id.description,
                            'kra_weightage': employee_kra_question_id.kra_weightage,
                            'project_task_id': record.id,
                        })
                if record.project_id.kra_type_ids:
                    record.department_ids = [(6, 0, record.project_id.kra_type_ids.mapped('hr_department').ids)]
                    return {
                        'domain': {
                            'employee_id': [
                                ('department_id', 'in', record.project_id.kra_type_ids.mapped('hr_department').ids)],
                        }
                    }
                else:
                    record.department_ids = False
                    return {
                        'domain': {
                            'employee_id': [],
                        }
                    }
            else:
                record.department_ids = False
                return {
                    'domain': {
                        'employee_id': [],
                    }
                }


