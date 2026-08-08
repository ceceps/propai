"""Synthetic seed data for Prolov, Jawa Barat market.

Everything here is invented. Prices, addresses, and agent identities are
plausible for West Java but correspond to no real listing or person, so the
demo can be shown publicly without exposing client data.

Seed-owned rows are identified by SEED_DOMAIN, which is how the purge step
finds them without touching anything a human created.
"""

from __future__ import annotations

from decimal import Decimal

# Seed-owned accounts share this domain, which is how purge identifies them.
SEED_DOMAIN = "prolov-seed.example.com"

USERS: list[dict[str, str]] = [
    {
        "email": f"admin@{SEED_DOMAIN}",
        "full_name": "Siti Rahmawati",
        "role": "admin",
        "password": "seed-admin-pw",
        "whatsapp_number": "6281200000001",
    },
    {
        "email": f"dewi@{SEED_DOMAIN}",
        "full_name": "Dewi Kurniasih",
        "role": "agent",
        "password": "seed-agent-pw",
        "whatsapp_number": "6281200000002",
    },
    {
        "email": f"bagus@{SEED_DOMAIN}",
        "full_name": "Bagus Pratama",
        "role": "agent",
        "password": "seed-agent-pw",
        "whatsapp_number": "6281200000003",
    },
    {
        "email": f"rian@{SEED_DOMAIN}",
        "full_name": "Rian Nugroho",
        "role": "freelance",
        "password": "seed-freelance-pw",
        "whatsapp_number": "6281200000004",
    },
]

# owner_key maps to a USERS email local-part, resolved at insert time.
PROPERTIES: list[dict] = [
    {
        "owner_key": "dewi",
        "title": "Rumah Modern 2 Lantai di Setiabudi, Bandung",
        "price": Decimal("2450000000"),
        "location": "Setiabudi, Bandung",
        "status": "available",
        "description": (
            "Rumah dua lantai dengan pencahayaan alami maksimal, berada di kawasan "
            "sejuk Bandung utara. Dekat kampus dan pusat kuliner Dago."
        ),
        "specs": {
            "bedrooms": 4, "bathrooms": 3, "land_area_m2": 180,
            "building_area_m2": 220, "certificate": "SHM", "carport": 2,
            "year_built": 2021, "electricity_va": 3500,
        },
    },
    {
        "owner_key": "dewi",
        "title": "Cluster Minimalis Summarecon Bekasi",
        "price": Decimal("1150000000"),
        "location": "Marga Mulya, Bekasi Utara",
        "status": "available",
        "description": (
            "Hunian cluster dengan keamanan 24 jam, kolam renang bersama, dan akses "
            "cepat ke Tol Bekasi Barat. Cocok untuk keluarga muda."
        ),
        "specs": {
            "bedrooms": 3, "bathrooms": 2, "land_area_m2": 90,
            "building_area_m2": 110, "certificate": "SHM", "carport": 1,
            "year_built": 2023, "electricity_va": 2200,
        },
    },
    {
        "owner_key": "dewi",
        "title": "Rumah Asri Dekat Stasiun Bogor",
        "price": Decimal("875000000"),
        "location": "Bantarjati, Bogor Utara",
        "status": "available",
        "description": (
            "Sepuluh menit ke Stasiun Bogor, ideal untuk commuter Jakarta. Halaman "
            "belakang cukup luas untuk taman kecil."
        ),
        "specs": {
            "bedrooms": 3, "bathrooms": 2, "land_area_m2": 105,
            "building_area_m2": 95, "certificate": "SHM", "carport": 1,
            "year_built": 2018, "electricity_va": 1300,
        },
    },
    {
        "owner_key": "bagus",
        "title": "Ruko Tiga Lantai Jalan Margonda, Depok",
        "price": Decimal("3200000000"),
        "location": "Margonda, Depok",
        "status": "available",
        "description": (
            "Ruko strategis di jalur utama Margonda dengan lalu lintas pejalan kaki "
            "tinggi. Cocok untuk kafe, klinik, atau kantor."
        ),
        "specs": {
            "bedrooms": 0, "bathrooms": 3, "land_area_m2": 96,
            "building_area_m2": 270, "certificate": "HGB", "carport": 2,
            "year_built": 2019, "electricity_va": 5500,
        },
    },
    {
        "owner_key": "bagus",
        "title": "Apartemen Studio Full Furnished, Cimahi",
        "price": Decimal("395000000"),
        "location": "Cibeureum, Cimahi",
        "status": "available",
        "description": (
            "Unit studio siap huni, sudah termasuk perabot. Cocok untuk investasi "
            "sewa jangka pendek maupun hunian pertama."
        ),
        "specs": {
            "bedrooms": 1, "bathrooms": 1, "land_area_m2": 0,
            "building_area_m2": 28, "certificate": "SHM Sarusun", "carport": 0,
            "year_built": 2022, "electricity_va": 1300, "floor": 12,
        },
    },
    {
        "owner_key": "bagus",
        "title": "Tanah Kavling Siap Bangun, Karawang Barat",
        "price": Decimal("640000000"),
        "location": "Adiarsa, Karawang Barat",
        "status": "available",
        "description": (
            "Kavling datar siap bangun dekat kawasan industri Karawang. Akses jalan "
            "beton selebar enam meter."
        ),
        "specs": {
            "bedrooms": 0, "bathrooms": 0, "land_area_m2": 320,
            "building_area_m2": 0, "certificate": "SHM", "carport": 0,
        },
    },
    {
        "owner_key": "dewi",
        "title": "Villa Pemandangan Gunung di Lembang",
        "price": Decimal("4100000000"),
        "location": "Cikahuripan, Lembang",
        "status": "reserved",
        "description": (
            "Villa dengan pemandangan Gunung Tangkuban Perahu, kolam air hangat, dan "
            "area perapian luar ruang. Riwayat sewa harian yang kuat."
        ),
        "specs": {
            "bedrooms": 5, "bathrooms": 4, "land_area_m2": 600,
            "building_area_m2": 380, "certificate": "SHM", "carport": 4,
            "year_built": 2020, "electricity_va": 7700,
        },
    },
    {
        "owner_key": "dewi",
        "title": "Rumah Subsidi Tipe 36, Cikarang",
        "price": Decimal("285000000"),
        "location": "Cikarang Selatan, Bekasi",
        "status": "available",
        "description": (
            "Rumah tipe 36 dalam skema subsidi pemerintah, angsuran ringan dan tetap. "
            "Dekat kawasan industri Jababeka."
        ),
        "specs": {
            "bedrooms": 2, "bathrooms": 1, "land_area_m2": 72,
            "building_area_m2": 36, "certificate": "SHM", "carport": 0,
            "year_built": 2024, "electricity_va": 1300, "subsidised": True,
        },
    },
    {
        "owner_key": "bagus",
        "title": "Rumah Klasik Kolonial di Cirebon Kota",
        "price": Decimal("1780000000"),
        "location": "Kejaksan, Cirebon",
        "status": "available",
        "description": (
            "Bangunan kolonial terawat dengan langit-langit tinggi dan lantai tegel "
            "asli. Dekat Keraton Kasepuhan."
        ),
        "specs": {
            "bedrooms": 4, "bathrooms": 2, "land_area_m2": 340,
            "building_area_m2": 260, "certificate": "SHM", "carport": 2,
            "year_built": 1948, "electricity_va": 3500, "heritage": True,
        },
    },
    {
        "owner_key": "bagus",
        "title": "Gudang Logistik Dekat Tol Padalarang",
        "price": Decimal("5600000000"),
        "location": "Kertajaya, Padalarang",
        "status": "available",
        "description": (
            "Gudang bentang lebar dengan akses truk kontainer dan tinggi plafon 8 "
            "meter. Dua menit dari pintu Tol Padalarang."
        ),
        "specs": {
            "bedrooms": 0, "bathrooms": 2, "land_area_m2": 1200,
            "building_area_m2": 900, "certificate": "HGB", "carport": 0,
            "year_built": 2017, "electricity_va": 23000, "clear_height_m": 8,
        },
    },
    {
        "owner_key": "dewi",
        "title": "Rumah Tumbuh di Antapani, Bandung Timur",
        "price": Decimal("980000000"),
        "location": "Antapani, Bandung",
        "status": "available",
        "description": (
            "Rumah satu lantai dengan struktur siap ditingkatkan ke lantai dua. "
            "Lingkungan tenang, dekat sekolah dan pasar."
        ),
        "specs": {
            "bedrooms": 3, "bathrooms": 2, "land_area_m2": 120,
            "building_area_m2": 85, "certificate": "SHM", "carport": 1,
            "year_built": 2016, "electricity_va": 2200,
        },
    },
    {
        "owner_key": "bagus",
        "title": "Kost Aktif 14 Kamar Dekat Kampus, Jatinangor",
        "price": Decimal("2900000000"),
        "location": "Hegarmanah, Jatinangor",
        "status": "available",
        "description": (
            "Rumah kost berjalan dengan tingkat hunian tinggi sepanjang tahun ajaran. "
            "Berjarak jalan kaki ke dua kampus besar."
        ),
        "specs": {
            "bedrooms": 14, "bathrooms": 14, "land_area_m2": 400,
            "building_area_m2": 520, "certificate": "SHM", "carport": 2,
            "year_built": 2015, "electricity_va": 11000, "occupancy_rate": 0.93,
        },
    },
    {
        "owner_key": "dewi",
        "title": "Rumah Taman Luas di Sentul City, Bogor",
        "price": Decimal("3450000000"),
        "location": "Babakan Madang, Sentul",
        "status": "available",
        "description": (
            "Hunian dengan taman dewasa dan udara pegunungan, di dalam kawasan "
            "terencana. Akses langsung Tol Jagorawi."
        ),
        "specs": {
            "bedrooms": 4, "bathrooms": 3, "land_area_m2": 300,
            "building_area_m2": 250, "certificate": "SHM", "carport": 2,
            "year_built": 2019, "electricity_va": 4400,
        },
    },
    {
        "owner_key": "bagus",
        "title": "Unit Komersial Mall Kelapa Nunggal",
        "price": Decimal("1250000000"),
        "location": "Kelapa Nunggal, Bogor",
        "status": "sold",
        "description": (
            "Unit ritel lantai dasar dengan muka toko lebar. Terjual, disimpan "
            "sebagai pembanding harga."
        ),
        "specs": {
            "bedrooms": 0, "bathrooms": 1, "land_area_m2": 0,
            "building_area_m2": 64, "certificate": "HGB", "carport": 0,
            "year_built": 2021, "electricity_va": 4400,
        },
    },
    {
        "owner_key": "dewi",
        "title": "Rumah Pinggir Sungai di Tasikmalaya",
        "price": Decimal("720000000"),
        "location": "Cipedes, Tasikmalaya",
        "status": "available",
        "description": (
            "Rumah tenang menghadap aliran sungai kecil, dengan teras kayu. Cocok "
            "untuk hunian pensiun atau rumah kedua."
        ),
        "specs": {
            "bedrooms": 3, "bathrooms": 2, "land_area_m2": 200,
            "building_area_m2": 130, "certificate": "SHM", "carport": 1,
            "year_built": 2014, "electricity_va": 2200,
        },
    },
]

# RAG corpus. Indonesian-language property documents, which is what the
# indonesian tsvector config and the hybrid retrieval path exist to serve.
DOCUMENTS: list[dict[str, str]] = [
    {
        "title": "Panduan Sertifikat Properti: SHM, HGB, dan SHM Sarusun",
        "lang": "id",
        "content": """
Sertifikat Hak Milik (SHM) adalah bentuk kepemilikan tanah terkuat di Indonesia.
SHM berlaku tanpa batas waktu dan hanya dapat dimiliki oleh Warga Negara
Indonesia. Properti bersertifikat SHM umumnya paling mudah dijaminkan ke bank
untuk KPR.

Hak Guna Bangunan (HGB) memberi pemegangnya hak mendirikan dan memiliki bangunan
di atas tanah yang bukan miliknya, dengan jangka waktu awal maksimal 30 tahun.
HGB dapat diperpanjang 20 tahun dan diperbarui kembali. Badan hukum Indonesia
dapat memegang HGB, sementara SHM tidak. Ruko dan gudang komersial di Jawa Barat
sering bersertifikat HGB.

SHM Sarusun (Satuan Rumah Susun) berlaku untuk unit apartemen. Pemegangnya
memiliki unit secara individual sekaligus bagian bersama atas tanah dan fasilitas
gedung secara proporsional.

Sebelum transaksi, pembeli sebaiknya memeriksa keaslian sertifikat di kantor
Badan Pertanahan Nasional (BPN) setempat dan memastikan tidak ada sengketa,
blokir, atau hak tanggungan yang melekat.
""".strip(),
    },
    {
        "title": "FAQ Pembiayaan KPR untuk Pembeli Rumah di Jawa Barat",
        "lang": "id",
        "content": """
Kredit Pemilikan Rumah (KPR) adalah fasilitas pinjaman bank untuk membeli
properti. Uang muka umumnya berkisar 10 sampai 30 persen dari harga properti,
tergantung kebijakan bank dan apakah ini rumah pertama pembeli.

Tenor KPR di Indonesia umumnya 5 sampai 25 tahun. Suku bunga dapat berbentuk
tetap (fixed) untuk beberapa tahun pertama, lalu berubah menjadi mengambang
(floating) mengikuti suku bunga acuan.

KPR Subsidi tersedia untuk rumah dengan harga di bawah batas tertentu, dengan
suku bunga tetap yang lebih rendah sepanjang tenor. Pembeli harus memenuhi
syarat penghasilan maksimum dan belum pernah memiliki rumah.

Dokumen yang lazim diminta bank: KTP, Kartu Keluarga, NPWP, slip gaji atau
laporan keuangan usaha, rekening koran tiga sampai enam bulan terakhir, dan
fotokopi sertifikat properti.

Biaya di luar harga properti mencakup Bea Perolehan Hak atas Tanah dan Bangunan
(BPHTB) sebesar 5 persen dari nilai transaksi setelah dikurangi NPOPTKP, biaya
notaris atau PPAT, biaya balik nama, serta biaya provisi dan administrasi bank.
""".strip(),
    },
    {
        "title": "Prolov Property Buying Guide for Foreign and Expat Buyers",
        "lang": "en",
        "content": """
Foreign nationals cannot hold Hak Milik (SHM) freehold title to Indonesian land.
The ownership structures available to foreigners are Hak Pakai (Right to Use),
typically granted for an initial 30 years and extendable, and leasehold
arrangements agreed directly with a titleholder.

Foreign buyers may hold strata title on apartment units under specific
conditions, including minimum price thresholds that vary by province. West Java
thresholds differ from those in Jakarta and Bali, so the figure should be
confirmed for the specific regency at the time of purchase.

Establishing a PT PMA (foreign investment company) allows a business entity to
hold HGB title. This route suits commercial property such as the shophouses and
warehouses common along the Bandung, Bekasi, and Karawang corridors.

Every foreign purchase should be reviewed by an Indonesian notary (PPAT) before
any payment is made. Prolov introduces clients to independent notaries and does
not act as legal counsel.
""".strip(),
    },
    {
        "title": "Panduan Wilayah: Koridor Properti Jawa Barat",
        "lang": "id",
        "content": """
Bandung Utara meliputi Setiabudi, Dago, dan Lembang. Kawasan ini berudara sejuk,
dekat kampus, dan diminati untuk hunian keluarga serta vila akhir pekan. Harga
per meter persegi termasuk yang tertinggi di Jawa Barat.

Bekasi dan Cikarang merupakan koridor industri dengan permintaan hunian pekerja
yang tinggi. Cluster keluarga muda dan rumah subsidi banyak tersedia, dengan
akses tol yang menjadi faktor harga utama.

Depok, khususnya sepanjang Jalan Margonda, adalah koridor komersial dan kampus.
Ruko dan kost memiliki tingkat hunian tinggi sepanjang tahun ajaran.

Bogor dan Sentul menarik pembeli yang mencari udara pegunungan dengan akses Tol
Jagorawi ke Jakarta. Banyak pembeli adalah commuter yang bekerja di Jakarta.

Karawang dan Padalarang berkembang sebagai pusat logistik dan pergudangan,
didorong kawasan industri dan jaringan tol Trans-Jawa.
""".strip(),
    },
]
