import sqlite3 as sql
import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime

print("uygulama başlatılıyor")

def giris_yap():
    username = entry_username.get()
    password = entry_password.get()
    try:
        password = int(password)
    except ValueError:
        messagebox.showerror("Hata", "ŞİFRE SAYI OLMALI!")
        return
    try:
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE username = ? AND password = ?",(username, password))
        output= cursor.fetchone()
        conn.close()

        if output:
            balance = output[0]
            messagebox.showinfo("Giriş Başarılı", f"Hoş Geldin {username}")
            ana_ekran_ac(username, balance)
        else:
            messagebox.showerror("HATA", "Kullanıcı Adı ya da Şifre Yanlış")
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", str(e))



def ana_ekran_ac(username, balance):
    pencere = tk.Toplevel(root)
    pencere.title("Kullanıcı Ekranı")
    pencere.geometry("1000x1000")
    conn = sql.connect("accounts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    nakit = cursor.fetchone()[0]
    cursor.execute("SELECT hisse_kodu , adet FROM portfoy WHERE username = ?", (username,))
    portfoy_listesi = cursor.fetchall()
    conn.close()

    FINNHUB_API_KEY = "d1gofi1r01qkdlvpenngd1gofi1r01qkdlvpeno0"
    portfoy_degeri = 0
    for hisse_kodu, adet in portfoy_listesi:
        try:
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={hisse_kodu}&token={FINNHUB_API_KEY}"
            quote_response = requests.get(quote_url)
            quote_data = quote_response.json()
            fiyat = quote_data.get("c", 0)
            portfoy_degeri += fiyat * adet
        except:
            continue

    toplam_bakiye = nakit + portfoy_degeri

    tk.Label(pencere, text = f"Toplam Bakiye: {toplam_bakiye:,.2f} $", font=("Arial",30)).grid(column =0, row = 0, columnspan = 2, padx = 10, pady = 10)
    tk.Label(pencere, text = "HİSSE EKRANI", font = ("Arial", 25)).grid(column = 0 , row = 1, columnspan = 1, padx = 10, pady = 10, sticky = "we")
    tk.Button(pencere, text = "Hisse Ara", command = hisse_arama_display).grid(column = 4, row = 0, columnspan = 2, padx = 10, pady = 10)

    canvas_horizontal = tk.Canvas(pencere, bg = "black", width = 1, height = 2, highlightthickness = 0)
    canvas_horizontal.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = "we")

    canvas = tk.Canvas(pencere, bg="black", width = 2, height = 2, highlightthickness=0)
    canvas.grid(row=0, column=3, rowspan=3, padx=10, pady=10, sticky="ns")

    tk.Button(pencere, text = "Hisse Al", command = lambda: hisse_satin_al_ekrani(username)).grid(column =4, row = 1, columnspan = 2, padx = 10, pady = 10)
    tk.Button(pencere, text = "Hisse Sat").grid(column = 4 , row = 2, columnspan = 2, padx = 10, pady = 10, sticky ="we")

    row_index = 4

    headers = ["Hisse", "Toplam Adet", "Ort. Maliyet ($)", "Güncel Fiyat ($)", "Toplam Değer ($)"]
    for col, header in enumerate(headers):
        tk.Label(pencere, text=header, font=("Arial", 12, "bold")).grid(row=row_index, column=col, padx=5, pady=5)

    row_index += 1

    for hisse_kodu in set(h[0] for h in portfoy_listesi):
        adetler = [h[1] for h in portfoy_listesi if h[0] == hisse_kodu]
        toplam_adet = sum(adetler)

        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT SUM(alim_fiyati), SUM(adet) FROM portfoy 
                          WHERE username = ? AND hisse_kodu = ?""", (username, hisse_kodu))
        toplam_alim_fiyati, toplam_adet_db = cursor.fetchone()
        conn.close()

        ort_maliyet = (toplam_alim_fiyati / toplam_adet_db) if toplam_adet_db else 0

        try:
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={hisse_kodu}&token={FINNHUB_API_KEY}"
            quote_response = requests.get(quote_url)
            fiyat = quote_response.json().get("c", 0)
        except:
            fiyat = 0

        toplam_deger = toplam_adet * fiyat

        row_values = [hisse_kodu, toplam_adet, f"{ort_maliyet:.2f}", f"{fiyat:.2f}", f"{toplam_deger:.2f}"]
        for col, val in enumerate(row_values):
            tk.Label(pencere, text=val, font=("Arial", 11)).grid(row=row_index, column=col, padx=5, pady=5)

        row_index += 1



def hisse_arama_display():
    hisse_arama = tk.Toplevel(root)
    hisse_arama.title("Hisse Arama")
    hisse_arama.geometry("300x300")
    tk.Label(hisse_arama, text = "Hisse Adı: ").grid(column = 0, row= 0, padx = 10, pady = 10)
    hisse_ad = tk.Entry(hisse_arama)
    hisse_ad.grid(column = 1, row = 0, padx = 10, pady = 10)
    result_label = tk.Label(hisse_arama, text=" ", font=("Arial", 16), fg="green")
    result_label.grid(column=0, row=2, columnspan=2, pady=10)

    tk.Button(hisse_arama, text = "Ara", command = lambda: hisse_arayici(hisse_ad, result_label)).grid(column = 0, row = 1, columnspan = 2, sticky = "we")



def hisse_arayici(hisse_ad, result_label):
    FINNHUB_API_KEY = "d1gofi1r01qkdlvpenngd1gofi1r01qkdlvpeno0"
    hisse_kodu = hisse_ad.get().upper()

    try:
        profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={hisse_kodu}&token={FINNHUB_API_KEY}"
        profile_response = requests.get(profile_url)
        profile_data = profile_response.json()
        name = profile_data.get("name", None)

        quote_url = f"https://finnhub.io/api/v1/quote?symbol={hisse_kodu}&token={FINNHUB_API_KEY}"
        quote_response = requests.get(quote_url)
        quote_data = quote_response.json()
        price = quote_data.get("c", None)

        if name and price:
            result_label.config(text=f"{hisse_kodu} → {name} | Fiyat: {price:.2f} USD", fg="green")
        else:
            result_label.config(text="Hisse veya fiyat bulunamadı.", fg="red")
    except Exception as e:
        result_label.config(text=f"Hata: {str(e)}", fg="red")



def hisse_satin_al_ekrani(username):
    hisse_alim_ekrani = tk.Toplevel()
    hisse_alim_ekrani.title("Hisse Alım Ekranı")
    hisse_alim_ekrani.geometry("500x500")
    alinmis_hisse = tk.Entry(hisse_alim_ekrani)
    tk.Label(hisse_alim_ekrani, text = "Hisse Adı:").grid(column = 0, row = 0, padx = 0, pady = 0, sticky = "e")
    alinmis_hisse.grid(column = 1, row = 0, padx = 10, pady = 10, sticky ="we")
    tk.Label(hisse_alim_ekrani, text = "Adet:").grid(column = 0 , row = 1, padx = 10, pady = 10, stick = "we")
    adet_entry = tk.Entry(hisse_alim_ekrani)
    adet_entry.grid(column = 1, row = 1, padx = 10, pady = 10, sticky ="we")

    tk.Button(hisse_alim_ekrani, text = "AL", command = lambda: al_sorgusu(username, alinmis_hisse.get(), adet_entry.get())).grid(column = 0, row = 3, columnspan = 3, padx = 10, pady = 10, sticky = "we")



def al_sorgusu(username, alinmis_hisse, adet_entry):
    try:
        adet = int(adet_entry)
    except ValueError:
        messagebox.showerror("Hata", "Adet Sayı Olmalı!")
        return

    try:
        FINNHUB_API_KEY = "d1gofi1r01qkdlvpenngd1gofi1r01qkdlvpeno0"
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={alinmis_hisse}&token={FINNHUB_API_KEY}"
        quote_response = requests.get(quote_url)
        quote_data = quote_response.json()
        price = quote_data.get("c", None)
        if price is None:
            messagebox.showerror("Hata", "Fiyat Bilgisi Bulunamadı!")
            return
        toplamfiyat = adet * price
        al_sorgusu_disp = tk.Toplevel()
        al_sorgusu_disp.title("Onay Ekranı")
        al_sorgusu_disp.geometry("300x100")
        tk.Label(al_sorgusu_disp, text = f"Toplam fiyat: {toplamfiyat:.2f}$ , onaylıyor musunuz?").grid(column = 0, columnspan = 2, row = 0, padx = 10, pady = 10, sticky = "we")
        tk.Button(al_sorgusu_disp, text = "Onay", command =lambda: hisse_al_onay(username, alinmis_hisse, adet, price, al_sorgusu_disp)).grid(column = 0, row = 1, padx = 10, pady = 10, sticky = "we")
        tk.Button(al_sorgusu_disp, text = "Ret").grid(column = 1, row = 1, padx = 10, pady = 10, sticky = "we")
    except Exception as e:
        messagebox.showerror("Hata", f"İşlem başarısız: {str(e)}")



def hisse_al_onay(username, hisse_kodu, adet, fiyat, pencere):
    try:
        toplamfiyat = adet* fiyat
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
        balance = cursor.fetchone()[0]
        
        if balance < toplamfiyat:
            messagebox.showerror("Hata", "Bakiye Yetersiz")
            conn.close()
            pencere.destroy()
            return
        
        yenibakiye = balance - toplamfiyat
        
        cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (yenibakiye, username))
        conn.commit()
        conn.close()

        conn2 = sql.connect("accounts.db")
        cursor2 = conn2.cursor()
        cursor2.execute("""CREATE TABLE IF NOT EXISTS portfoy(
                        username TEXT,
                        hisse_kodu TEXT,
                        adet INTEGER,
                        alim_fiyati REAL,
                        alim_tarihi TEXT)""")
        
        cursor2.execute("INSERT INTO portfoy VALUES(?,?,?,?,?)",(username, hisse_kodu, adet, toplamfiyat, datetime.now().strftime("%Y-%m-%d")))
        conn2.commit()
        conn2.close()
        messagebox.showinfo("Başarılı!","Alım Yapıldı!")
        pencere.destroy()
    except Exception as e:
        messagebox.showerror("Hata", f"Veritabanı Hatası: {str(e)}")
        pencere.destroy()



def hesap_olusturma_ekrani():
    yeni_hesap = tk.Toplevel()
    yeni_hesap.title("Hesap Oluşturma Ekranı")
    yeni_hesap.geometry("400x400")

    tk.Label(yeni_hesap, text = "Ad:").grid(column = 0, row = 0, padx = 10, pady = 10, sticky = "e")
    isim_girisi = tk.Entry(yeni_hesap)
    isim_girisi.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = "we")

    tk.Label(yeni_hesap, text = "Şifre:").grid(column = 0, row = 1, padx = 10, pady = 10, sticky = "e")
    sifre_girisi = tk.Entry(yeni_hesap)
    sifre_girisi.grid(column = 1 , row = 1, padx = 10, pady = 10, sticky = "we")

    tk.Button(yeni_hesap, text = "Oluştur", command = lambda: hesap_olustur(isim_girisi, sifre_girisi)).grid(column = 0 , row = 2 , columnspan = 2, padx = 10, pady = 10, sticky = "we")



def hesap_olustur(isim_girisi, sifre_girisi):
        isimg = isim_girisi.get()
        try:
            sifreg = int(sifre_girisi.get())
        except ValueError:
            messagebox.showerror("Hata", "Şifre Sayı Olmalı!")
            return
        if not isimg or not sifreg:
            messagebox.showerror("Hata", "Boş Alan Bırakılamaz!")
            return
        try:
            conn=sql.connect("accounts.db")
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                            username TEXT PRIMARY KEY,
                            password INTEGER,
                            balance INTEGER)""")
            conn.commit()
            cursor.execute("INSERT INTO users(username, password, balance) VALUES (?,?,100000)", (isimg, sifreg,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Kayıt Tamamlandı", "Giriş Ekranına Dönerek Giriş yapabilirsin!")
        except sql.IntegrityError:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten var!")
        except Exception as e:
            messagebox.showerror("Veritabanı Hatası", str(e))
def veritabani_kurulum():
    conn = sql.connect("accounts.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password INTEGER,
            balance INTEGER)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfoy(
            username TEXT,
            hisse_kodu TEXT,
            adet INTEGER,
            alim_fiyati REAL,
            alim_tarihi TEXT)
    """)

    conn.commit()
    conn.close()



veritabani_kurulum()

root = tk.Tk()
root.title("Borsa Simülasyonu")
root.geometry("1000x1000")

tk.Label(root, text = "Kullanıcı Adı").grid(column = 0, row = 0, padx = 10, pady = 5, sticky = "e")
entry_username = tk.Entry(root)
entry_username.grid(column = 1, row= 0, padx = 10, pady= 5, sticky = "e" )

tk.Label(root, text = "Şifre",).grid(column = 0, row = 1, padx = 10, pady = 5)
entry_password = tk.Entry(root, show = "*")
entry_password.grid(column = 1, row = 1, padx = 10, pady = 5, sticky = "e")

tk.Button(root, text = "Giriş", command = giris_yap).grid(row = 2, column = 0, columnspan =2, padx = 10, pady = 10, sticky = "we")
tk.Button(root, text = "Hesap Oluştur", fg = "blue", command = hesap_olusturma_ekrani).grid(row = 3, column = 0, columnspan = 2, padx = 5, pady = 2,)


if __name__ == "__main__":
    root.mainloop()
