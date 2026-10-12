# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MahadOfficial(models.Model):
    _name = 'mahad.official'
    _description = "Master Data Pejabat / Kepala Ma'had Al-Jami'ah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'is_active desc, date_start desc, id desc'

    name = fields.Char(string="Nama Pejabat", required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Karyawan (HR Odoo)", tracking=True)
    nip = fields.Char(string="NIP", tracking=True)
    job_title = fields.Char(string="Jabatan", default="Kepala UPT. Ma'had Al-Jami'ah", required=True, tracking=True)
    sk_number = fields.Char(string="Nomor SK Pengangkatan", tracking=True, help="Contoh: SK Rektor No. 124 Tahun 2024")
    date_start = fields.Date(string="Mulai Menjabat", default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Akhir Masa Jabatan", tracking=True)
    is_active = fields.Boolean(string="Pejabat Aktif / Penandatangan Utama", default=False, tracking=True,
                               help="Centang jika pejabat ini menjadi penandatangan aktif default untuk syahadah baru.")
    
    signature_mode = fields.Selection([
        ('qr', 'TTE QR Code Resmi (Standar Elektronik Otomatis)'),
        ('scan', 'Tanda Tangan Basah Hasil Scan (PNG Transparan)'),
        ('both', 'Kombinasi (TTE QR Code + TTD Basah Scan & Stempel)'),
    ], string="Metode Penandatanganan", default='qr', required=True, tracking=True,
       help="Pilih bagaimana tanda tangan akan ditampilkan pada dokumen sertifikat Syahadah.")

    signature_image = fields.Binary(string="Tanda Tangan Basah Hasil Scan (PNG)", attachment=True,
                                    help="Scan tanda tangan basah format PNG transparan.")
    stamp_image = fields.Binary(string="Stempel Resmi UPT (PNG)", attachment=True,
                                help="Format PNG transparan stempel Ma'had Al-Jami'ah.")
    notes = fields.Text(string="Catatan Tambahan")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.name = self.employee_id.name
            self.nip = getattr(self.employee_id, 'identification_id', '') or ''
            if getattr(self.employee_id, 'job_title', ''):
                self.job_title = self.employee_id.job_title

    @api.constrains('is_active')
    def _check_single_active_signer(self):
        for rec in self:
            if rec.is_active:
                other_active = self.search([('id', '!=', rec.id), ('is_active', '=', True)])
                if other_active:
                    # Nonaktifkan yang lain agar selalu hanya ada 1 penandatangan aktif utama
                    other_active.write({'is_active': False})
