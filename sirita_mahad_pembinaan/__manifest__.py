# -*- coding: utf-8 -*-
{
    'name': "Ma'had Al-Jami'ah IAIN Parepare — Pembinaan Kesantrian (Akademik, Izin & Takzir)",
    'version': '20.0.1.0.0',
    'category': 'Education / Ma\'had',
    'summary': 'Pengembangan Khusus Ma\'had Al-Jami\'ah PTKIN: Ta\'lim, Hafalan, Izin Pesiar/Bermalam & Poin Kedisiplinan',
    'description': """
        Modul Ekstensi Khusus Ma'had Al-Jami'ah IAIN Parepare:
        1. Manajemen Ta'lim & Buku Kendali Hafalan (Ziyadah/Muraja'ah).
        2. Syahadah / Sertifikat Kelulusan Ma'had (Syarat Skripsi SIAKAD API).
        3. Alur Perizinan Pesiar & Bermalam dengan QR Gate Control (REST API).
        4. Sistem Poin Pelanggaran Kedisiplinan & Takzir Edukatif (SP-1, SP-2, SP-3).
        5. Otomatisasi Cron Keterlambatan & Generasi Tagihan Massal BLU.
    """,
    'author': 'sufyALDI | TIPD IAIN Parepare | Forum PTIPD PTKIN',
    'website': 'https://iainpare.ac.id',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'website', 'sirita_mahad', 'mail'],
    'data': [
        'security/ir.access.csv',
        'data/ir_cron_data.xml',
        'views/mahad_official_views.xml',
        'views/mahad_talim_views.xml',
        'views/report_syahadah_views.xml',
        'views/mahad_syahadah_views.xml',
        'views/syahadah_web_views.xml',
        'views/mahad_permit_views.xml',
        'views/mahad_penalty_views.xml',
        'views/mahad_billing_wizard_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
