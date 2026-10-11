import numpy as np
import pandas as pd

def calculate_priority_vector(matrix):
    """
    Menghitung vektor prioritas (bobot) dari matriks perbandingan berpasangan.
    """
    # Menjumlahkan setiap kolom
    col_sum = matrix.sum(axis=0)
    # Normalisasi matriks (membagi setiap elemen dengan jumlah kolomnya)
    normalized_matrix = matrix / col_sum
    # Rata-rata dari setiap baris pada matriks yang dinormalisasi adalah vektor prioritas
    priority_vector = normalized_matrix.mean(axis=1)
    return priority_vector

def calculate_consistency_ratio(matrix, priority_vector):
    """
    Menghitung Consistency Ratio (CR).
    """
    n = matrix.shape[0]
    
    # Jika ukuran matriks kurang dari 3, secara matematis konsisten (CR = 0)
    if n < 3:
        return 0.0, True

    # Mengalikan matriks asli dengan vektor prioritas
    weighted_sum = np.dot(matrix, priority_vector)
    
    # Menghitung Lambda Max (eigenvalue terbesar)
    lambda_max = np.mean(weighted_sum / priority_vector)
    
    # Menghitung Consistency Index (CI)
    ci = (lambda_max - n) / (n - 1)
    
    # Random Index (RI) berdasarkan ukuran matriks (n)
    # Sumber: Saaty (1980)
    ri_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 
               6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    
    # Mengambil nilai RI, gunakan 1.49 jika n > 10
    ri = ri_dict.get(n, 1.49)
    
    # Menghitung Consistency Ratio (CR)
    cr = ci / ri
    
    # CR yang dapat diterima umumnya <= 0.1 (10%)
    is_consistent = cr <= 0.1
    
    return cr, is_consistent
