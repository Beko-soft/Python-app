import sys
import os
import time
from rembg import remove
from PIL import Image
import io

# Model Adı ve Modeli bellekte tutmak için dışarıda bir session objesi tutma
BGTX_MODEL_NAME = "u2net"
# rembg, session_name ile modelin tekrar yüklenmesini engeller.
global BGTX_SESSION
BGTX_SESSION = None


def initialize_bgtx_model():
    """AI modelinin yüklü olup olmadığını kontrol eder ve yükler."""
    global BGTX_SESSION
    print("--- [BGTX ENGINE BAŞLATILIYOR] ---")
    print(f"1. Kontrol: '{BGTX_MODEL_NAME}' AI Modeli Kontrol Ediliyor...")

    try:
        # Session nesnesini rembg'den alıyoruz. Bu nesne bellek içi cache'i yönetir.
        from rembg import new_session
        BGTX_SESSION = new_session(BGTX_MODEL_NAME)

        # Bu noktada model yüklenmiş veya cache'lenmiş olacaktır.
        print("1. BAŞARILI: Model yüklendi ve hazır.")
        print("   -> BGTX, bu session sayesinde modeli yeniden yüklemeyecektir.")

    except Exception as e:
        print("1. KRİTİK HATA: AI Modeli yüklenirken sorun çıktı!")
        print(f"   -> Hata Detayı: {e}")
        sys.exit(1)


def process_image(input_path):
    """Tek bir resmin arka planını kaldırır ve sonucun dosya yolunu döndürür."""
    global BGTX_SESSION

    try:
        # 3.1. Giriş dosyasını bayt (binary) formatında oku
        with open(input_path, "rb") as f:
            input_data = f.read()

        # 3.2. Arka plan kaldırma Engine'ini çağır (session objesini kullanıyoruz!)
        # Engine, modelin zaten BGTX_SESSION içinde olduğunu bilecek.
        output_data = remove(input_data, session=BGTX_SESSION)

        # 3.3. Sonucu bir PIL Image objesine çevir
        output_image = Image.open(io.BytesIO(output_data))

        # 4. Çıktı Yolu Oluştur ve Kaydet
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_bgtx.png"
        output_image.save(output_path, "PNG")

        return {"status": "success", "input": os.path.basename(input_path), "output_path": output_path}

    except Exception as e:
        return {"status": "error", "input": os.path.basename(input_path), "message": str(e)}


def batch_process_images(image_paths):
    """Verilen tüm resim yollarını sırayla işler ve toplu rapor döndürür."""

    total_files = len(image_paths)
    print(f"\n3. İşlem: Toplam {total_files} adet resim için BGTX Çekirdeği çalıştırılıyor...")
    proc_start_time = time.time()
    results = []

    for i, path in enumerate(image_paths):
        print(f"   -> [{i + 1}/{total_files}] İşleniyor: {os.path.basename(path)}")
        result = process_image(path)
        results.append(result)

    proc_elapsed_time = time.time() - proc_start_time

    # --- 4. Nihai Çıktı Raporu ---
    print("-" * 35)
    print("4. BGTX TOPLU SONUÇ RAPORU:")
    print(f"   -> Toplam İşlenen Dosya: {total_files}")
    print(f"   -> Toplam İşlem Süresi: {proc_elapsed_time:.2f} saniye")

    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = total_files - success_count
    print(f"   -> BAŞARILI: {success_count} adet, HATALI: {error_count} adet.")

    if error_count > 0:
        print("\n[Hata Detayları]:")
        for r in results:
            if r['status'] == 'error':
                print(f"   - HATA ({r['input']}): {r['message']}")

    print("-" * 35)
    return results


# --- ANA ÇALIŞMA ALANI ---
if __name__ == "__main__":
    initialize_bgtx_model()

    # Kullanıcıdan birden fazla dosya yolunu alıyoruz (Ayırıcı: virgül)
    while True:
        input_line = input(
            "\nLütfen işlenecek resimlerin TAM YOLLARINI aralarına VİRGÜL (,) koyarak girin (Örn: /yol/resim1.png,/yol/resim2.jpg): "
        ).strip()

        # Girişi virgülle ayırıp boşlukları temizliyoruz
        paths = [p.strip() for p in input_line.split(',') if p.strip()]

        # Tüm yolların geçerli olduğunu kontrol et
        valid_paths = [p for p in paths if os.path.exists(p)]

        if not paths:
            print("HATA: Hiç dosya yolu girmediniz.")
        elif len(valid_paths) != len(paths):
            invalid_paths = [p for p in paths if not os.path.exists(p)]
            print(f"HATA: Aşağıdaki yollar GEÇERSİZ veya BULUNAMADI: {', '.join(invalid_paths)}")
        else:
            break

    # Toplu işlemi başlat
    batch_process_images(paths)
