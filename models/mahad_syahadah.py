# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MahadSyahadah(models.Model):
    _name = 'mahad.syahadah'
    _description = "Syahadah / Sertifikat Kelulusan Ma'had"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nomor Syahadah", required=True, default="NEW", copy=False, tracking=True)
    student_id = fields.Many2one('res.partner', string="Mahasantri", required=True, domain="[('is_student', '=', True)]", tracking=True)
    nim = fields.Char(string="NIM", related="student_id.ref", store=True)
    issue_date = fields.Date(string="Tanggal Terbit", default=fields.Date.context_today, required=True)
    academic_year = fields.Char(string="Tahun Akademik", default="2026/2027", required=True)
    predikat = fields.Selection([
        ('mumtaz', 'Mumtaz (Sangat Memuaskan)'),
        ('jayyid_jiddan', 'Jayyid Jiddan (Memuaskan)'),
        ('jayyid', 'Jayyid (Baik)'),
    ], string="Predikat Kelulusan", default='mumtaz', required=True, tracking=True)
    tahfizh_target_achieved = fields.Char(string="Capaian Hafalan", default="Juz 30 Mutqin")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Diterbitkan / Lulus'),
        ('cancelled', 'Dibatalkan'),
    ], string="Status", default='draft', tracking=True)
    is_unlocked_for_skripsi = fields.Boolean(string="Buka Kunci Syarat Skripsi (SIAKAD)", compute='_compute_unlocked', store=True)
    notes = fields.Text(string="Keterangan Tambahan")

    @api.depends('state')
    def _compute_unlocked(self):
        for rec in self:
            rec.is_unlocked_for_skripsi = (rec.state == 'validated')

    @api.model
    def create(self, vals):
        if vals.get('name', 'NEW') == 'NEW':
            vals['name'] = self.env['ir.sequence'].next_by_code('mahad.syahadah') or 'SYH/' + fields.Date.today().strftime('%Y') + '/001'
        return super(MahadSyahadah, self).create(vals)

    def action_validate(self):
        self.write({'state': 'validated'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
