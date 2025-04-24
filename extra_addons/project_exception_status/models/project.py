from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectStatus(models.Model):
    _inherit = 'project.status'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=lambda self: self._get_next_sequence(),
        help='Sequence order for the status stages. Lower numbers come first.'
    )

    @api.model
    def _get_next_sequence(self):
        """Get the next available sequence number"""
        last_seq = self.search([], order='sequence desc', limit=1).sequence
        return (last_seq or 0) + 10


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def write(self, vals):
        """Override write to check status changes"""
        if 'project_status' in vals:
            for record in self:
                new_status = self.env['project.status'].browse(vals['project_status'])
                current_status = record.project_status

                if current_status and new_status:  # Only check if both statuses exist
                    if not self.env.user.has_group('project_exception_status.group_project_status'):
                        if new_status.status_sequence < current_status.status_sequence:
                            raise ValidationError(_(
                                'Vous n êtes pas autorisé à déplacer le projet vers un statut précédent.'
                            ).format(
                                current_status.name, current_status.status_sequence,
                                new_status.name, new_status.status_sequence
                            ))
        return super(ProjectProject, self).write(vals)
