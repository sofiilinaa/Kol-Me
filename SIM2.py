import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit as st
import re

def input_uang_otomatis(label, key):
    # Ambil input mentah user
    raw_input = st.session_state.get(key, "0")

    # Bersihkan ke digit saja
    angka_bersih = re.sub(r"[^\d]", "", raw_input)

    # Format ke 'Rp xxx.xxx'
    if angka_bersih:
        angka_int = int(angka_bersih)
        formatted = f"{angka_int:,}".replace(",", ".")
    else:
        formatted = "0"

    # Tampilkan input yang terformat kembali ke field
    input_baru = st.text_input(label, value=formatted, key=key, label_visibility="visible")

    # Return nilai numerik
    return int(re.sub(r"[^\d]", "", input_baru)) if input_baru else 0


# SETUP FILE DAN KONSTANTA
os.makedirs("data", exist_ok=True)
PRODUKSI_FILE = 'data/data_produksi.csv'
PENJUALAN_FILE = 'data/data_penjualan.csv'
KEUANGAN_FILE = 'data/laporan_keuangan.csv'
STOK_FILE = 'data/stok.csv'
PENGISIAN_STOK_FILE = 'data/pengisian_stok.csv'
LOGIN_STATUS_FILE = 'data/login_status.csv'
USERS_FILE = "data/users.csv"

HARGA_BIBIT = 100
HARGA_PUPUK = 30000
HARGA_KOL = 4000

# FUNGSI BANTUAN
def simpan_data(df, file):
    df.to_csv(file, index=False)

def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame()

def load_stok():
    if os.path.exists(STOK_FILE):
        df = pd.read_csv(STOK_FILE)
        if not df.empty and 'Stok' in df.columns:
            value = df.iloc[0]['Stok']
            if pd.notna(value):
                return int(value)
    return 1000

def simpan_stok(stok_baru):
    df = pd.DataFrame([{"Stok": stok_baru}])
    df.to_csv(STOK_FILE, index=False)

def is_user_logged_in(username):
    if os.path.exists(LOGIN_STATUS_FILE):
        df = pd.read_csv(LOGIN_STATUS_FILE)
        return username in df["username"].values
    return False

def set_user_login_status(username, status):
    if status:
        df = pd.read_csv(LOGIN_STATUS_FILE) if os.path.exists(LOGIN_STATUS_FILE) else pd.DataFrame(columns=["username"])
        if username not in df["username"].values:
            df.loc[len(df)] = [username]
            df.to_csv(LOGIN_STATUS_FILE, index=False)
    else:
        if os.path.exists(LOGIN_STATUS_FILE):
            df = pd.read_csv(LOGIN_STATUS_FILE)
            df = df[df["username"] != username]
            df.to_csv(LOGIN_STATUS_FILE, index=False)

def register_user(username, password):
    if not username.endswith("@kolme.com"):
        return "Email harus menggunakan domain @kolme.com"
    df = pd.read_csv(USERS_FILE) if os.path.exists(USERS_FILE) else pd.DataFrame(columns=["username", "password"])
    if username in df["username"].values:
        return "Email sudah terdaftar."
    df.loc[len(df)] = [username, password]
    df.to_csv(USERS_FILE, index=False)
    return "Berhasil mendaftar! Silakan login."

def authenticate_user(username, password):
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        user_row = df[df["username"] == username]
        if not user_row.empty and user_row.iloc[0]["password"] == password:
            return True
    return False

# Session login
if "login" not in st.session_state:
    st.session_state["login"] = False
if "halaman" not in st.session_state:
    st.session_state["halaman"] = "Home"

# Jika belum login
if not st.session_state["login"]:
    col1, col2 = st.columns([1, 3])
    with col2:
        st.title("Selamat Datang di KOL-ME")

    st.divider()

    menu = st.radio("Pilih Menu", ["Login", "Daftar"])

    if menu == "Login":
        st.subheader(":material/lock: Login Admin")
        st.info("Hanya admin resmi KOL-ME yang dapat masuk.")

        username = st.text_input(":material/contact_mail: Email")
        password = st.text_input(":material/key: Kata Sandi", type="password")

        if st.button(":material/login: Login"):
            if authenticate_user(username, password):
                if is_user_logged_in(username):
                    st.error("❌ Pengguna ini sedang login di tempat lain.")
                else:
                    set_user_login_status(username, True)
                    st.session_state["login"] = True
                    st.session_state["username"] = username
                    st.success("Login berhasil!")
            else:
                st.error("Email atau kata sandi salah.")

    else:  # Menu Pendaftaran
        st.subheader(":material/person_add: Daftar Akun Baru")
        new_username = st.text_input("Email (@kolme.com)")
        new_password = st.text_input("Password", type="password")
        if st.button("Daftar"):
            msg = register_user(new_username, new_password)
            if msg.startswith("Berhasil"):
                st.success(msg)
            else:
                st.error(msg)

    st.divider()
    st.caption(":material/forest: Sistem pertanian digital KOL-ME")

# Jika sudah login
else:
    with st.sidebar:
        st.markdown(f":material/person: Login sebagai:\n`{st.session_state['username']}`")
        halaman = st.selectbox("Pilih Halaman", ["Home", "Produksi", "Penjualan", "Isi Stok", "Laporan Keuangan"])
        st.session_state["halaman"] = halaman
        if st.button(":material/logout: Logout"):
            set_user_login_status(st.session_state["username"], False)
            st.session_state["login"] = False
            st.session_state.pop("username", None)
            st.success("Anda telah logout")
    
    # Pastikan halaman selalu terdefinisi
    halaman = st.session_state.get("halaman", "Home")
    
    # HALAMAN HOME
    if halaman == 'Home':
        st.title(":material/home: Home")
        st.markdown("""
        Selamat datang di aplikasi manajemen produksi dan penjualan KOL-ME!

        Aplikasi ini membantu Anda mencatat:
        - Transaksi produksi
        - Transaksi penjualan
        - Laporan keuangan otomatis
        - Penambahan dan pengurangan stok kol
        """)

    # HALAMAN PRODUKSI
    elif halaman == 'Produksi':
        st.title(":material/box_add: Tambah Transaksi Produksi")
        tanggal = st.date_input("Tanggal Produksi", value=datetime.today())

        jumlah_bibit = input_uang_otomatis("Bibit (Rp 100/batang)", key="bibit")
        jumlah_pupuk = input_uang_otomatis("Pupuk (Rp 30.000/kantong)", key="pupuk")
        biaya_perawatan = input_uang_otomatis("Biaya Perawatan (Rp)", key="perawatan")
        biaya_tenaga_kerja = input_uang_otomatis("Biaya Tenaga Kerja (Rp)", key="tenaga_kerja")

        total = jumlah_bibit * HARGA_BIBIT + jumlah_pupuk * HARGA_PUPUK + biaya_perawatan + biaya_tenaga_kerja
        st.info(f"Total Biaya Produksi: Rp {total:,.0f}")

        if st.button(":material/save: Simpan Produksi"):
            df = load_data(PRODUKSI_FILE)
            new = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Bibit (Batang)": jumlah_bibit,
                "Total Harga Bibit": jumlah_bibit * HARGA_BIBIT,   #Pastikan dihitung
                "Pupuk (Kantong)": jumlah_pupuk,
                "Total Harga Pupuk": jumlah_pupuk * HARGA_PUPUK,   #Pastikan dihitung
                "Biaya Perawatan": biaya_perawatan,
                "Biaya Tenaga Kerja": biaya_tenaga_kerja,
                "Total Biaya": total
            }])
            df = pd.concat([df, new], ignore_index=True)
            simpan_data(df, PRODUKSI_FILE)

            df_keuangan = load_data(KEUANGAN_FILE)
            transaksi_keuangan = pd.DataFrame([
                {"Tanggal": tanggal.strftime("%Y-%m-%d"), "Keterangan": "Beban Produksi", "Debit": total, "Kredit": 0},
                {"Tanggal": tanggal.strftime("%Y-%m-%d"), "Keterangan": "     Kas", "Debit": 0, "Kredit": total}
            ])
            df_keuangan = pd.concat([df_keuangan, transaksi_keuangan], ignore_index=True)
            simpan_data(df_keuangan, KEUANGAN_FILE)

            st.success("✅ Data produksi dan laporan keuangan disimpan!")

        st.subheader("📊 Riwayat Transaksi Produksi")
        df_produksi = load_data(PRODUKSI_FILE)

        if not df_produksi.empty:
            df_produksi["Tanggal"] = pd.to_datetime(df_produksi["Tanggal"], errors="coerce")
            df_produksi = df_produksi.dropna(subset=["Tanggal"])
            df_produksi = df_produksi.sort_values("Tanggal", ascending=False).reset_index(drop=True)

            # Pastikan kolom numerik bertipe float/int
            df_produksi["Total Harga Bibit"] = pd.to_numeric(df_produksi["Total Harga Bibit"], errors='coerce').fillna(0)
            df_produksi["Total Harga Pupuk"] = pd.to_numeric(df_produksi["Total Harga Pupuk"], errors='coerce').fillna(0)
            
            # Buat dataframe untuk tampilan
            df_display = df_produksi.copy()
            df_display["Tanggal"] = df_display["Tanggal"].dt.strftime("%d %b %Y")
            
            # Format tampilan keuangan
            df_display["Total Harga Bibit"] = df_display["Total Harga Bibit"].apply(lambda x: f"Rp {int(x):,}" if pd.notnull(x) else "Rp 0")
            df_display["Total Harga Pupuk"] = df_display["Total Harga Pupuk"].apply(lambda x: f"Rp {int(x):,}" if pd.notnull(x) else "Rp 0")
            df_display["Biaya Perawatan"] = df_display["Biaya Perawatan"].apply(lambda x: f"Rp {int(x):,}" if pd.notnull(x) else "Rp 0")
            df_display["Biaya Tenaga Kerja"] = df_display["Biaya Tenaga Kerja"].apply(lambda x: f"Rp {int(x):,}" if pd.notnull(x) else "Rp 0")
            df_display["Total Biaya"] = df_display["Total Biaya"].apply(lambda x: f"Rp {int(x):,}" if pd.notnull(x) else "Rp 0")
            
            # Pilih kolom yang akan ditampilkan
            df_display = df_display[[
                "Tanggal", 
                "Total Harga Bibit", 
                "Total Harga Pupuk", 
                "Biaya Perawatan", 
                "Biaya Tenaga Kerja", 
                "Total Biaya"
            ]]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.markdown("### 🧹 Hapus Data Produksi")
            opsi_hapus = st.multiselect(
                "Pilih transaksi yang ingin dihapus berdasarkan tanggal:",
                options=[f"{i+1}. {row['Tanggal'].strftime('%Y-%m-%d')} - Total Rp {row['Total Biaya']:,.0f}" for i, row in df_produksi.iterrows()],
                key="pilih_hapus_produksi"
            )

            if opsi_hapus:
                if st.button("🗑 Hapus Data Terpilih"):
                    indeks_hapus = [int(item.split(".")[0]) - 1 for item in opsi_hapus]
                    data_dihapus = df_produksi.iloc[indeks_hapus]

                    # Update file produksi
                    df_produksi = df_produksi.drop(index=indeks_hapus).reset_index(drop=True)
                    simpan_data(df_produksi, PRODUKSI_FILE)

                    # Update laporan keuangan
                    df_keuangan = load_data(KEUANGAN_FILE)
                    for _, row in data_dihapus.iterrows():
                        tanggal_str = row["Tanggal"].strftime("%Y-%m-%d")
                        df_keuangan = df_keuangan[~(
                            (df_keuangan['Tanggal'] == tanggal_str) & (
                                (df_keuangan['Keterangan'].str.strip() == "Beban Produksi") & (df_keuangan['Debit'] == row['Total Biaya']) |
                                (df_keuangan['Keterangan'].str.strip() == "Kas") & (df_keuangan['Kredit'] == row['Total Biaya'])
                            )
                        )]
                    simpan_data(df_keuangan, KEUANGAN_FILE)

                    st.success("✅ Data produksi dan laporan keuangan berhasil dihapus.")
        else:
            st.info("Belum ada data produksi.")

    # HALAMAN PENJUALAN
    elif halaman == 'Penjualan':
        st.title(":material/shopping_cart: Tambah Transaksi Penjualan")
        stok_kol = load_stok()
        st.markdown(f" *Stok Kol Saat Ini:* {stok_kol} Kg")

        tanggal_jual = st.date_input("Tanggal Penjualan", value=datetime.today())
        kode = f"J-{tanggal_jual.strftime('%Y%m%d')}"
        st.text_input("Kode Transaksi", value=kode, disabled=True)

        jumlah = input_uang_otomatis("Jumlah Kol Terjual (Kg)", key="jumlah_terjual")
        total = jumlah * HARGA_KOL
        st.info(f"Total Penjualan: Rp {total:,.0f}")

        if st.button(":material/save: Simpan Penjualan"):
            if jumlah > stok_kol:
                st.error(f"❌ Jumlah kol yang dijual melebihi stok! Stok tersedia: {stok_kol} Kg")
            else:
                df = load_data(PENJUALAN_FILE)
                new = pd.DataFrame([{
                    "Tanggal": tanggal_jual.strftime("%Y-%m-%d"),
                    "Kode Transaksi": kode,
                    "Jumlah Kol (Kg)": jumlah,
                    "Total Penjualan": total
                }])
                df = pd.concat([df, new], ignore_index=True)
                simpan_data(df, PENJUALAN_FILE)

                stok_kol -= jumlah
                simpan_stok(stok_kol)

                df_keuangan = load_data(KEUANGAN_FILE)
                tanggal_str = tanggal_jual.strftime("%Y-%m-%d")
                transaksi_keuangan = pd.DataFrame([
                    {"Tanggal": tanggal_str, "Keterangan": "Kas", "Debit": total, "Kredit": 0},
                    {"Tanggal": tanggal_str, "Keterangan": "     Penjualan Kol", "Debit": 0, "Kredit": total}
                ])
                df_keuangan = pd.concat([df_keuangan, transaksi_keuangan], ignore_index=True)
                simpan_data(df_keuangan, KEUANGAN_FILE)

                st.success("✅ Data penjualan dan laporan keuangan disimpan!")

        st.subheader("Riwayat Transaksi Penjualan")
        df_penjualan = load_data(PENJUALAN_FILE)
        if not df_penjualan.empty:
            df_penjualan["Tanggal"] = pd.to_datetime(df_penjualan["Tanggal"], errors='coerce')
            df_penjualan = df_penjualan.dropna(subset=['Tanggal'])
            df_penjualan = df_penjualan.sort_values("Tanggal", ascending=False).reset_index(drop=True)

            df_display = df_penjualan.copy()
            df_display["Tanggal"] = df_display["Tanggal"].dt.strftime("%d %B %Y")

            st.dataframe(df_display, use_container_width=True)

            st.markdown("### 🧹 Hapus Transaksi Penjualan")
            opsi_hapus = st.selectbox(
                "Pilih transaksi yang ingin dihapus:",
                options=[
                    f"{i+1}. {row['Tanggal'].strftime('%Y-%m-%d')} | {int(row['Jumlah Kol (Kg)']):,} Kg | Total Rp {int(row['Total Penjualan']):,}".replace(",", ".") 
                    for i, row in df_penjualan.iterrows()
                ],
                key="pilih_hapus_penjualan"
            )

            if opsi_hapus:
                index_hapus = int(opsi_hapus.split(".")[0]) - 1
                row = df_penjualan.iloc[index_hapus]

                if st.button("🗑 Hapus Transaksi Ini"):
                    # Kembalikan stok kol
                    stok_kol = load_stok()
                    stok_kol += row["Jumlah Kol (Kg)"]
                    simpan_stok(stok_kol)

                    # Hapus baris dari data penjualan
                    df_penjualan = df_penjualan.drop(index=index_hapus).reset_index(drop=True)
                    simpan_data(df_penjualan, PENJUALAN_FILE)

                    # Hapus dari laporan keuangan
                    df_keuangan = load_data(KEUANGAN_FILE)
                    tanggal_str = row["Tanggal"].strftime("%Y-%m-%d")
                    total = row["Total Penjualan"]
                    df_keuangan = df_keuangan[~(
                        (df_keuangan['Tanggal'] == tanggal_str) &
                        (((df_keuangan['Keterangan'].str.strip() == "Kas") & (df_keuangan['Debit'] == total)) |
                         ((df_keuangan['Keterangan'].str.strip() == "Penjualan Kol") & (df_keuangan['Kredit'] == total)))
                    )]
                    simpan_data(df_keuangan, KEUANGAN_FILE)

                    st.success("✅ Transaksi penjualan dan data keuangan berhasil dihapus.")
        else:
            st.info("Belum ada data penjualan.")

    # HALAMAN ISI STOK
    elif halaman == 'Isi Stok':
        st.title(":material/warehouse: Pengisian/Pengurangan Stok Kol")
        stok_sekarang = load_stok()
        st.markdown(f" *Stok Saat Ini:* {stok_sekarang} Kg")

        tanggal_stok = st.date_input("Tanggal", value=datetime.today())
        mode = st.radio("Pilih Aksi", ["Tambah Stok", "Kurangi Stok"], horizontal=True)
        jumlah = st.number_input("Jumlah (Kg)", 0)
        keterangan = st.text_input("Keterangan (opsional)")

        if st.button(":material/save: Simpan"):
            if jumlah <= 0:
                st.warning("⚠️ Masukkan jumlah yang lebih dari 0.")
            else:
                if mode == "Tambah Stok":
                    stok_baru = stok_sekarang + jumlah
                    aksi = "ditambahkan"
                else:
                    if jumlah > stok_sekarang:
                        st.error("❌ Jumlah pengurangan melebihi stok saat ini!")
                        st.stop()
                    stok_baru = stok_sekarang - jumlah
                    aksi = "dikurangi"

                simpan_stok(stok_baru)

                df_pengisian = load_data(PENGISIAN_STOK_FILE)
                new_entry = pd.DataFrame([{
                    "Tanggal": tanggal_stok.strftime("%Y-%m-%d"),
                    "Aksi": "Tambah" if mode == "Tambah Stok" else "Kurang",
                    "Jumlah (Kg)": jumlah,
                    "Keterangan": keterangan
                }])
                df_pengisian = pd.concat([df_pengisian, new_entry], ignore_index=True)
                simpan_data(df_pengisian, PENGISIAN_STOK_FILE)

                st.success(f"✅ Stok berhasil {aksi} sebanyak {jumlah} Kg. Stok saat ini: {stok_baru} Kg")

        st.subheader(" Riwayat Pengisian/Pengurangan Stok")
        df_pengisian = load_data(PENGISIAN_STOK_FILE)
        if not df_pengisian.empty:
            df_pengisian["Tanggal"] = pd.to_datetime(df_pengisian["Tanggal"])
            df_pengisian = df_pengisian.sort_values("Tanggal", ascending=False)
            st.dataframe(df_pengisian)
        else:
            st.info("Belum ada riwayat pengisian atau pengurangan stok.")

    # HALAMAN LAPORAN
    elif halaman == 'Laporan Keuangan':
        st.title(":material/request_quote: Jurnal Umum")
        df = load_data(KEUANGAN_FILE)
        if df.empty:
            st.info("Belum ada data keuangan.")
            st.stop()
        else:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df = df.sort_values("Tanggal")

        total_debit = df["Debit"].sum()
        total_kredit = df["Kredit"].sum()

        total_row = pd.DataFrame([{
            "Tanggal": "",
            "Keterangan": " Total  ",
            "Debit": total_debit,
            "Kredit": total_kredit
        }])
        df_final = pd.concat([df, total_row], ignore_index=True)

        df_final["Tanggal"] = pd.to_datetime(df_final["Tanggal"], errors='coerce')
        df_final["Tanggal"] = df_final["Tanggal"].apply(lambda x: f"{x.day} {x.strftime('%B')}" if pd.notnull(x) else "")
        df_final["Debit"] = df_final["Debit"].apply(lambda x: f"{x:,.0f}" if x != 0 else "")
        df_final["Kredit"] = df_final["Kredit"].apply(lambda x: f"{x:,.0f}" if x != 0 else "")

        st.dataframe(df_final[["Tanggal", "Keterangan", "Debit", "Kredit"]], use_container_width=True)

        saldo = total_debit - total_kredit
        st.markdown(f"""
        -  *Total Pemasukan (Debit):* Rp {total_debit:,.0f}  
        -  *Total Pengeluaran (Kredit):* Rp {total_kredit:,.0f}  
        """)

        if st.button("🗑 Hapus Semua Data"):
            pd.DataFrame().to_csv(KEUANGAN_FILE)
            pd.DataFrame().to_csv(PRODUKSI_FILE)
            pd.DataFrame().to_csv(PENJUALAN_FILE)
            pd.DataFrame().to_csv(PENGISIAN_STOK_FILE)
            pd.DataFrame([{"Stok": 1000}]).to_csv(STOK_FILE, index=False)
            st.warning("Semua data dihapus dan stok direset ke 1000 Kg.")

        st.subheader("Buku Besar")

        df_buku_besar = df.copy()
    
        df_kas = df_buku_besar[df_buku_besar["Keterangan"].str.strip() == "Kas"].copy()
        if not df_kas.empty:
            df_kas = df_kas.groupby('Tanggal').agg({
                'Debit': 'sum',
                'Kredit': 'sum',
                'Keterangan': 'first'
            }).reset_index()
        
        df_non_kas = df_buku_besar[df_buku_besar["Keterangan"].str.strip() != "Kas"]
        df_buku_besar = pd.concat([df_non_kas, df_kas], ignore_index=True)
    
        akun_list = sorted(df_buku_besar["Keterangan"].str.strip().unique())
        selected_akun = st.selectbox("Pilih Akun:", akun_list)

        df_akun = df_buku_besar[df_buku_besar["Keterangan"].str.strip() == selected_akun].copy()
        df_akun = df_akun.sort_values("Tanggal").reset_index(drop=True)

        if selected_akun == "Kas":
            df_akun["Saldo"] = (df_akun["Debit"] - df_akun["Kredit"]).cumsum()
        elif selected_akun in ["Penjualan Kol", "Modal"]:
            df_akun["Saldo"] = (df_akun["Kredit"] - df_akun["Debit"]).cumsum()
        else:
            df_akun["Saldo"] = (df_akun["Debit"] - df_akun["Kredit"]).cumsum()

        df_akun_display = df_akun.copy()
        df_akun_display["Tanggal"] = df_akun_display["Tanggal"].dt.strftime("%d %b %Y")
        df_akun_display["Debit"] = df_akun_display["Debit"].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_akun_display["Kredit"] = df_akun_display["Kredit"].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_akun_display["Saldo"] = df_akun_display["Saldo"].apply(lambda x: f"Rp {x:,.0f}")

        st.dataframe(
            df_akun_display[["Tanggal", "Keterangan", "Debit", "Kredit", "Saldo"]], 
            use_container_width=True,
            column_config={
                "Debit": st.column_config.Column(width="small"),
                "Kredit": st.column_config.Column(width="small"),
                "Saldo": st.column_config.Column(width="small")
        }
    )

    # ========== NERACA SALDO ==========
        st.subheader("Neraca Saldo")
    
        df_neraca = df.copy()
    
    # Kelompokkan berdasarkan akun dan hitung total debit/kredit
        df_neraca = df_neraca.groupby('Keterangan').agg({
            'Debit': 'sum',
            'Kredit': 'sum'
        }).reset_index()

    # Hitung saldo untuk masing-masing akun
        def hitung_saldo(row):
            akun = row['Keterangan'].strip()
            if akun in ["Kas"]:  # Akun aktiva
                return row['Debit'] - row['Kredit']
            elif akun in ["Penjualan Kol"]:  # Akun pendapatan
                return row['Kredit'] - row['Debit']
            else:  # Beban dan lainnya
                return row['Debit'] - row['Kredit']

        df_neraca['Saldo'] = df_neraca.apply(hitung_saldo, axis=1)

    # Klasifikasi akun
        def klasifikasi_akun(akun):
            akun = akun.strip()
            if akun == "Kas":
                return "Aktiva"
            elif akun == "Penjualan Kol":
                return "Pendapatan"
            elif akun == "Beban Produksi":
                return "Beban"
            else:
                return "Lainnya"

        df_neraca['Klasifikasi'] = df_neraca['Keterangan'].apply(klasifikasi_akun)

    # Format tampilan
        df_neraca_display = df_neraca.copy()
        df_neraca_display['Debit'] = df_neraca_display['Debit'].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_neraca_display['Kredit'] = df_neraca_display['Kredit'].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_neraca_display['Saldo'] = df_neraca_display['Saldo'].apply(lambda x: f"Rp {x:,.0f}")

    # Tampilkan neraca saldo
        st.dataframe(
            df_neraca_display[['Keterangan', 'Klasifikasi', 'Debit', 'Kredit', 'Saldo']],
            use_container_width=True,
            hide_index=True
        )

    # Hitung total debit dan kredit
        total_debit_neraca = df_neraca['Debit'].sum()
        total_kredit_neraca = df_neraca['Kredit'].sum()

        st.markdown(f"""
        **Total Debit:** Rp {total_debit_neraca:,.0f}  
        **Total Kredit:** Rp {total_kredit_neraca:,.0f}  
        **Selisih:** Rp {abs(total_debit_neraca - total_kredit_neraca):,.0f}
        """)

        if total_debit_neraca == total_kredit_neraca:
            st.success("✅ Neraca seimbang")
        else:
            st.error("❌ Neraca tidak seimbang! Periksa kembali entri jurnal.")
