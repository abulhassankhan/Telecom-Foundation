from odoo import api,fields,models
from odoo.exceptions import UserError
from datetime import datetime


class PmsReport(models.Model):
    _name = 'pms.report'
    _rec_name = 'employee_id'

    def _get_kra_type_particular_department(self):
        user = self.env.user
        if user.has_group('bn_project_access_right.group_pmo_admin'):
            return "[]"
        elif user.has_group('hr.group_hr_manager'):
            return "[]"
        elif user.has_group('bn_project_access_right.group_pmo_manager'):
            employee_id = self.env.user.employee_id
            department_id = employee_id.department_id
            kra_type = self.env['kra.type'].sudo().search([('hr_department', '=', department_id.id)])
            return [('id', '=', kra_type.id)]

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    kpi_type_id = fields.Many2one('kra.type', 'Department', domain=_get_kra_type_particular_department)
    # kpi_ids = fields.Many2one('employee.kra.question', 'KPI')
    key_perfomance_ids = fields.Many2many('employee.kra.question', string='KPIs')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    department_id = fields.Many2one('hr.department', 'Hr Department')
    pms_report_lines = fields.One2many('pms.report.lines', 'pms_report_id')



    @api.onchange('kpi_type_id')
    def onchange_department_id(self):
        if self.kpi_type_id:
            self.department_id = self.kpi_type_id.hr_department
            employee_kra = self.env['employee.kra'].search([
                ('kra_type_id', '=', self.kpi_type_id.id)
            ])
            if employee_kra:
                 self.key_perfomance_ids = employee_kra.kra_question_ids.ids



    def compute_report(self):
        # if self.pms_report_lines:
        self.pms_report_lines.unlink()
        from_datetime = datetime.combine(self.from_date, datetime.min.time())  # Converts to datetime at 00:00:00
        to_datetime = datetime.combine(self.to_date, datetime.max.time())

        total_tasks = self.env['project.task'].sudo().search([
            ('employee_id', '=', self.employee_id.id),
            ('start_date', '>=', from_datetime),
            ('end_date', '<=', to_datetime)
        ])
        for kpi in self.key_perfomance_ids:
            kpi_tasks = self.env['project.task'].sudo().search([
                ('employee_id', '=', self.employee_id.id),
                ('kra_check', '=', kpi.id),
                ('start_date', '>=', from_datetime),
                ('end_date', '<=', to_datetime)
            ], order='create_date')
            total_marks_percent = 0
            first_record = None
            first_iteration = True
            if kpi_tasks:
                for task in kpi_tasks:
                    pms_report_line = self.pms_report_lines.create({
                        'kpi_id': task.kra_check.id,
                        # 'kpi_weightage'
                        'task_id': task.id,
                        'no_of_task': 1,
                        'task_weightage': task.task_weightage,
                        'task_marks': task.marks,
                        'obtain_marks_percent': (task.marks /100) * task.task_weightage,
                        'pms_report_id': self.id
                    })
                    total_marks_percent += (task.marks /100) * task.task_weightage
                    if first_iteration:
                        first_record = pms_report_line
                        # pms_report_line.write({
                        #     'kpi_weightage_percent': (len(kpi_tasks)/len(total_tasks)) * 100
                        #     'total_marks_percent': sum(obtain_marks_percent)
                        # })
                    first_iteration = False
                first_record.write({
                    'kpi_weightage_percent': (len(kpi_tasks) / len(total_tasks)) * 100,
                    'total_marks_percent': total_marks_percent,
                    'marks_out_of_100_percent': (total_marks_percent/kpi.kra_weightage) * 100,
                })
                grade = None
                if first_record.marks_out_of_100_percent >= 80:
                    grade = 'OS'
                if first_record.marks_out_of_100_percent >= 70 and first_record.marks_out_of_100_percent < 80:
                    grade = 'EE'
                if first_record.marks_out_of_100_percent >= 60 and first_record.marks_out_of_100_percent < 70:
                    grade = 'ME'
                if first_record.marks_out_of_100_percent >= 50 and first_record.marks_out_of_100_percent < 60:
                    grade = 'BE'
                if first_record.marks_out_of_100_percent < 50:
                    grade = 'SD'
                first_record.write({'grade': grade})


class PmsReportLines(models.Model):
    _name = 'pms.report.lines'

    pms_report_id = fields.Many2one('pms.report')
    kpi_id = fields.Many2one('employee.kra.question', 'KPI')
    kpi_weightage = fields.Float('KPI %')
    task_id = fields.Many2one('project.task', 'Task')
    no_of_task = fields.Float('No of Tasks')
    task_weightage = fields.Float('Task Weightage')
    task_marks = fields.Float('Marks')
    kpi_weightage_percent = fields.Float('KPI Weightage %')
    obtain_marks_percent = fields.Float('Obtain Marks %')
    total_marks_percent = fields.Float('Total Marks %')
    marks_out_of_100_percent = fields.Float('% out of 100')
    grade = fields.Char('Grade')


