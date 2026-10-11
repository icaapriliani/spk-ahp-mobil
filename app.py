import streamlit as st
import pandas as pd
import numpy as np
import itertools
from utils.ahp_logic import calculate_priority_vector, calculate_consistency_ratio

def init_session_state():
    if 'kriteria' not in st.session_state:
        st.session_state.kriteria = []
    if 'alternatif' not in st.session_state:
        st.session_state.alternatif = []
    if 'matriks_kriteria' not in st.session_state:
        st.session_state.matriks_kriteria = pd.DataFrame()

def main():
    st.set_page_config(
        page_title="Sistem Pendukung Keputusan AHP",
        page_icon="📊",
        layout="wide"
    )
    
    init_session_state()

    st.title("📊 Sistem Pendukung Keputusan (SPK) - Metode AHP")
    st.markdown("Aplikasi ini dirancang secara umum sehingga Anda dapat menentukan sendiri kriteria dan alternatif yang akan dibandingkan.")
    
    st.divider()

    # Skala Saaty untuk AHP
    skala_ahp = {
        "1 - Sama Penting (Equal)": 1,
        "2 - Nilai Antara 1 dan 3": 2,
        "3 - Sedikit Lebih Penting (Moderate)": 3,
        "4 - Nilai Antara 3 dan 5": 4,
        "5 - Jelas Lebih Penting (Strong)": 5,
        "6 - Nilai Antara 5 dan 7": 6,
        "7 - Sangat Jelas Lebih Penting (Very Strong)": 7,
        "8 - Nilai Antara 7 dan 9": 8,
        "9 - Mutlak Lebih Penting (Extreme)": 9
    }

    # Menggunakan sistem Tab untuk merapikan antarmuka
    tab1, tab2, tab3, tab4 = st.tabs(["📝 1. Input Data", "⚖️ 2. Perbandingan Kriteria", "⚖️ 3. Perbandingan Alternatif", "🏆 4. Hasil Akhir"])

    with tab1:
        col1, col2 = st.columns(2)

        # Fungsi callback untuk mengosongkan input otomatis setelah ditambah
        def submit_kriteria():
            kb = st.session_state.input_kriteria.strip()
            if kb:
                if kb not in st.session_state.kriteria:
                    st.session_state.kriteria.append(kb)
                else:
                    st.toast("Kriteria sudah ada!", icon="⚠️")
            st.session_state.input_kriteria = ""

        def submit_alternatif():
            ab = st.session_state.input_alternatif.strip()
            if ab:
                if ab not in st.session_state.alternatif:
                    st.session_state.alternatif.append(ab)
                else:
                    st.toast("Alternatif sudah ada!", icon="⚠️")
            st.session_state.input_alternatif = ""

        with col1:
            st.subheader("Input Kriteria")
            st.text_input("Tambah Kriteria Baru:", key="input_kriteria", on_change=submit_kriteria)
            st.button("Tambah Kriteria", type="primary", on_click=submit_kriteria)
                    
            if st.session_state.kriteria:
                df_kriteria = pd.DataFrame(st.session_state.kriteria, columns=["Nama Kriteria"], index=range(1, len(st.session_state.kriteria) + 1))
                st.dataframe(df_kriteria, use_container_width=True)
                if st.button("Hapus Semua Kriteria"):
                    st.session_state.kriteria = []
                    st.rerun()

        with col2:
            st.subheader("Input Alternatif")
            st.text_input("Tambah Alternatif Baru:", key="input_alternatif", on_change=submit_alternatif)
            st.button("Tambah Alternatif", type="primary", on_click=submit_alternatif)
                    
            if st.session_state.alternatif:
                df_alternatif = pd.DataFrame(st.session_state.alternatif, columns=["Nama Alternatif"], index=range(1, len(st.session_state.alternatif) + 1))
                st.dataframe(df_alternatif, use_container_width=True)
                if st.button("Hapus Semua Alternatif"):
                    st.session_state.alternatif = []
                    st.rerun()

    with tab2:
        st.subheader("Perbandingan Berpasangan Antar Kriteria")
        if len(st.session_state.kriteria) < 2:
            st.warning("Silakan masukkan minimal 2 kriteria pada tab 'Input Data' terlebih dahulu.")
        else:
            kriteria = st.session_state.kriteria
            n = len(kriteria)
            
            st.info("💡 **Petunjuk:** Pilih kriteria mana yang lebih penting di antara keduanya, lalu tentukan seberapa jauh tingkat kepentingannya berdasarkan skala 1-9.")
            
            # Membuat kombinasi unik untuk setiap pasangan kriteria
            pairs = list(itertools.combinations(kriteria, 2))
            
            if 'perbandingan_kriteria' not in st.session_state:
                st.session_state.perbandingan_kriteria = {}
                
            for p in pairs:
                st.markdown(f"**{p[0]} vs {p[1]}**")
                col1, col2 = st.columns(2)
                
                with col1:
                    lebih_penting = st.radio(
                        f"Kriteria yang lebih penting:",
                        options=[p[0], p[1]],
                        key=f"penting_{p[0]}_{p[1]}",
                        horizontal=True
                    )
                with col2:
                    val = st.selectbox(
                        "Tingkat kepentingan:",
                        options=list(skala_ahp.keys()),
                        key=f"skala_{p[0]}_{p[1]}"
                    )
                
                # Menyimpan bobot berdasarkan pilihan
                nilai_angka = skala_ahp[val]
                if lebih_penting == p[0]:
                    st.session_state.perbandingan_kriteria[(p[0], p[1])] = nilai_angka
                else:
                    st.session_state.perbandingan_kriteria[(p[0], p[1])] = 1 / nilai_angka
                    
                st.markdown("---")
            
            if st.button("Simpan & Buat Matriks Kriteria", type="primary"):
                # Membuat matriks n x n berisi angka 1
                matrix = np.ones((n, n))
                for i in range(n):
                    for j in range(i+1, n):
                        k1 = kriteria[i]
                        k2 = kriteria[j]
                        val = st.session_state.perbandingan_kriteria.get((k1, k2), 1)
                        # Mengisi matriks bagian atas dan bawah diagonal
                        matrix[i, j] = val
                        matrix[j, i] = 1 / val if val != 0 else 1
                        
                df_matrix = pd.DataFrame(matrix, index=kriteria, columns=kriteria)
                st.session_state.matriks_kriteria = df_matrix
                st.success("Matriks berhasil dibuat dan disimpan!")
                
            if not st.session_state.matriks_kriteria.empty:
                st.write("**Matriks Perbandingan Berpasangan Kriteria:**")
                st.dataframe(st.session_state.matriks_kriteria.style.format("{:.2f}"))
                
                # --- PERHITUNGAN AHP ---
                mat_kriteria = st.session_state.matriks_kriteria.values
                prioritas = calculate_priority_vector(mat_kriteria)
                cr, is_consistent = calculate_consistency_ratio(mat_kriteria, prioritas)
                
                # Simpan bobot ke session state untuk Tab berikutnya
                st.session_state.bobot_kriteria = pd.Series(prioritas, index=kriteria)
                
                st.subheader("Hasil Analisis Kriteria")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Bobot Prioritas Kriteria:**")
                    df_prioritas = pd.DataFrame({
                        "Kriteria": kriteria,
                        "Bobot": prioritas
                    }).sort_values(by="Bobot", ascending=False)
                    st.dataframe(df_prioritas.style.format({"Bobot": "{:.4f}"}), use_container_width=True)
                    
                with col2:
                    st.write("**Uji Konsistensi:**")
                    st.metric(label="Consistency Ratio (CR)", value=f"{cr:.4f}")
                    if is_consistent:
                        st.success("✅ Nilai CR <= 0.1, matriks KONSISTEN. Anda bisa melanjutkan ke tahap berikutnya.")
                    else:
                        st.error("❌ Nilai CR > 0.1, matriks TIDAK KONSISTEN. Penilaian kurang logis. Silakan ubah kembali nilai perbandingan di atas!")

    with tab3:
        st.subheader("Perbandingan Alternatif terhadap Kriteria")
        if len(st.session_state.alternatif) < 2:
            st.warning("Silakan masukkan minimal 2 alternatif pada tab 'Input Data' terlebih dahulu.")
        elif not st.session_state.kriteria:
            st.warning("Data kriteria belum ada.")
        else:
            kriteria = st.session_state.kriteria
            alternatif = st.session_state.alternatif
            m = len(alternatif)
            
            if 'perbandingan_alternatif' not in st.session_state:
                st.session_state.perbandingan_alternatif = {}
                
            # Pastikan DataFrame selalu sesuai dengan kriteria dan alternatif saat ini
            if 'bobot_alternatif' not in st.session_state or \
               list(st.session_state.bobot_alternatif.index) != alternatif or \
               list(st.session_state.bobot_alternatif.columns) != kriteria:
                st.session_state.bobot_alternatif = pd.DataFrame(index=alternatif, columns=kriteria, dtype=float)
                
            st.info("Bandingkan alternatif-alternatif yang ada berdasarkan masing-masing kriteria. Jika ada 3 kriteria, Anda harus membandingkan alternatif sebanyak 3 kali.")
            
            # Membuat expander untuk setiap kriteria
            for k in kriteria:
                with st.expander(f"Bandingkan Alternatif Berdasarkan Kriteria: {k}", expanded=False):
                    pairs_alt = list(itertools.combinations(alternatif, 2))
                    
                    for p in pairs_alt:
                        col1, col2 = st.columns(2)
                        with col1:
                            lebih_penting = st.radio(
                                f"Alternatif yang lebih baik ({p[0]} vs {p[1]}):",
                                options=[p[0], p[1]],
                                key=f"penting_alt_{k}_{p[0]}_{p[1]}",
                                horizontal=True
                            )
                        with col2:
                            val = st.selectbox(
                                "Tingkat kepentingan:",
                                options=list(skala_ahp.keys()),
                                key=f"skala_alt_{k}_{p[0]}_{p[1]}"
                            )
                        
                        nilai_angka = skala_ahp[val]
                        if lebih_penting == p[0]:
                            st.session_state.perbandingan_alternatif[(k, p[0], p[1])] = nilai_angka
                        else:
                            st.session_state.perbandingan_alternatif[(k, p[0], p[1])] = 1 / nilai_angka
                            
                        st.markdown("---")
                            
                    if st.button(f"Simpan & Hitung Bobot ({k})", key=f"btn_{k}"):
                        matrix_alt = np.ones((m, m))
                        for i in range(m):
                            for j in range(i+1, m):
                                a1 = alternatif[i]
                                a2 = alternatif[j]
                                val = st.session_state.perbandingan_alternatif.get((k, a1, a2), 1)
                                matrix_alt[i, j] = val
                                matrix_alt[j, i] = 1 / val if val != 0 else 1
                        
                        # Simpan matriks alternatif untuk diekspor ke Excel nanti
                        if 'matriks_alternatif_dict' not in st.session_state:
                            st.session_state.matriks_alternatif_dict = {}
                        st.session_state.matriks_alternatif_dict[k] = pd.DataFrame(matrix_alt, index=alternatif, columns=alternatif)
                                
                        prioritas_alt = calculate_priority_vector(matrix_alt)
                        cr_alt, is_cons_alt = calculate_consistency_ratio(matrix_alt, prioritas_alt)
                        
                        # Simpan bobot ke session state
                        st.session_state.bobot_alternatif[k] = prioritas_alt
                        
                        st.write(f"**CR:** {cr_alt:.4f}")
                        if is_cons_alt:
                            st.success(f"✅ Matriks Alternatif untuk kriteria {k} KONSISTEN")
                        else:
                            st.error(f"❌ Matriks Alternatif untuk kriteria {k} TIDAK KONSISTEN")
                            
            st.divider()
            if not st.session_state.bobot_alternatif.isna().all().all():
                st.subheader("Rangkuman Bobot Alternatif")
                st.dataframe(st.session_state.bobot_alternatif.style.format("{:.4f}"))

    with tab4:
        st.subheader("Hasil Akhir dan Visualisasi")
        if 'bobot_kriteria' not in st.session_state or 'bobot_alternatif' not in st.session_state:
            st.warning("Data belum lengkap. Silakan selesaikan pengisian matriks kriteria dan alternatif terlebih dahulu.")
        elif st.session_state.bobot_alternatif.isna().any().any():
            st.warning("Bobot alternatif belum lengkap untuk semua kriteria. Pastikan Anda telah mengklik tombol 'Simpan & Hitung Bobot' untuk SETIAP kriteria di Tab 3.")
        else:
            st.info("Semua data telah lengkap! Berikut adalah hasil perhitungan akhir.")
            
            # Hitung skor akhir = matriks bobot alternatif dikali vektor bobot kriteria
            hasil_akhir = st.session_state.bobot_alternatif.dot(st.session_state.bobot_kriteria)
            
            # Membuat DataFrame untuk hasil dan diurutkan dari skor terbesar
            df_hasil = pd.DataFrame(hasil_akhir, columns=["Skor Akhir"]).sort_values(by="Skor Akhir", ascending=False)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("**🏆 Peringkat Alternatif:**")
                st.dataframe(df_hasil.style.format("{:.4f}"), use_container_width=True)
                
            with col2:
                # Membuat visualisasi bar chart menggunakan Plotly
                import plotly.express as px
                fig = px.bar(df_hasil.reset_index(), x='index', y='Skor Akhir', 
                             title='Grafik Skor Akhir Alternatif',
                             labels={'index': 'Alternatif', 'Skor Akhir': 'Skor Akhir'},
                             color='Skor Akhir', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
                
            pemenang = df_hasil.index[0]
            st.success(f"🎉 **Kesimpulan:** Berdasarkan perhitungan metode AHP, alternatif terbaik yang direkomendasikan adalah **{pemenang}** dengan skor tertinggi **{df_hasil.iloc[0, 0]:.4f}**.")
            
            st.divider()
            st.subheader("Unduh Laporan Lengkap (Excel)")
            st.write("Anda dapat mengunduh seluruh proses pengerjaan AHP (Mulai dari matriks awal hingga hasil akhir) dalam bentuk file Excel.")
            
            # --- FUNGSI EXPORT EXCEL ---
            from utils.excel_generator import create_ahp_excel
            
            # Jika user belum menghitung ulang alternatif di tab 3, kita ambil dari state yang ada
            matriks_alt_dict = st.session_state.get('matriks_alternatif_dict', {})
            
            excel_data = create_ahp_excel(
                st.session_state.kriteria, 
                st.session_state.alternatif, 
                st.session_state.matriks_kriteria, 
                matriks_alt_dict
            )
            
            st.download_button(
                label="📥 Unduh Laporan Excel (Dengan Rumus)",
                data=excel_data,
                file_name="Laporan_Perhitungan_AHP_Lengkap.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

if __name__ == "__main__":
    main()
