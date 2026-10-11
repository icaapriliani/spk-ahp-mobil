import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

def create_ahp_excel(kriteria, alternatif, matriks_kriteria, matriks_alternatif_dict):
    wb = Workbook()
    ws = wb.active
    ws.title = "Perhitungan AHP"
    
    # Styles
    font_bold = Font(bold=True)
    fill_yellow = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    fill_header = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    fill_peach = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    fill_green = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    border_thin = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    align_center = Alignment(horizontal='center', vertical='center')
    
    n_k = len(kriteria)
    n_a = len(alternatif)
    
    def apply_style(start_r, start_c, end_r, end_c, fill=None, bold=False, center=True):
        for r in range(start_r, end_r + 1):
            for c in range(start_c, end_c + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = border_thin
                if fill:
                    cell.fill = fill
                if bold:
                    cell.font = font_bold
                if center:
                    cell.alignment = align_center

    current_row = 1
    ws.cell(row=current_row, column=1, value="SISTEM PENDUKUNG KEPUTUSAN - METODE AHP").font = Font(bold=True, size=14)
    current_row += 2

    # --- 1. DATA AWAL ---
    ws.cell(row=current_row, column=1, value="1. DATA AWAL").font = font_bold
    current_row += 1
    ws.cell(row=current_row, column=1, value="Kriteria").font = font_bold
    ws.cell(row=current_row, column=2, value="Alternatif").font = font_bold
    apply_style(current_row, 1, current_row, 2, fill=fill_header, bold=True)
    
    max_len = max(n_k, n_a)
    for i in range(max_len):
        if i < n_k:
            ws.cell(row=current_row + 1 + i, column=1, value=kriteria[i])
        if i < n_a:
            ws.cell(row=current_row + 1 + i, column=2, value=alternatif[i])
    apply_style(current_row + 1, 1, current_row + max_len, 2)
    current_row += max_len + 3

    # ==========================================
    # FUNGSI PEMBANTU: MATRIKS & UJI KONSISTENSI
    # ==========================================
    def build_matrix_and_consistency(title, items, input_matrix, is_criteria=True):
        nonlocal current_row
        n = len(items)
        ws.cell(row=current_row, column=1, value=title).font = font_bold
        current_row += 1
        
        # 1. Matriks Perbandingan Awal
        start_matrix_r = current_row
        ws.cell(row=current_row, column=1, value="Elemen")
        for j, item in enumerate(items):
            ws.cell(row=current_row, column=j+2, value=item)
            ws.cell(row=current_row+1+j, column=1, value=item)
        apply_style(current_row, 1, current_row, n+1, fill=fill_yellow, bold=True)
        apply_style(current_row+1, 1, current_row+n, 1, fill=fill_yellow, bold=True)
        
        for i in range(n):
            for j in range(n):
                cell = ws.cell(row=current_row+1+i, column=j+2)
                if i == j:
                    cell.value = 1
                elif i < j:
                    val = input_matrix.iloc[i, j] if input_matrix is not None else 1
                    cell.value = float(val)
                else:
                    col_letter = get_column_letter(i+2)
                    row_num = current_row+1+j
                    cell.value = f"=1/{col_letter}{row_num}"
                    
        apply_style(current_row+1, 2, current_row+n, n+1)
        
        # Baris TOTAL Matriks Awal
        current_row += n + 1
        ws.cell(row=current_row, column=1, value="TOTAL")
        total_awal_cells = []
        for j in range(n):
            col_letter = get_column_letter(j+2)
            c = ws.cell(row=current_row, column=j+2, value=f"=SUM({col_letter}{start_matrix_r+1}:{col_letter}{current_row-1})")
            total_awal_cells.append(f"{col_letter}{current_row}")
        apply_style(current_row, 1, current_row, n+1, fill=fill_header, bold=True)
        
        current_row += 2
        
        # 2. Matriks Normalisasi, Vektor, Bobot & Eigen Value
        start_norm_r = current_row
        ws.cell(row=current_row, column=1, value="Kriteria" if is_criteria else "Alternatif")
        for j, item in enumerate(items):
            ws.cell(row=current_row, column=j+2, value=item)
        ws.cell(row=current_row, column=n+2, value="Vektor")
        ws.cell(row=current_row, column=n+3, value="Bobot")
        ws.cell(row=current_row, column=n+4, value="Eigen Value")
        apply_style(current_row, 1, current_row, n+4, fill=fill_yellow, bold=True)
        
        bobot_cells = []
        for i in range(n):
            ws.cell(row=current_row+1+i, column=1, value=items[i])
            for j in range(n):
                col_letter = get_column_letter(j+2)
                val_c = f"{col_letter}{start_matrix_r+1+i}"
                tot_c = total_awal_cells[j]
                ws.cell(row=current_row+1+i, column=j+2, value=f"={val_c}/{tot_c}")
                
            # Vektor = Penjumlahan tiap baris
            start_c = get_column_letter(2)
            end_c = get_column_letter(n+1)
            ws.cell(row=current_row+1+i, column=n+2, value=f"=SUM({start_c}{current_row+1+i}:{end_c}{current_row+1+i})")
            
            # Bobot = Vektor / n
            vektor_c = f"{get_column_letter(n+2)}{current_row+1+i}"
            b_cell = ws.cell(row=current_row+1+i, column=n+3, value=f"={vektor_c}/{n}")
            bobot_cells.append(f"{get_column_letter(n+3)}{current_row+1+i}")
            
            # Eigen Value = Bobot * Total Kolom ke-i matriks awal
            eigen_formula = f"={b_cell.coordinate}*{total_awal_cells[i]}"
            ws.cell(row=current_row+1+i, column=n+4, value=eigen_formula)
            
        apply_style(current_row+1, 1, current_row+n, n+4)
        
        # Baris TOTAL Normalisasi
        current_row += n + 1
        ws.cell(row=current_row, column=1, value="TOTAL")
        for j in range(n):
            col_letter = get_column_letter(j+2)
            ws.cell(row=current_row, column=j+2, value=f"=SUM({col_letter}{start_norm_r+1}:{col_letter}{current_row-1})")
        # Total Eigen Value
        eigen_col = get_column_letter(n+4)
        tot_eigen_cell = ws.cell(row=current_row, column=n+4, value=f"=SUM({eigen_col}{start_norm_r+1}:{eigen_col}{current_row-1})")
        apply_style(current_row, 1, current_row, n+4, fill=fill_header, bold=True)
        
        # 3. Nilai CI, CR, dan Keterangan Konsisten
        current_row += 1
        ws.cell(row=current_row, column=n+3, value="CI").font = font_bold
        ci_cell = ws.cell(row=current_row, column=n+4, value=f"=({tot_eigen_cell.coordinate}-{n})/({n}-1)" if n > 1 else 0)
        apply_style(current_row, n+3, current_row, n+4)
        
        current_row += 1
        ws.cell(row=current_row, column=n+3, value="CR").font = font_bold
        ri_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        ri = ri_dict.get(n, 1.49)
        cr_formula = f"=IF({ri}=0, 0, {ci_cell.coordinate}/{ri})"
        cr_cell = ws.cell(row=current_row, column=n+4, value=cr_formula)
        
        # Badge Keterangan Konsisten persis seperti di gambar
        status_cell = ws.cell(row=current_row, column=n+5, value=f'=IF({cr_cell.coordinate}<=0.1, "Konsisten", "Tidak Konsisten")')
        status_cell.font = font_bold
        status_cell.fill = fill_peach
        status_cell.alignment = align_center
        status_cell.border = border_thin
        apply_style(current_row, n+3, current_row, n+4)
        
        current_row += 3
        return bobot_cells

    # --- 2. PERHITUNGAN KRITERIA ---
    bobot_kriteria_cells = build_matrix_and_consistency(
        "2. MATRIKS PERBANDINGAN DAN NORMALISASI KRITERIA",
        kriteria,
        matriks_kriteria,
        is_criteria=True
    )

    # --- 3. PERHITUNGAN ALTERNATIF PER KRITERIA ---
    ws.cell(row=current_row, column=1, value="3. MATRIKS PERBANDINGAN ALTERNATIF TERHADAP TIAP KRITERIA").font = font_bold
    current_row += 1
    
    # Simpan bobot alternatif per kriteria: dict k -> list of cell refs
    bobot_alternatif_per_k = {}
    for k in kriteria:
        mat_alt = matriks_alternatif_dict.get(k)
        bobot_alt_cells = build_matrix_and_consistency(
            f"Perbandingan Alternatif berdasarkan Kriteria: {k}",
            alternatif,
            mat_alt,
            is_criteria=False
        )
        bobot_alternatif_per_k[k] = bobot_alt_cells

    # --- 4. HASIL MATRIK SKOR ALTERNATIF & PERANGKINGAN ---
    ws.cell(row=current_row, column=1, value="Hasil Matrik Skor Alternatif").font = Font(bold=True, size=12)
    current_row += 1
    
    # Tabel 1: Rekap Bobot Alternatif & Nilai Bobot Kriteria
    start_rekap_r = current_row
    ws.cell(row=current_row, column=1, value="Skor")
    for j, k in enumerate(kriteria):
        ws.cell(row=current_row, column=j+2, value=k)
    apply_style(current_row, 1, current_row, n_k+1, fill=fill_yellow, bold=True)
    
    # Kolom Kriteria & Nilai Bobot di sebelah kanannya
    ws.cell(row=current_row, column=n_k+3, value="Kriteria")
    ws.cell(row=current_row, column=n_k+4, value="Nilai Bobot")
    apply_style(current_row, n_k+3, current_row, n_k+4, fill=fill_yellow, bold=True)
    
    for i, a in enumerate(alternatif):
        ws.cell(row=current_row+1+i, column=1, value=a).font = font_bold
        for j, k in enumerate(kriteria):
            ref = bobot_alternatif_per_k[k][i]
            ws.cell(row=current_row+1+i, column=j+2, value=f"={ref}")
            
    for j, k in enumerate(kriteria):
        ws.cell(row=current_row+1+j, column=n_k+3, value=k)
        ws.cell(row=current_row+1+j, column=n_k+4, value=f"={bobot_kriteria_cells[j]}")
        
    apply_style(current_row+1, 1, current_row+n_a, n_k+1)
    apply_style(current_row+1, n_k+3, current_row+n_k, n_k+4)
    current_row += max(n_a, n_k) + 3

    # Tabel 2: Perkalian Bobot Alternatif * Bobot Kriteria, Total NILAI, dan SKOR (Rank)
    start_calc_r = current_row
    ws.cell(row=current_row, column=1, value="Skor")
    for j, k in enumerate(kriteria):
        ws.cell(row=current_row, column=j+2, value=k)
    ws.cell(row=current_row, column=n_k+2, value="NILAI")
    ws.cell(row=current_row, column=n_k+3, value="SKOR")
    apply_style(current_row, 1, current_row, n_k+3, fill=fill_yellow, bold=True)
    
    nilai_cells = []
    for i, a in enumerate(alternatif):
        ws.cell(row=current_row+1+i, column=1, value=a).font = font_bold
        row_mul_cells = []
        for j, k in enumerate(kriteria):
            # Sel bobot alternatif di tabel rekap 1
            alt_ref = f"{get_column_letter(j+2)}{start_rekap_r+1+i}"
            # Sel bobot kriteria di tabel rekap 1
            crit_ref = f"${get_column_letter(n_k+4)}${start_rekap_r+1+j}"
            ws.cell(row=current_row+1+i, column=j+2, value=f"={alt_ref}*{crit_ref}")
            row_mul_cells.append(f"{get_column_letter(j+2)}{current_row+1+i}")
            
        # NILAI = SUM perkalian
        c_start = get_column_letter(2)
        c_end = get_column_letter(n_k+1)
        ws.cell(row=current_row+1+i, column=n_k+2, value=f"=SUM({c_start}{current_row+1+i}:{c_end}{current_row+1+i})")
        nilai_cells.append(f"{get_column_letter(n_k+2)}{current_row+1+i}")
        
    # SKOR = RANK formula
    rank_range = f"${get_column_letter(n_k+2)}${start_calc_r+1}:${get_column_letter(n_k+2)}${start_calc_r+n_a}"
    for i in range(n_a):
        n_c = f"{get_column_letter(n_k+2)}{start_calc_r+1+i}"
        ws.cell(row=start_calc_r+1+i, column=n_k+3, value=f"=RANK({n_c}, {rank_range})")
        
    apply_style(start_calc_r+1, 1, start_calc_r+n_a, n_k+3)
    
    # Tambahkan Grafik Perangkingan AHP (BarChart)
    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = "Grafik Perangkingan AHP"
    chart.y_axis.title = "Nilai Bobot"
    chart.x_axis.title = "Alternatif"
    chart.width = 15
    chart.height = 8
    
    data = Reference(ws, min_col=n_k+2, min_row=start_calc_r, max_row=start_calc_r+n_a)
    cats = Reference(ws, min_col=1, min_row=start_calc_r+1, max_row=start_calc_r+n_a)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.legend = None
    
    chart_col = get_column_letter(n_k+5)
    ws.add_chart(chart, f"{chart_col}{start_rekap_r}")
    
    current_row += n_a + 2

    # Kesimpulan & Tabel Ranking Bawah
    ws.cell(row=current_row, column=1, value="Hasil diatas menunjukkan bahwa alternatif yang terpilih adalah:").font = font_bold
    current_row += 1
    
    ws.cell(row=current_row, column=1, value="Rangking").font = font_bold
    ws.cell(row=current_row, column=2, value="Nilai Skor").font = font_bold
    ws.cell(row=current_row, column=3, value="Alternatif").font = font_bold
    apply_style(current_row, 1, current_row, 3, fill=fill_yellow, bold=True)
    
    # Isi urutan ranking 1 sampai n_a menggunakan rumus INDEX/MATCH atau SORT
    for rank_idx in range(1, n_a + 1):
        r_now = current_row + rank_idx
        ws.cell(row=r_now, column=1, value=rank_idx)
        # Ambil nilai skor ke-rank_idx menggunakan LARGE
        ws.cell(row=r_now, column=2, value=f"=LARGE({rank_range}, {rank_idx})")
        # Ambil nama alternatif dengan INDEX MATCH
        val_ref = f"B{r_now}"
        ws.cell(row=r_now, column=3, value=f"=INDEX($A${start_calc_r+1}:$A${start_calc_r+n_a}, MATCH({val_ref}, {rank_range}, 0))")
    apply_style(current_row+1, 1, current_row+n_a, 3)

    # Format lebar kolom
    ws.column_dimensions['A'].width = 25
    for c in range(2, n_k + 8):
        ws.column_dimensions[get_column_letter(c)].width = 16
        
    import io
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
