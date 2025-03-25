from odoo import models, fields, api
from odoo.http import request
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import json


class TicketDashboard(models.Model):
    _inherit = 'ticket.dashboard'

    @api.model
    def get_ticket_table_data(self, team_leader, team, assign_user, filter_date, start_date, end_date):
        ticket_obj = self.env['sh.helpdesk.ticket'].sudo().search(
            [], order='id desc', limit=1)
        uid = request.session.uid
        user = request.env['res.users'].sudo().browse(uid)
        cids = request.httprequest.cookies.get('cids', str(user.company_id.id))
        cids = [int(cid) for cid in cids.split(',')]
        company_id = self.env.company
        ticket_data_dic = {}
        ticket_data_list = []
        for stage in company_id.dashboard_tables:
            doman = []
            if filter_date == 'today':

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    datetime.now().date().strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif filter_date == 'yesterday':

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                prev_day = (datetime.now().date() -
                            relativedelta(days=1)).strftime('%Y/%m/%d 00:00:00')
                dt_flt1.append(prev_day)
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                prev_day = (datetime.now().date() -
                            relativedelta(days=1)).strftime('%Y/%m/%d 23:59:59')
                dt_flt2.append(prev_day)
                doman.append(tuple(dt_flt2))

            elif filter_date == 'weekly':  # current week

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append((datetime.now().date(
                ) - relativedelta(weeks=1, weekday=0)).strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif filter_date == 'prev_week':  # Previous week

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append((datetime.now().date(
                ) - relativedelta(weeks=2, weekday=0)).strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append((datetime.now().date(
                ) - relativedelta(weeks=1, weekday=6)).strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif filter_date == 'monthly':  # Current Month

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date()).strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif filter_date == 'prev_month':  # Previous Month

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date() - relativedelta(months=1)).strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt2))

            elif filter_date == 'cur_year':  # Current Year

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date()).strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif filter_date == 'prev_year':  # Previous Year

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date() - relativedelta(years=1)).strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt2))
            elif filter_date == 'custom':
                if start_date and end_date:
                    dt_flt1 = []
                    dt_flt1.append('create_date')
                    dt_flt1.append('>=')
                    dt_flt1.append(datetime.strptime(
                        str(start_date), DEFAULT_SERVER_DATE_FORMAT).strftime("%Y/%m/%d"))
                    doman.append(tuple(dt_flt1))

                    dt_flt2 = []
                    dt_flt2.append('create_date')
                    dt_flt2.append('<=')
                    dt_flt2.append(datetime.strptime(
                        str(end_date), DEFAULT_SERVER_DATE_FORMAT).strftime("%Y/%m/%d"))
                    doman.append(tuple(dt_flt2))
            if team and team not in [None, False, ""] and int(team) != 0:
                doman.append(('team_id', '=', int(team)))
            elif team and team not in [None, False, ""] and int(team) == 0:
                if self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_team_leader') and self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_user') and not self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_manager'):
                    team_ids = self.env['sh.helpdesk.team'].sudo().search(
                        ['|', ('team_head', '=', self.env.user.id), ('team_members', 'in', [self.env.user.id])])
                    doman.append(('team_id', 'in', team_ids.ids))
                elif not self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_team_leader') and self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_user') and not self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_manager'):
                    team_ids = request.env['sh.helpdesk.team'].sudo().search(
                        [('team_members', 'in', [self.env.user.id])])
                    doman.append(('team_id', 'in', team_ids.ids))
            if team_leader and team_leader not in [None, False, ""] and int(team_leader) != 0:
                doman.append(('team_head', '=', int(team_leader)))
            elif team_leader and team_leader not in [None, False, ""] and int(team_leader) == 0:
                if self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_team_leader') and self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_user') and not self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('|'))
                    doman.append(('team_head', '=', self.env.user.id))
                    doman.append(('user_id', '=', self.env.user.id))
                    doman.append(('sh_user_ids', 'in', [self.env.user.id]))
            if assign_user and assign_user not in [None, False, ""] and int(assign_user) != 0:
                doman.append(('|'))
                doman.append(('user_id', '=', int(assign_user)))
                doman.append(('sh_user_ids', 'in', [int(assign_user)]))
            elif assign_user and assign_user not in [None, False, ""] and int(assign_user) == 0:
                if self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_team_leader') and self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_user') and not self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('|'))
                    doman.append(('user_id', '=', self.env.user.id))
                    doman.append(('sh_user_ids', 'in', [self.env.user.id]))
                    doman.append(('team_head', '=', self.env.user.id))
                elif not self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_team_leader') and self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_user') and not self.env.user.has_group(
                        'sh_all_in_one_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('user_id', '=', self.env.user.id))
                    doman.append(('sh_user_ids', 'in', [self.env.user.id]))
            ticket_list = []
            doman.append(('stage_id', '=', stage.id))
            doman.append(('company_id', 'in', cids))
            search_tickets = ticket_obj.sudo().search(doman)
            if search_tickets:
                for ticket in search_tickets:
                    create_date = datetime.strftime(ticket.create_date, "%Y-%m-%d %H:%M:%S")
                    write_date = datetime.strftime(ticket.write_date, "%Y-%m-%d %H:%M:%S")
                    ticket_dic = {
                        'ticket_id': ticket.id,
                        'ticket_no': ticket.name,
                        'partner_name': ticket.partner_id.name_get()[0][1] if ticket.partner_id else None,
                        'partner_mobile': ticket.partner_id.mobile,
                        'partner_id': ticket.partner_id.id,
                        'create_date': create_date,
                        'write_date': write_date,
                        'user_id': ticket.user_id.name,
                    }
                    ticket_list.append(ticket_dic)
            search_stage = self.env['helpdesk.stages'].sudo().search([
                ('id', '=', stage.id)
            ], limit=1)
            if search_stage:
                ticket_data_dic.update({search_stage.name: ticket_list})
                ticket_data_list.append(search_stage.name)
        return self.env['ir.ui.view'].with_context()._render_template('sh_all_in_one_helpdesk.ticket_dashboard_tbl', {
            'ticket_data_dic': ticket_data_dic,
            'ticket_data_list': ticket_data_list,
        })