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
                return json.load(file)
            except json.JSONDecodeError:
                st.error(f"Format data dalam file '{nama_file}' tidak valid.")
                return {}
    else:
        return {}

# Fungsi untuk menulis data ke file JSON
def tulis_data_ke_file(nama_file, data):
    with open(nama_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Fungsi untuk login
def login(username, password, users):
    return users.get(username) == password

# Fungsi untuk registrasi
def register(username, password, users):
    if username in users:
        return False
    users[username] = password
    return True

# Fungsi untuk mencari buku berdasarkan kata kunci di berbagai kolom
def cari_buku_berdasarkan_kata_kunci(data, keywords):
    hasil = []
    for buku in data:
        if any(keyword.lower() in str(buku).lower() for keyword in keywords):
            hasil.append(buku)
    return hasil

# Fungsi untuk menambahkan buku baru
def tambah_buku(data, buku_baru):
    data.append(buku_baru)
    return data

# Fungsi untuk mengedit buku berdasarkan NIM
def edit_buku(data, nim, data_baru):
    for buku in data:
        if buku['NIM'] == nim:
            buku.update(data_baru)
            return True
    return False

# Fungsi untuk menghapus buku berdasarkan NIM
def hapus_buku(data, nim):
    for buku in data:
        if buku['NIM'] == nim:
            data.remove(buku)
            return True
    return False

# Nama file untuk data pengguna dan data buku
file_pengguna = 'data_pengguna.json'
file_buku = 'datajsonbuku.json'

# Memuat data pengguna dan data buku dari file JSON
data_pengguna = baca_data_dari_file(file_pengguna)
data_buku = baca_data_dari_file(file_buku)

# Inisialisasi session state untuk login
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
url_aplikasi = "https://perpus-pkl.streamlit.app/"
qr_code = buat_qr_code(url_aplikasi)
qr_image = Image.open(qr_code)
st.sidebar.image(qr_image, caption="Untuk Mengakses Portal Ini Gunakan QR Code Diatas.", use_container_width=True)

# Login atau Registrasi
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
            if reg_username in data_pengguna:
                st.error("Username sudah terdaftar.")
            else:
                data_pengguna[reg_username] = reg_password
                tulis_data_ke_file(file_pengguna, data_pengguna)
                st.success("Registrasi berhasil! Silakan login menggunakan akun Anda.")
else:
    st.sidebar.write(f"Selamat datang, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logout berhasil.")

# Jika pengguna sudah login, tampilkan aplikasi utama
if st.session_state.logged_in:
    st.title("Portal Pencarian Judul Laporan PKL Prodi Teknik Informatika Jurusan Teknik Elektro Politeknik Negeri Pontianak")

    # Tampilkan semua buku setelah login
    if data_buku:
        semua_buku = []
        for kategori in data_buku:
            semua_buku.extend(kategori['buku'])

        st.subheader("Pencarian Buku")
        keyword_input = st.text_input("Masukkan Kata Kunci Pencarian (pisahkan dengan koma jika lebih dari satu kata kunci):")
        keywords = [kw.strip() for kw in keyword_input.split(",") if kw.strip()]

        if st.button("Cari"):
            hasil_pencarian = cari_buku_berdasarkan_kata_kunci(semua_buku, keywords)

            if hasil_pencarian:
                df = pd.DataFrame(hasil_pencarian)
                st.subheader("Hasil Pencarian")
                st.dataframe(df)
            else:
                st.warning("Tidak ada buku yang cocok dengan pencarian Anda.")
    else:
        st.error("Tidak ada data buku yang ditemukan.")
