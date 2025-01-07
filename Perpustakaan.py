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

# Fungsi untuk mencari buku berdasarkan kategori atau kata kunci
def cari_buku(kategori_dicari, keywords, data):
    hasil = []
    kata_kunci_ditemukan = set()
    for kategori in data:
        if kategori_dicari.lower() == kategori['kategori'].lower() or kategori_dicari == "Pilih kategori buku":
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
st.set_page_config(page_title="Pencarian Buku Laporan PKL", layout="wide")

# Sidebar
st.sidebar.header("Portal Pencarian Buku Laporan PKL")
st.sidebar.markdown("""
Portal Ini Untuk Mencari Judul Buku Laporan PKL Prodi Teknik Informatika Jurusan Teknik Elektro di Perpustakaan Politeknik Negeri Pontianak Tahun 2021.
""")

# Menambahkan QR code pada sidebar
url_aplikasi = "https://perpustkaan-polnep-judul-pkl-ti.streamlit.app/"
qr_code = buat_qr_code(url_aplikasi)
qr_image = Image.open(qr_code)
st.sidebar.image(qr_image, caption="Untuk Mengakses Portal Ini Gunakan QR Code Diatas.", use_container_width=True)

# Login atau Registrasi
if not st.session_state.logged_in:
    st.title("Login ke Portal Pencarian Buku")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(username, password, data_pengguna):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login berhasil!")
        else:
            st.error("Username atau password salah.")

    st.subheader("Registrasi Pengguna Baru")
    reg_username = st.text_input("Username Baru")
    reg_password = st.text_input("Password Baru", type="password")

    if st.button("Registrasi"):
        if register(reg_username, reg_password, data_pengguna):
            st.success("Registrasi berhasil! Anda akan login otomatis.")
            st.session_state.logged_in = True
            st.session_state.username = reg_username
        else:
            st.error("Username sudah terdaftar.")
else:
    st.sidebar.write(f"Selamat datang, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logout berhasil.")

# Jika pengguna sudah login, tampilkan aplikasi utama
if st.session_state.logged_in:
    # Judul aplikasi
    st.title("Portal Pencarian Judul Laporan PKL Prodi Teknik Informatika Jurusan Teknik Elektro Politeknik Negeri Pontianak")

    # Nama file JSON yang ingin dibaca
    nama_file = 'C://TUGAS MAKUL ALGORITMA PEMROGRAMAN//KELOMPOK 2//datajsonbuku.json'

    # Membaca data dari file JSON
    data_perpustakaan = baca_data_dari_file(nama_file)

    # Jika data berhasil dibaca
    if data_perpustakaan:
        # Ambil daftar kategori buku
        Daftar_Judul = [kategori['kategori'] for kategori in data_perpustakaan]

        kategori_yang_dicari = st.radio("Tampilkan Daftar Judul Buku:", Daftar_Judul)
        
        # Input pengguna
        daftar_kategori = ["Cari Judul Laporan Berdasarkan Kata Kunci"] + [kategori['kategori'] for kategori in data_perpustakaan]
        
        keyword_input = st.text_input("Masukkan Kata Kunci Pencarian (pisahkan dengan koma jika lebih dari satu kata kunci):")
        keywords = [kw.strip() for kw in keyword_input.split(",") if kw.strip()]

        # Tombol pencarian
        if st.button("Cari"):
            if kategori_yang_dicari != "Pilih kategori buku" or keywords:
                # Cari buku berdasarkan kategori atau kata kunci
                hasil_pencarian, kata_kunci_ditemukan = cari_buku(kategori_yang_dicari, keywords, data_perpustakaan)

                # Buat DataFrame untuk menampilkan hasil
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
                    st.subheader(f"Hasil pencarian untuk kategori '{kategori_yang_dicari}':")
                    st.write(df.to_html(index=False), unsafe_allow_html=True)
                    
                    # Tampilkan jumlah hasil pencarian
                    st.info(f"Jumlah hasil pencarian: {len(hasil_pencarian)} buku.")
                    
                    # Tampilkan jumlah kata kunci yang ditemukan
                    st.info(f"Jumlah kata kunci yang ditemukan: {len(kata_kunci_ditemukan)} dari {len(keywords)} kata kunci yang dicari.")
                else:
                    st.warning("Tidak ada buku yang cocok dengan pencarian Anda.")
            else:
                st.warning("Silakan pilih kategori buku atau masukkan kata kunci.")
    else:
        st.error("Data perpustakaan tidak tersedia.")
