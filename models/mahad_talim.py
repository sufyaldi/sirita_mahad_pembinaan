# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MahadTalimClass(models.Model):
    _name = 'mahad.talim.class'
    _description = "Halaqah / Kelas Ta'lim Ma'had"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nama Halaqah / Kelas", required=True, tracking=True)
    type = fields.Selection([
        ('tahfizh', 'Tahfizh Al-Qur\'an'),
        ('arab', 'Bahasa Arab'),
        ('inggris', 'Bahasa Inggris'),
        ('fiqih_akhlaq', 'Fiqih & Akhlaq'),
    ], string="Jenis Ta'lim", required=True, default='tahfizh', tracking=True)
    musyrif_id = fields.Many2one('hr.employee', string="Musyrif / Pengampu", tracking=True)
    semester = fields.Selection([
        ('ganjil', 'Semester Ganjil'),
        ('genap', 'Semester Genap'),
    ], string="Semester", default='ganjil', required=True)
    academic_year = fields.Char(string="Tahun Akademik", default="2026/2027", required=True)
    student_ids = fields.Many2many('res.partner', string="Anggota Mahasantri", domain="[('is_student', '=', True)]")
    student_count = fields.Integer(string="Jumlah Mahasantri", compute='_compute_student_count', store=True)
    description = fields.Text(string="Keterangan / Silabus")
    active = fields.Boolean(default=True)

    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)

class MahadTalimRecord(models.Model):
    _name = 'mahad.talim.record'
    _description = "Buku Kendali Hafalan & Ta'lim Mahasantri"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string="Kode Record", required=True, copy=False, readonly=True, default="Baru", tracking=True)
    student_id = fields.Many2one('res.partner', string="Mahasantri", required=True, domain="[('is_student', '=', True)]", tracking=True)
    class_id = fields.Many2one('mahad.talim.class', string="Halaqah / Kelas", required=True)
    date = fields.Date(string="Tanggal", default=fields.Date.context_today, required=True)
    category = fields.Selection([
        ('ziyadah', 'Ziyadah (Setoran Baru)'),
        ('murajaah', 'Muraja\'ah (Pengulangan)'),
        ('penilaian_harian', 'Penilaian Keaktifan'),
        ('ujian_semester', 'Ujian Semester Ma\'had'),
    ], string="Kategori Record", required=True, default='ziyadah')
    surah_juz_topic = fields.Char(string="Surah / Juz / Topik Materi", required=True, help="Contoh: Juz 30 (Q.S. An-Naba' 1-20)")
    grade_status = fields.Selection([
        ('mumtaz', 'Mumtaz (Sangat Baik / Lulus)'),
        ('jayyid_jiddan', 'Jayyid Jiddan (Baik Sekali)'),
        ('jayyid', 'Jayyid (Baik)'),
        ('rasib', 'Rasib (Mengulang)'),
    ], string="Predikat / Status", default='mumtaz', required=True, tracking=True)
    notes = fields.Text(string="Catatan Pembina / Musyrif")

    @api.depends('name', 'student_id', 'surah_juz_topic')
    def _compute_display_name(self):
        for rec in self:
            std = rec.student_id.name or 'Mahasantri'
            topic = rec.surah_juz_topic or ''
            kode = rec.name or 'Baru'
            if topic:
                rec.display_name = f"{kode} - {std} ({topic})"
            else:
                rec.display_name = f"{kode} - {std}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Baru') in ['Baru', 'NEW', False]:
                seq = self.env['ir.sequence'].next_by_code('mahad.talim.record')
                if not seq:
                    today = fields.Date.today()
                    # Fallback jika ir.sequence belum dibuat
                    seq = f"TLM/{today.strftime('%Y%m')}/{self.search_count([]) + 1:04d}"
                vals['name'] = seq
        return super().create(vals_list)

