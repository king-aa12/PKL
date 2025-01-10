import streamlit as st
import qrcode
import json
import pandas as pd
from PIL import Image
from io import BytesIO
import os

# Fungsi untuk membuat QR code
def buat_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Fungsi untuk membaca data dari file JSON
def baca_data_dari_file(nama_file):
    if os.path.exists(nama_file):
        with open(nama_file, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                return data
            except json.JSONDecodeError:
                st.error(f"Format data dalam file '{nama_file}' tidak valid.")
                return None
    else:
        st.error(f"File '{nama_file}' tidak ditemukan.")
        return None

# Fungsi untuk menyimpan data ke file JSON
def simpan_data_ke_file(nama_file, data):
    with open(nama_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Fungsi untuk mencari buku berdasarkan kata kunci
def cari_buku(keywords, data):
    hasil = []
    kata_kunci_ditemukan = set()
    for kategori in data:
        for buku in kategori['buku']:
            for keyword in keywords:
                if keyword.lower() in str(buku).lower():
                    hasil.append(buku)
                    kata_kunci_ditemukan.add(keyword.lower())
                    break
    return hasil, kata_kunci_ditemukan

# Fungsi untuk login
def login(username, password, users):
    return users.get(username) == password

# Fungsi untuk registrasi
def register(username, password, users):
    if username in users:
        return False
    users[username] = password
    return True

# Fungsi untuk menampilkan semua buku
def tampilkan_semua_buku(data):
    semua_buku = []
    for kategori in data:
        semua_buku.extend(kategori['buku'])
    return semua_buku

# Fungsi utama untuk mengatur login dan registrasi
def atur_login(data_pengguna):
    if not st.session_state.logged_in:
        st.title("Portal Pencarian Buku Laporan PKL")
        pilihan = st.radio("Pilih Opsi:", ["Login", "Registrasi"])

        if pilihan == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if login(username, password, data_pengguna):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login berhasil!")
                else:
                    st.error("Username atau password salah.")

        elif pilihan == "Registrasi":
            reg_username = st.text_input("Username Baru")
            reg_password = st.text_input("Password Baru", type="password")
            if st.button("Registrasi"):
                if register(reg_username, reg_password, data_pengguna):
                    st.success("Registrasi berhasil! Silakan login menggunakan akun Anda.")
                else:
                    st.error("Username sudah terdaftar.")

# Fungsi untuk menampilkan opsi edit, tambah, dan hapus buku
def tampilkan_opsi_buku():
    pilihan = st.sidebar.radio("Menu", ["Tampilkan Semua Buku", "Cari Buku", "Tambah Buku", "Edit Buku", "Hapus Buku"])
    return pilihan

# Fungsi untuk menambah buku
def tambah_buku(data, nama_file):
    if st.session_state.username != "admin":
        st.error("Hanya admin yang dapat menambah buku.")
        return

    st.subheader("Tambah Buku")
    nomor_urut = st.text_input("Nomor Urut Arsip")
    tahun = st.text_input("Tahun Pelaksanaan")
    nim = st.text_input("NIM")
    nama_mahasiswa = st.text_input("Nama Mahasiswa")
    judul_laporan = st.text_input("Judul Laporan PKL")
    dosen_pembimbing = st.text_input("Nama Dosen Pembimbing")
    tempat_pelaksanaan = st.text_input("Nama Tempat Pelaksanaan")
    kab_kota = st.text_input("Kabupaten/Kota Pelaksanaan")

    if st.button("Tambah Buku"):
        if nomor_urut and tahun and nim and nama_mahasiswa and judul_laporan and dosen_pembimbing and tempat_pelaksanaan and kab_kota:
            buku_baru = {
                "Nomor_Urut_Arsip": nomor_urut,
                "Tahun_Pelaksanaan": tahun,
                "NIM": nim,
                "Nama_Mahasiswa": nama_mahasiswa,
                "Judul_Laporan_PKL": judul_laporan,
                "Nama_Dosen_Pembimbing": dosen_pembimbing,
                "Nama_Tempat_Pelaksanaan": tempat_pelaksanaan,
                "Kabupaten_/_Kota_Pelaksanaan": kab_kota
            }
            data[0]['buku'].append(buku_baru)
            simpan_data_ke_file(nama_file, data)
            st.success("Buku berhasil ditambahkan!")
        else:
            st.error("Semua kolom harus diisi.")

# Fungsi untuk mengedit buku
def edit_buku(data, nama_file):
    if st.session_state.username != "admin":
        st.error("Hanya admin yang dapat mengedit buku.")
        return

    st.subheader("Edit Buku")
    nomor_urut = st.text_input("Masukkan Nomor Urut Arsip Buku yang Ingin Diedit")

    if st.button("Cari Buku"):
        buku_ditemukan = next((buku for buku in data[0]['buku'] if buku['Nomor_Urut_Arsip'] == nomor_urut), None)
        if buku_ditemukan:
            st.write("Buku Ditemukan:")
            st.json(buku_ditemukan)

            buku_ditemukan['Tahun_Pelaksanaan'] = st.text_input("Tahun Pelaksanaan", buku_ditemukan['Tahun_Pelaksanaan'])
            buku_ditemukan['NIM'] = st.text_input("NIM", buku_ditemukan['NIM'])
            buku_ditemukan['Nama_Mahasiswa'] = st.text_input("Nama Mahasiswa", buku_ditemukan['Nama_Mahasiswa'])
            buku_ditemukan['Judul_Laporan_PKL'] = st.text_input("Judul Laporan PKL", buku_ditemukan['Judul_Laporan_PKL'])
            buku_ditemukan['Nama_Dosen_Pembimbing'] = st.text_input("Nama Dosen Pembimbing", buku_ditemukan['Nama_Dosen_Pembimbing'])
            buku_ditemukan['Nama_Tempat_Pelaksanaan'] = st.text_input("Nama Tempat Pelaksanaan", buku_ditemukan['Nama_Tempat_Pelaksanaan'])
            buku_ditemukan['Kabupaten_/_Kota_Pelaksanaan'] = st.text_input("Kabupaten/Kota Pelaksanaan", buku_ditemukan['Kabupaten_/_Kota_Pelaksanaan'])

            if st.button("Simpan Perubahan"):
                simpan_data_ke_file(nama_file, data)
                st.success("Buku berhasil diperbarui!")
        else:
            st.error("Buku tidak ditemukan.")

# Fungsi untuk menghapus buku
def hapus_buku(data, nama_file):
    if st.session_state.username != "admin":
        st.error("Hanya admin yang dapat menghapus buku.")
        return

    st.subheader("Hapus Buku")
    nomor_urut = st.text_input("Masukkan Nomor Urut Arsip Buku yang Ingin Dihapus")

    if st.button("Hapus Buku"):
        buku_ditemukan = next((buku for buku in data[0]['buku'] if buku['Nomor_Urut_Arsip'] == nomor_urut), None)
        if buku_ditemukan:
            data[0]['buku'].remove(buku_ditemukan)
            simpan_data_ke_file(nama_file, data)
            st.success("Buku berhasil dihapus!")
        else:
            st.error("Buku tidak ditemukan.")

# Fungsi utama untuk menampilkan aplikasi utama setelah login
def aplikasi_utama():
    st.sidebar.write(f"Selamat datang, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.success("Logout berhasil.")

    st.title("Portal Pencarian Judul Laporan PKL Prodi Teknik Informatika Jurusan Teknik Elektro Politeknik Negeri Pontianak")
    nama_file = 'datajsonbuku.json'
    data_perpustakaan = baca_data_dari_file(nama_file)

    pilihan = tampilkan_opsi_buku()

    if pilihan == "Cari Buku":
        if data_perpustakaan:
            st.subheader("Pencarian Buku")
            keyword_input = st.text_input("Masukkan Kata Kunci Pencarian (Nama MHS, NIM, Nama DosPem, Tempat PKL, Kab/Kota) jika ingin memasukkan lebih dari 1 kata kunci pakai tanda koma (,):", max_chars=50)
            keywords = [kw.strip() for kw in keyword_input.split(",") if kw.strip()]

            cari_button = st.button("Cari")

            if cari_button:
                if keywords:
                    hasil_pencarian, kata_kunci_ditemukan = cari_buku(keywords, data_perpustakaan)
                    st.info(f"Jumlah hasil pencarian: {len(hasil_pencarian)} buku.")
                    st.info(f"Jumlah kata kunci yang ditemukan: {len(kata_kunci_ditemukan)} dari {len(keywords)} kata kunci yang dicari.")
                    if hasil_pencarian:
                        df = pd.DataFrame(hasil_pencarian)
                        df['No'] = range(1, len(df) + 1)
                        df = df.rename(columns={
                            'Nomor_Urut_Arsip': 'No. Arsip', 
                            'Tahun_Pelaksanaan': 'Tahun', 
                            'NIM': 'NIM',
                            'Nama_Mahasiswa': 'Nama Mahasiswa', 
                            'Judul_Laporan_PKL': 'Judul Laporan PKL', 
                            'Nama_Dosen_Pembimbing': 'Nama Dosen Pembimbing',
                            'Nama_Tempat_Pelaksanaan': 'Nama Tempat Pelaksanaan', 
                            'Kabupaten_/_Kota_Pelaksanaan': 'Kab./Kota'
                        })
                        df = df[['No', 'No. Arsip', 'Tahun', 'NIM', 
                                 'Nama Mahasiswa', 'Judul Laporan PKL', 'Nama Dosen Pembimbing', 
                                 'Nama Tempat Pelaksanaan', 'Kab./Kota']]
                        st.subheader("Hasil Pencarian Buku:")
                        st.write(df.to_html(index=False), unsafe_allow_html=True)
                    else:
                        st.warning("Tidak ada buku yang cocok dengan pencarian Anda.")
                else:
                    st.warning("Silakan masukkan kata kunci pencarian.")

    elif pilihan == "Tampilkan Semua Buku":
        if data_perpustakaan:
            semua_buku = tampilkan_semua_buku(data_perpustakaan)
            if semua_buku:
                st.info(f"Jumlah total buku: {len(semua_buku)} buku.")
                df = pd.DataFrame(semua_buku)
                df['No'] = range(1, len(df) + 1)
                df = df.rename(columns={
                    'Nomor_Urut_Arsip': 'No. Arsip', 
                    'Tahun_Pelaksanaan': 'Tahun', 
                    'NIM': 'NIM',
                    'Nama_Mahasiswa': 'Nama Mahasiswa', 
                    'Judul_Laporan_PKL': 'Judul Laporan PKL', 
                    'Nama_Dosen_Pembimbing': 'Nama Dosen Pembimbing',
                    'Nama_Tempat_Pelaksanaan': 'Nama Tempat Pelaksanaan', 
                    'Kabupaten_/_Kota_Pelaksanaan': 'Kab./Kota'
                })
                df = df[['No', 'No. Arsip', 'Tahun', 'NIM', 
                         'Nama Mahasiswa', 'Judul Laporan PKL', 'Nama Dosen Pembimbing', 
                         'Nama Tempat Pelaksanaan', 'Kab./Kota']]

                st.subheader("Daftar Semua Buku")
                st.write(df.to_html(index=False), unsafe_allow_html=True)
            else:
                st.warning("Tidak ada buku yang tersedia.")
        else:
            st.error("Data perpustakaan tidak tersedia.")

    elif pilihan == "Tambah Buku":
        if data_perpustakaan:
            tambah_buku(data_perpustakaan, nama_file)

    elif pilihan == "Edit Buku":
        if data_perpustakaan:
            edit_buku(data_perpustakaan, nama_file)

    elif pilihan == "Hapus Buku":
        if data_perpustakaan:
            hapus_buku(data_perpustakaan, nama_file)

# Inisialisasi data pengguna
data_pengguna = {
    "admin": "admin123"
}

# Session state untuk menyimpan status login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Set page config
st.set_page_config(page_title="Pencarian Buku Laporan PKL Teknik Informatika Tahun 2021", layout="wide")

# Menjalankan fungsi login atau aplikasi utama berdasarkan status login
if st.session_state.logged_in:
    aplikasi_utama()
else:
    atur_login(data_pengguna)
