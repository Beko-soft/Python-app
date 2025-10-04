import sys
import os
import time # İşlem süresini ölçmek için
from rembg import remove
from PIL import Image
import io

# BGTX_MODEL_NAME'i rembg varsayılan modeli olarak bırakıyoruz. 
# rembg, modeli otomatik olarak indirir ve cache'ler.
BGTX_MODEL_NAME = "u2net"

def initialize_bgtx_model():
    """AI modelinin yüklü olup olmadığını kontrol eder ve yükler."""
    print("--- [BGTX ENGINE BAŞLATILIYOR] ---")
    print(f"1. Kontrol: '{BGTX_MODEL_NAME}' AI Modeli Kontrol Ediliyor...")
    
    start_time = time.time()
    try:
        # rembg.remove fonksiyonunu ilk kez çağırmak, modelin indirilmesini/yüklenmesini tetikler.
        # Bu işlem (model indirilmişse) çok hızlıdır. İlk çalıştırmada model indirilir ve cachelenir.
        temp_img = Image.new('RGB', (1, 1), color = 'red')
        temp_byte_arr = io.BytesIO()
        temp_img.save(temp_byte_arr, format='PNG')
        temp_data = temp_byte_arr.getvalue()
        
        # Modeli yüklemek için remove'u çağırıyoruz. model parametresi modelin adını belirtir.
        # Bu, modelin diske cache'lenmesini garanti eder.
        remove(temp_data, session_name=BGTX_MODEL_NAME, post_process_mask=True) 
        
        elapsed_time = time.time() - start_time
        print(f"1. BAŞARILI: Model yüklendi ve hazır. (Süre: {elapsed_time:.2f} sn)")
        print("   -> BGTX, artık bu model dosyasını her zaman çevrimdışı (offline) kullanacaktır.")
        
    except Exception as e:
        print("1. KRİTİK HATA: AI Modeli yüklenirken sorun çıktı!")
        print("   -> Hata notu: Bağlantı sorunu veya 'onnxruntime' gibi bağımlılıklar eksik olabilir.")
        print(f"   -> Hata Detayı: {e}")
        sys.exit(1) # Programı sonlandır

def process_and_save_image():
    """Kullanıcıdan dosya yolunu alır ve arka planı kaldırıp kaydeder."""
    
    # --- 2. Giriş Alma Aşaması ---
    while True:
        input_path = input("\nLütfen arka planı kaldırılacak resmin TAM YOLUNU girin (Örn: /home/kanka/resim.png): ").strip()
        
        if os.path.exists(input_path):
            break
        else:
            print(f"HATA: '{input_path}' yolu bulunamadı. Lütfen geçerli bir yol girin.")
    
    print("-" * 35)
    print(f"2. Giriş: İşlenecek dosya: {input_path}")
    
    # --- 3. İşlem Aşaması (BGTX Core) ---
    print("3. İşlem: BGTX Çekirdeği çalıştırılıyor...")
    proc_start_time = time.time()
    
    try:
        # 3.1. Giriş dosyasını bayt (binary) formatında oku
        with open(input_path, "rb") as f:
            input_data = f.read()
        print("3.1. OK: Resim dosyası belleğe yüklendi.")

        # 3.2. Arka plan kaldırma Engine'ini çağır (En yoğun kısım)
        output_data = remove(input_data, session_name=BGTX_MODEL_NAME)
        
        # 3.3. Sonucu bir PIL Image objesine çevir
        output_image = Image.open(io.BytesIO(output_data))
        print("3.2. OK: Arka plan kaldırma tamamlandı. Şeffaf imaj objesi oluşturuldu.")
        
        # --- 4. Çıktı Aşaması ---
        
        # Orijinal dosya adını ve uzantısını ayır
        base, ext = os.path.splitext(input_path)
        # Yeni dosya adı oluştur (Önemli: Çıktı her zaman PNG olmalı, çünkü PNG şeffaflığı destekler)
        output_path = f"{base}_bgtx.png" 

        # 4.1. Yeni dosyayı diske kaydet
        # Kayıt formatının PNG olması şeffaflığı korur.
        output_image.save(output_path, "PNG") 
        
        proc_elapsed_time = time.time() - proc_start_time
        print("-" * 35)
        print("4. BGTX BAŞARILI SONUÇ RAPORU:")
        print(f"   -> İşlenen Dosya: {os.path.basename(input_path)}")
        print(f"   -> Çıktı Dosyası: {output_path}")
        print(f"   -> Toplam İşlem Süresi: {proc_elapsed_time:.2f} saniye")
        print("   -> BGTX görevi tamamladı. Zeus ve Cektor'a GUI entegrasyonu kaldı!")
        
    except Exception as e:
        print("-" * 35)
        print("4. KRİTİK HATA: BGTX İşlemi sırasında beklenmedik bir sorun oluştu.")
        print(f"Hata Kodu: {e}")
        print("Lütfen dosya formatının ve içeriğinin geçerli olduğundan emin ol.")
        sys.exit(1)

# --- ANA ÇALIŞMA ALANI ---
if __name__ == "__main__":
    # Modelin hazır olduğundan emin ol (offline kullanımı garanti eder)
    initialize_bgtx_model() 
    
    # İşleme döngüsünü başlat
    process_and_save_image()
