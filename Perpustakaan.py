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
            if register(reg_username, reg_password, data_pengguna):
                st.success("Registrasi berhasil! Silakan login menggunakan akun Anda.")
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
    st.title("Portal Pencarian Judul Laporan PKL Prodi Teknik Informatika Jurusan Teknik Elektro Politeknik Negeri Pontianak")

    # Nama file JSON yang ingin dibaca
    nama_file = 'datajsonbuku.json'

    # Membaca data dari file JSON
    data_perpustakaan = baca_data_dari_file(nama_file)

    # Jika data berhasil dibaca, tampilkan semua buku setelah login
    if data_perpustakaan:
        semua_buku = []
        for kategori in data_perpustakaan:
            semua_buku.extend(kategori['buku'])

        st.subheader("Pencarian Buku")
        keyword_input = st.text_input("Masukkan Kata Kunci Pencarian (pisahkan dengan koma jika lebih dari satu kata kunci):")
        keywords = [kw.strip() for kw in keyword_input.split(",") if kw.strip()]

        if st.button("Cari"):
            hasil_pencarian = cari_buku_berdasarkan_kata_kunci(semua_buku, keywords)

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
                df = df[['No', 'No. Arsip', 'Tahun', 'NIM', 'Nama Mahasiswa', 'Judul Laporan PKL', 'Nama Dosen Pembimbing', 'Nama Tempat Pelaksanaan', 'Kab./Kota']]
                st.subheader("Hasil Pencarian")
                st.write(df.to_html(index=False), unsafe_allow_html=True)
            else:
                st.warning("Tidak ada buku yang cocok dengan pencarian Anda.")


# Fungsi untuk memeriksa apakah pengguna adalah admin
def cek_admin():
    return st.session_state.username == "admin"

# Fungsi utama aplikasi setelah login
if st.session_state.logged_in:
    st.title("Portal Manajemen Buku Laporan PKL")

    # Nama file JSON yang ingin dibaca
    nama_file = 'datajsonbuku.json'
    data_perpustakaan = baca_data_dari_file(nama_file)

    # Tampilkan daftar semua buku jika data tersedia
    if data_perpustakaan:
        semua_buku = [buku for kategori in data_perpustakaan for buku in kategori['buku']]
        st.subheader("Daftar Buku Tersedia")
        df = pd.DataFrame(semua_buku)
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
        st.dataframe(df)

        # Hanya admin yang dapat mengedit, menambah, atau menghapus buku
        if cek_admin():
            st.subheader("Manajemen Buku")

            # Tambah Buku Baru
            if st.checkbox("Tambah Buku Baru"):
                nim_baru = st.text_input("NIM")
                nama_mahasiswa = st.text_input("Nama Mahasiswa")
                judul_laporan = st.text_input("Judul Laporan PKL")
                nama_dosen = st.text_input("Nama Dosen Pembimbing")
                tempat_pelaksanaan = st.text_input("Nama Tempat Pelaksanaan")
                kabupaten = st.text_input("Kab./Kota Pelaksanaan")
                tahun_pelaksanaan = st.text_input("Tahun Pelaksanaan")
                no_arsip = st.text_input("No. Arsip")

                if st.button("Simpan Buku Baru"):
                    buku_baru = {
                        "NIM": nim_baru,
                        "Nama_Mahasiswa": nama_mahasiswa,
                        "Judul_Laporan_PKL": judul_laporan,
                        "Nama_Dosen_Pembimbing": nama_dosen,
                        "Nama_Tempat_Pelaksanaan": tempat_pelaksanaan,
                        "Kabupaten_/_Kota_Pelaksanaan": kabupaten,
                        "Tahun_Pelaksanaan": tahun_pelaksanaan,
                        "Nomor_Urut_Arsip": no_arsip
                    }
                    semua_buku.append(buku_baru)
                    tulis_data_ke_file(nama_file, semua_buku)
                    st.success("Buku baru berhasil ditambahkan!")

            # Edit Buku
            if st.checkbox("Edit Buku"):
                nim_edit = st.text_input("Masukkan NIM Buku yang Akan Diedit")
                if st.button("Cari Buku"):
                    buku_ditemukan = next((b for b in semua_buku if b['NIM'] == nim_edit), None)
                    if buku_ditemukan:
                        st.write("Buku Ditemukan:", buku_ditemukan)
                        nama_mahasiswa = st.text_input("Nama Mahasiswa", buku_ditemukan['Nama_Mahasiswa'])
                        judul_laporan = st.text_input("Judul Laporan PKL", buku_ditemukan['Judul_Laporan_PKL'])
                        nama_dosen = st.text_input("Nama Dosen Pembimbing", buku_ditemukan['Nama_Dosen_Pembimbing'])
                        tempat_pelaksanaan = st.text_input("Nama Tempat Pelaksanaan", buku_ditemukan['Nama_Tempat_Pelaksanaan'])
                        kabupaten = st.text_input("Kab./Kota Pelaksanaan", buku_ditemukan['Kabupaten_/_Kota_Pelaksanaan'])
                        tahun_pelaksanaan = st.text_input("Tahun Pelaksanaan", buku_ditemukan['Tahun_Pelaksanaan'])
                        no_arsip = st.text_input("No. Arsip", buku_ditemukan['Nomor_Urut_Arsip'])

                        if st.button("Simpan Perubahan"):
                            buku_ditemukan.update({
                                "Nama_Mahasiswa": nama_mahasiswa,
                                "Judul_Laporan_PKL": judul_laporan,
                                "Nama_Dosen_Pembimbing": nama_dosen,
                                "Nama_Tempat_Pelaksanaan": tempat_pelaksanaan,
                                "Kabupaten_/_Kota_Pelaksanaan": kabupaten,
                                "Tahun_Pelaksanaan": tahun_pelaksanaan,
                                "Nomor_Urut_Arsip": no_arsip
                            })
                            tulis_data_ke_file(nama_file, semua_buku)
                            st.success("Perubahan berhasil disimpan!")
                    else:
                        st.warning("Buku dengan NIM tersebut tidak ditemukan.")

            # Hapus Buku
            if st.checkbox("Hapus Buku"):
                nim_hapus = st.text_input("Masukkan NIM Buku yang Akan Dihapus")
                if st.button("Hapus Buku"):
                    buku_dihapus = next((b for b in semua_buku if b['NIM'] == nim_hapus), None)
                    if buku_dihapus:
                        semua_buku.remove(buku_dihapus)
                        tulis_data_ke_file(nama_file, semua_buku)
                        st.success("Buku berhasil dihapus!")
                    else:
                        st.warning("Buku dengan NIM tersebut tidak ditemukan.")
        else:
            st.info("Fitur manajemen buku hanya tersedia untuk admin.")
    else:
        st.error("Tidak ada data buku yang ditemukan.")
