
from odoo import models, fields, api, tools
from odoo.tools.safe_eval import safe_eval
import operator
import logging
from odoo.http import request
from decorator import decorator
_logger = logging.getLogger(__name__)

def login_admin_access(method):

    def login_and_check(method, self, *args, **kwargs):
        user = self.env.user
        origin = request.httprequest.remote_addr if request else 'n/a'
        log_data = (method.__name__, self.sudo().mapped('name'), user.login, user.id, origin)
        if not self.env.is_admin():
            _logger.warning('DENY access to module.%s on %s to user %s ID #%s via %s', *log_data)
            raise AccessDenied()
        _logger.info('ALLOW access to module.%s on %s to user %s #%s via %s', *log_data)
        return method(self, *args, **kwargs)
    return decorator(login_and_check, method)


class Module(models.Model):
    _inherit = "ir.module.module"

    @login_admin_access
    def button_immediate_install(self):

        _logger.info('User #%d triggered module installation', self.env.uid)

        menus_obj = self.env['ir.ui.menu'].search([],order="id desc",limit=1)
        menus_obj.write({'is_write':True})
        if request:
            request.allowed_company_ids = self.env.companies.ids
        return self._button_immediate_function(type(self).button_install)

class UsersRes(models.Model):
    _inherit = 'res.users'
    _description = 'Res Users'

    access_menu_ids= fields.Many2many('ir.ui.menu', string='Groups')
    access_report_ids = fields.Many2many('ir.actions.report', string='Groups')

    def write(self, vals):
        res = super(UsersRes, self).write(vals)
        self.env['ir.ui.menu'].load_menus(debug=1)
        return res

class GroupsRes(models.Model):
    _inherit = 'res.groups'
    _description = 'Res Groups'

    menu_ids = fields.Many2many('ir.ui.menu', string='Groups')
    report_ids = fields.Many2many('ir.actions.report', string='Groups')

    def write(self, vals):
        res = super(GroupsRes, self).write(vals)
        self.env['ir.ui.menu'].load_menus(debug=1)
        return res

class MenuIrUi(models.Model):
    _inherit="ir.ui.menu"
    _description = 'Ir Ui Menu'

    is_write = fields.Boolean('Write',default=False)

    @api.model
    @api.returns('self')
    def get_user_roots_menu(self):
        menus_list = []
        res_group = self.env['res.groups'].search([('id','in',self.env.user.groups_id.ids)])
        for menu_group in res_group:
            if menu_group.menu_ids:
                for menu in menu_group.menu_ids:
                    if menu not in menus_list:
                        menus_list.append(menu.id)

        ir_ui_menu = self.search([('id', 'not in', self.env.user.access_menu_ids.ids),('parent_id', '=', False)])

        if len(menus_list)> 0:
            ir_menu = ir_ui_menu.search([('id','not in',menus_list),('parent_id', '=', False)])
            return ir_menu
        return ir_ui_menu

    def write(self, vals):
        res = super(MenuIrUi, self).write(vals)
        request.env['ir.ui.menu'].load_menus(request.session.debug)
        return res

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):

        menus_obj = self.env['ir.ui.menu'].search([],order="id desc",limit=1)
        if menus_obj.is_write == False:
            repo_list = []
            res_user_hide=self.env['ir.ui.menu']
            user_hide = res_user_hide.search([('id', 'in', self.env.user.access_menu_ids.ids),('parent_id','=',False)])
            
            group_res=self.env['res.groups']
            res_group_menu = group_res.search([('users', 'in', self.env.user.id),('menu_ids', '!=', False)])
            reports_user = False
            reports_group = False
            
            res_user1 = self.env['res.users'].search([('id', '!=', self.env.user.id),('access_report_ids', '!=', False),('parent_id','=',False)])
            for user1 in res_user1:
                reports_user = user1.access_report_ids
                if res_user1:
                    if reports_user:
                        reports_user.create_action()

            res_user = self.env['res.users'].search([('id', '=', self.env.user.id),('access_report_ids', '!=', False),('parent_id','=',False)])
            for user in res_user:
                reports_user = user.access_report_ids
                if res_user:
                    if reports_user:
                        reports_user.unlink_action()

            res_group = self.env['res.groups'].search([('users', '=', self.env.user.id),('report_ids', '!=', False)])
            res_group1 = self.env['res.groups'].search([('users', '!=', self.env.user.id),('report_ids', '!=', False)])
            for group in res_group:
                reports_group = group.report_ids
                if res_group:
                    if reports_group:
                        reports_group.unlink_action()
                        
            for group1 in res_group1:
                reports_group1 = group1.report_ids
                if res_group1:
                    if reports_group1:
                        if res_user and res_group:
                            if reports_user:
                                repos = self.env['ir.actions.report'].search([('id', 'not in', reports_user.ids),('id', 'not in', reports_group.ids)])
                                repos.create_action()
                            else:
                                reports_group1.create_action()
                        else:
                            if reports_user:
                                repots = self.env['ir.actions.report'].search([('id', 'not in', reports_user.ids)])
                                repots.create_action()
                            else:
                                reports_group1.create_action()

            ir_act_report = self.env['ir.actions.report'].search([('users_ids', '=', self.env.user.id)])
            ir_act_report1 = self.env['ir.actions.report'].search([('users_ids', '!=', self.env.user.id)])
            if ir_act_report:
                ir_act_report.unlink_action()
            if ir_act_report1:
                if res_user and res_group and ir_act_report:
                    if reports_user or reports_group:
                        report_obj = self.env['ir.actions.report'].search([('id', 'not in', reports_user.ids),('id', 'not in', reports_group.ids),('id', 'not in', ir_act_report.ids)])
                        report_obj.create_action()
                    else:
                        ir_act_report1.create_action()
                elif res_user and res_group:
                    if reports_user or reports_group:
                        reports_group_obj = self.env['ir.actions.report'].search([('id', 'not in', reports_user.ids),('id', 'not in', reports_group.ids)])
                        reports_group_obj.create_action()
                    else:
                        ir_act_report1.create_action()
                else:
                    if reports_user or reports_group or ir_act_report:
                        if reports_group:
                            hide_report = self.env['ir.actions.report'].search([('id', 'not in', reports_group.ids)])
                            hide_report.create_action()
                        if reports_user:
                            hide_report = self.env['ir.actions.report'].search([('id', 'not in', reports_user.ids)])
                            hide_report.create_action()
                        if ir_act_report:
                            hide_report = self.env['ir.actions.report'].search([('id', 'not in', ir_act_report.ids)])
                            hide_report.create_action()

                    else:
                        ir_act_report1.create_action()

            if user_hide: 
                fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon', 'web_icon_data']
                menu_roots = self.get_user_roots_menu()
                menu_roots_data = menu_roots.read(fields) if menu_roots else []
                menu_root = {
                            'id': False,
                            'name': 'root',
                            'parent_id': [-1, ''],
                            'children': menu_roots_data,
                            'all_menu_ids': menu_roots.ids,
                        }

            elif res_group_menu: 
                fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon', 'web_icon_data']
                menu_roots = self.get_user_roots_menu()
                menu_roots_data = menu_roots.read(fields) if menu_roots else []
                menu_root = {
                            'id': False,
                            'name': 'root',
                            'parent_id': [-1, ''],
                            'children': menu_roots_data,
                            'all_menu_ids': menu_roots.ids,
                        }
              
            else:
                fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon', 'web_icon_data']
                menu_roots = self.get_user_roots()
                menu_roots_data = menu_roots.read(fields) if menu_roots else []
                menu_root = {
                    'id': False,
                    'name': 'root',
                    'parent_id': [-1, ''],
                    'children': menu_roots_data,
                    'all_menu_ids': menu_roots.ids,
                }
                
            if not menu_roots_data:
                return menu_root


            child_menus = self.search([('id', 'child_of', menu_roots.ids)])
            menus=child_menus.search([('id', 'not in', self.env.user.access_menu_ids.ids)])
            if res_group_menu: 
                menu_list = []
                for group_id in res_group_menu:
                    menu_list += group_id.menu_ids.ids
                    menus = child_menus.search([('id','not in', list(set(menu_list))),('id', 'not in', self.env.user.access_menu_ids.ids)])
            
            menu_items = menus.read(fields)

            menu_items.extend(menu_roots_data)
            menu_root['all_menu_ids'] = menus.ids  # includes menu_roots!

            menu_items_map = {menu_item["id"]: menu_item for menu_item in menu_items}
            for menu_item in menu_items:
                parent = menu_item['parent_id'] and menu_item['parent_id'][0]
                if parent in menu_items_map:
                    menu_items_map[parent].setdefault(
                        'children', []).append(menu_item)

            for menu_item in menu_items:
                menu_item.setdefault('children', []).sort(key=operator.itemgetter('sequence'))

            (menu_roots + menus)._set_menuitems_xmlids(menu_root)

            return menu_root
        else:
            menus_obj.write({'is_write':False})
            return super(MenuIrUi, self).load_menus(request.session.debug)



    





    


        

