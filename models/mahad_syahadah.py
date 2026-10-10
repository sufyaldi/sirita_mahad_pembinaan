# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MahadSyahadah(models.Model):
    _name = 'mahad.syahadah'
    _description = "Syahadah / Sertifikat Kelulusan Ma'had"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nomor Syahadah", required=True, default="NEW", copy=False, tracking=True)
    student_id = fields.Many2one('res.partner', string="Mahasantri", required=True, domain="[('is_student', '=', True)]", tracking=True)
    nim = fields.Char(string="NIM", related="student_id.ref", store=True)
    faculty_prodi = fields.Char(string="Fakultas / Program Studi", default="Tarbiyah / Pendidikan Agama Islam")
    issue_date = fields.Date(string="Tanggal Terbit", default=fields.Date.context_today, required=True)
    academic_year = fields.Char(string="Tahun Akademik", default="2026/2027", required=True)
    
    # Nilai Kompetensi / Kemampuan (Sesuai Format Sertifikat)
    score_quran = fields.Integer(string="Nilai Bacaan Al-Qur'an", default=85)
    score_surat_pendek = fields.Integer(string="Nilai Hafalan Surat Pendek", default=80)
    score_doa = fields.Integer(string="Nilai Hafalan Do'a Harian", default=75)
    score_ibadah = fields.Integer(string="Nilai Praktik Ibadah", default=80)

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'NEW') == 'NEW':
                seq = self.env['ir.sequence'].next_by_code('mahad.syahadah')
                vals['name'] = seq or ('SYH/' + fields.Date.today().strftime('%Y') + '/' + str(self.env['mahad.syahadah'].search_count([]) + 1).zfill(3))
        return super(MahadSyahadah, self).create(vals_list)

    def action_validate(self):
        self.write({'state': 'validated'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
