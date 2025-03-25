from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import datetime

class ProjectTaskExecutiveAppraisal(models.Model):
    _inherit = 'project.task.executive.appraisal'

    total_marks_obtain = fields.Float('Marks Obtained', compute='_compute_totals')
    total_out_of_marks = fields.Float('Ouf Of Marks', compute='_compute_totals')
    total_grade = fields.Char('Grade', compute='_compute_totals')
    slash = fields.Char('Slash', default='/')

    appraiser_review = fields.Html('Appraiser Review')
    reviewer_evaluation = fields.Html('Reviewer Evaluation')

    def _compute_totals(self):
        for rec in self:
            total_marks_out_of = 0
            total_marks_obtain = 0
            grade = None

            if rec.project_task_executive_appraisal_kra_ids:
                for line in rec.project_task_executive_appraisal_kra_ids:
                    total_marks_out_of += line.marks_of_out
                    total_marks_obtain += line.marks

            if rec.project_task_soft_skills_kra_ids:
                for line in rec.project_task_soft_skills_kra_ids:
                    total_marks_out_of += line.marks_of_out
                    total_marks_obtain += line.marks

            if rec.project_task_outstanding_achievements_kra_ids:
                for line in rec.project_task_outstanding_achievements_kra_ids:
                    total_marks_out_of += line.marks_of_out
                    total_marks_obtain += line.marks

            if total_marks_obtain >= 80:
                grade = 'OS'
            if total_marks_obtain >= 70 and total_marks_obtain < 80:
                grade = 'EE'
            if total_marks_obtain >= 60 and total_marks_obtain < 70:
                grade = 'ME'
            if total_marks_obtain >= 50 and total_marks_obtain < 60:
                grade = 'BE'
            if total_marks_obtain < 50:
                grade = 'SD'

            rec.total_out_of_marks = total_marks_out_of
            rec.total_marks_obtain = total_marks_obtain
            rec.total_grade = grade


    @api.constrains('employee_id', 'from_date', 'to_date')
    def constrains_employee_id(self):
        for record in self:
            record.project_task_executive_appraisal_kra_ids.unlink()
            record.project_task_soft_skills_kra_ids.unlink()
            record.project_task_outstanding_achievements_kra_ids.unlink()

            kpi_type_id = self.env['kra.type'].search([
                ('hr_department', '=', record.employee_id.department_id.id)
            ])
            if kpi_type_id:
                employee_kra = self.env['employee.kra'].sudo().search([
                    ('kra_type_id', '=', kpi_type_id.id)
                ])
                if employee_kra:
                    kpi_ids = employee_kra.kra_question_ids
                    
                    from_datetime = datetime.combine(self.from_date, datetime.min.time())  # Converts to datetime at 00:00:00
                    to_datetime = datetime.combine(self.to_date, datetime.max.time())
                    
                    total_tasks = self.env['project.task'].sudo().search([
                        ('employee_id', '=', self.employee_id.id),
                        ('start_date', '>=', from_datetime),
                        ('end_date', '<=', to_datetime)
                    ])

                    for kpi in kpi_ids:
                        kpi_tasks = self.env['project.task'].sudo().search([
                            ('employee_id', '=', self.employee_id.id),
                            ('kra_check', '=', kpi.id),
                            ('start_date', '>=', from_datetime),
                            ('end_date', '<=', to_datetime)
                        ])
                        if len(kpi_tasks) > 0:
                            total_marks_percent = 0
                            for task in kpi_tasks:
                                total_marks_percent += (task.marks / 100) * task.task_weightage

                            total_marks_percent = (total_marks_percent / kpi.kra_weightage) * 100

                            kpi_line = record.project_task_executive_appraisal_kra_ids.create({
                                'kra_question_id': kpi.id,
                                'kra_description': kpi.description,
                                'kra_weightage': (len(kpi_tasks) / len(total_tasks)) * 100,
                                'executive_appraisal_id': record.id
                            })
                            kpi_line.write({
                                'marks_of_out': (kpi_line.kra_weightage / 100) * 50,
                            })

                            kpi_line.write({
                                'marks': (kpi_line.marks_of_out * total_marks_percent) / 100
                            })


            project_task_soft_skills = self.env['project.task.soft.skills'].sudo().search([])
            for lines in project_task_soft_skills:
                self.env['project.task.soft.skills.kra'].sudo().create({
                    'soft_skills_id': lines.id,
                    'marks': 0.0,
                    'marks_of_out': lines.marks,
                    'executive_appraisal_id': record.id,
                })

            project_task_outstanding_achievements = self.env['project.task.outstanding.achievements'].sudo().search([])
            for lines in project_task_outstanding_achievements:
                self.env['project.task.outstanding.achievements.kra'].sudo().create({
                    'outstanding_achievements_id': lines.id,
                    'marks': 0.0,
                    'marks_of_out': lines.marks,
                    'executive_appraisal_id': record.id,
                })

class ProjectTaskSoftSkillsKRAModel(models.Model):
    _inherit = 'project.task.soft.skills.kra'

    @api.onchange('marks')
    def onchange_marks(self):
        for rec in self:
            if rec.marks > rec.marks_of_out:
                raise ValidationError(f'Marks cannot be greater than {rec.marks_of_out}')


class ProjectTaskOutstandingAchievementsKRAModel(models.Model):
    _inherit = 'project.task.outstanding.achievements.kra'

    @api.onchange('marks')
    def onchange_marks(self):
        for rec in self:
            if rec.marks > rec.marks_of_out:
                raise ValidationError(f'Marks cannot be greater than {rec.marks_of_out}')