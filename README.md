# Modul Pembinaan Kesantrian Ma'had Al-Jami'ah PTKIN
## (sirita_mahad_pembinaan)

Modul ekstensi Odoo yang dirancang untuk standardisasi tata kelola kurikulum kepesantrenan, perizinan santri, dan penegakan kedisiplinan di lingkungan Ma'had Al-Jami'ah Perguruan Tinggi Keagamaan Islam Negeri (PTKIN).

Modul ini beroperasi berdampingan dengan modul manajemen hunian asrama (sirita_mahad) guna melengkapi ekosistem pembinaan karakter, spiritualitas, dan akademik mahasantri.

---

### Informasi Modul
- Nama Teknis: sirita_mahad_pembinaan
- Nama Aplikasi: Ma'had Al-Jami'ah PTKIN — Pembinaan Kesantrian (Akademik, Izin & Takzir)
- Kategori: Education / Ma'had
- Versi: 20.0.1.0.0
- Lisensi: LGPL-3
- Penulis / Author: sufyALDI | TIPD IAIN Parepare
- Dependensi: base, web, mail, sirita_mahad

---

### Ruang Lingkup dan Fitur Utama

#### 1. Akademik, Halaqah Ta'lim & Hafalan Al-Qur'an
- Halaqah / Kelas Ta'lim:
  Pengelompokan mahasantri ke dalam kelas ta'lim (Al-Qur'an dan Kitab Kuning) berdasarkan semester dan tahun akademik, dilengkapi penugasan Musyrif/Musyrifah pengampu halaqah.
- Buku Kendali Hafalan:
  Pencatatan rekam jejak setoran hafalan santri (Ziyadah dan Muraja'ah), meliputi Surah, rentang ayat, kelancaran tajwid, nilai kelayakan (mutqin), serta paraf digital musyrif.

#### 2. Sertifikat Syahadah Ma'had (Syarat Ujian Akademik SIAKAD)
- Penerbitan sertifikat kelulusan program Ma'had Al-Jami'ah bagi santri yang telah menuntaskan target kurikulum dan hafalan.
- Validasi berjenjang hingga pengesahan oleh Pimpinan/Mudir Ma'had.
- REST API SIAKAD (/api/mahad/syahadah/status):
  Layanan integrasi API untuk memeriksa kelayakan mahasiswa secara langsung (real-time) sebagai prasyarat pendaftaran ujian skripsi/tugas akhir di SIAKAD perguruan tinggi.

#### 3. Alur Perizinan Pesiar & Bermalam (QR Gate Scanner)
- Pengajuan izin santri untuk keluar asrama harian (pesiar) maupun izin bermalam/pulang kampung.
- Persetujuan bertingkat oleh Musyrif/Musyrifah pendamping.
- Token dan QR Code unik untuk setiap surat izin yang disetujui.
- REST API Scanner Gerbang (/api/mahad/permit/scan_qr):
  Integrasi dengan pos keamanan gerbang kampus untuk validasi check-out saat santri keluar dan check-in saat kembali ke asrama.
- Cron Otomatis:
  Pendeteksian keterlambatan izin santri secara otomatis dan penandaan status overstay.

#### 4. Tata Tertib, Kedisiplinan & Takzir Edukatif
- Master Kategori Pelanggaran:
  Pengelompokan jenis pelanggaran dengan bobot poin terstandar (Ringan: 1-5 poin, Sedang: 6-15 poin, Berat: lebih dari 15 poin).
- Rekam Jejak Pelanggaran:
  Pencatatan kasus pelanggaran tata tertib oleh musyrif disertai saksi dan bukti temuan.
- Takzir Edukatif:
  Pemberian sanksi yang berorientasi pada pembinaan karakter dan spiritualitas (hafalan surat pilihan, tugas kebersihan masjid/mushalla, resume kajian kitab) tanpa kekerasan fisik.
- Akumulasi Poin & Surat Peringatan:
  Kalkulasi akumulasi poin pada profil santri yang secara otomatis memicu status Surat Peringatan (SP-1, SP-2, SP-3) dan pemanggilan orang tua/wali.

#### 5. Wizard Penagihan Massal Asrama
- Fitur bantuan penerbitan tagihan biaya hunian/asrama secara massal berdasarkan kriteria gedung, kamar, atau angkatan santri ke modul keuangan dan akuntansi lembaga.

---

### Struktur Direktori Modul

sirita_mahad_pembinaan/
|-- __init__.py
|-- __manifest__.py
|-- README.md
|-- controllers/
|   |-- __init__.py
|   `-- main.py                    (Endpoint REST API QR Scanner & Syahadah)
|-- data/
|   `-- ir_cron_data.xml           (Jadwal background job otomatis)
|-- models/
|   |-- __init__.py
|   |-- mahad_billing_wizard.py    (Wizard invoice tagihan massal)
|   |-- mahad_penalty.py           (Model poin pelanggaran & takzir)
|   |-- mahad_permit.py            (Model perizinan & gerbang QR)
|   |-- mahad_syahadah.py          (Model sertifikat syahadah kelulusan)
|   `-- mahad_talim.py             (Model halaqah & buku kendali hafalan)
|-- security/
|   `-- ir.access.csv              (Hak akses Musyrif, Pengelola, Mudir)
`-- views/
    |-- mahad_billing_wizard_views.xml
    |-- mahad_penalty_views.xml
    |-- mahad_permit_views.xml
    |-- mahad_syahadah_views.xml
    |-- mahad_talim_views.xml
    `-- menu.xml                   (Struktur urutan navigasi menu)

---

### Hak Akses Pengguna
Modul ini memanfaatkan sistem keamanan Odoo dengan pembagian hak akses:
1. Musyrif / User:
   Mengisi buku kendali hafalan, mencatat kehadiran halaqah ta'lim, memverifikasi permohonan izin pesiar/bermalam santri binaannya, dan mencatat pelanggaran harian.
2. Pengelola / Manager:
   Mengelola data master halaqah, mengonfirmasi data perizinan, mengelola takzir, dan menjalankan wizard tagihan massal asrama.
3. Mudir / Administrator:
   Mengesahkan Sertifikat Syahadah kelulusan ma'had, mengatur master aturan dan poin pelanggaran, memvalidasi Surat Peringatan (SP), serta mengonfigurasi otomatisasi sistem.
