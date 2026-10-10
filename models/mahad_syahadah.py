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

    # Referensi Pejabat Penandatangan Dinamis (Kepala Ma'had)
    signatory_id = fields.Many2one('mahad.official', string="Pejabat Penandatangan", default=lambda self: self._default_signatory_id(), tracking=True)
    signatory_name = fields.Char(string="Nama Penandatangan", tracking=True)
    signatory_nip = fields.Char(string="NIP Penandatangan", tracking=True)
    signatory_job = fields.Char(string="Jabatan Penandatangan", default="Kepala UPT. Ma'had Al-Jami'ah", tracking=True)
    signatory_sk = fields.Char(string="SK Pengangkatan", tracking=True)
    signature_mode = fields.Selection([
        ('qr', 'TTE QR Code Resmi (Standar Elektronik Otomatis)'),
        ('scan', 'Tanda Tangan Basah Hasil Scan (PNG Transparan)'),
        ('both', 'Kombinasi (TTE QR Code + TTD Basah Scan & Stempel)'),
    ], string="Metode Penandatanganan", default='qr', tracking=True)

    # TTE Digital Signature Token & Verifikasi
    tte_token = fields.Char(string="TTE Digital Token / Hash", readonly=True, copy=False, tracking=True)
    tte_datetime = fields.Datetime(string="Waktu Pengesahan TTE", readonly=True, copy=False)
    tte_verification_url = fields.Char(string="URL Verifikasi TTE", compute='_compute_tte_url', store=True)

    @api.model
    def _default_signatory_id(self):
        return self.env['mahad.official'].search([('is_active', '=', True)], limit=1)

    @api.onchange('signatory_id')
    def _onchange_signatory_id(self):
        if self.signatory_id:
            self.signatory_name = self.signatory_id.name
            self.signatory_nip = self.signatory_id.nip
            self.signatory_job = self.signatory_id.job_title
            self.signatory_sk = self.signatory_id.sk_number
            if self.signatory_id.signature_mode:
                self.signature_mode = self.signatory_id.signature_mode

    @api.depends('name', 'tte_token', 'nim')
    def _compute_tte_url(self):
        base_url = "https://mahad.iainpare.ac.id"
        for rec in self:
            query_param = rec.tte_token or rec.nim or rec.name
            rec.tte_verification_url = f"{base_url}/syahadah/verify?q={query_param}"

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
            if not vals.get('signatory_name') and vals.get('signatory_id'):
                official = self.env['mahad.official'].browse(vals['signatory_id'])
                if official.exists():
                    vals['signatory_name'] = official.name
                    vals['signatory_nip'] = official.nip
                    vals['signatory_job'] = official.job_title
                    vals['signatory_sk'] = official.sk_number
                    if not vals.get('signature_mode') and official.signature_mode:
                        vals['signature_mode'] = official.signature_mode
        return super(MahadSyahadah, self).create(vals_list)

    def action_validate(self):
        import hashlib
        for rec in self:
            vals = {'state': 'validated'}
            if rec.signatory_id and not rec.signatory_name:
                vals.update({
                    'signatory_name': rec.signatory_id.name,
                    'signatory_nip': rec.signatory_id.nip,
                    'signatory_job': rec.signatory_id.job_title,
                    'signatory_sk': rec.signatory_id.sk_number,
                })
            if not rec.signature_mode and rec.signatory_id and rec.signatory_id.signature_mode:
                vals['signature_mode'] = rec.signatory_id.signature_mode

            # Generate Unique TTE Token jika belum ada
            if not rec.tte_token:
                now_str = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                raw_payload = f"{rec.name}|{rec.nim}|{rec.signatory_nip}|{now_str}|IAIN_PAREPARE_MAHAD"
                hash_digest = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()[:12].upper()
                year = fields.Date.today().strftime('%Y')
                vals['tte_token'] = f"TTE-SYH-{year}-{hash_digest}"
                vals['tte_datetime'] = fields.Datetime.now()
            rec.write(vals)

    def action_cancel(self):
        self.write({'state': 'cancelled'})

