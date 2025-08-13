import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

DB = "crm.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS eggs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subscription TEXT NOT NULL,
            egg_type TEXT NOT NULL,
            box_size INTEGER NOT NULL DEFAULT 30,
            quantity INTEGER NOT NULL DEFAULT 1,
            delivery_day TEXT NOT NULL,
            delivery_time TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def yumurta_ekle(name, price):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO eggs (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

def uye_ekle(name, subscription, egg_type, box_size, quantity, delivery_day, delivery_time, phone):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''INSERT INTO members 
        (name, subscription, egg_type, box_size, quantity, delivery_day, delivery_time, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
        (name, subscription, egg_type, box_size, quantity, delivery_day, delivery_time, phone))
    conn.commit()
    conn.close()

def yumurtalari_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM eggs")
    eggs = c.fetchall()
    conn.close()
    return eggs

def uyeleri_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM members")
    members = c.fetchall()
    conn.close()
    return members

def uye_guncelle(id, name, subscription, egg_type, box_size, quantity, delivery_day, delivery_time, phone):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        UPDATE members 
        SET name=?, subscription=?, egg_type=?, box_size=?, quantity=?, delivery_day=?, delivery_time=?, phone=? 
        WHERE id=?
    ''', (name, subscription, egg_type, box_size, quantity, delivery_day, delivery_time, phone, id))
    conn.commit()
    conn.close()

def uye_sil(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    conn.close()

def yumurta_guncelle(id, name, price):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE eggs SET name=?, price=? WHERE id=?", (name, price, id))
    conn.commit()
    conn.close()

def yumurta_sil(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM eggs WHERE id=?", (id,))
    conn.commit()
    conn.close()

def bugunun_teslimatlari_getir():
    gun_map = {
        "Monday": "Pazartesi",
        "Tuesday": "Salı",
        "Wednesday": "Çarşamba",
        "Thursday": "Perşembe",
        "Friday": "Cuma",
        "Saturday": "Cumartesi",
        "Sunday": "Pazar"
    }
    today_eng = datetime.now().strftime("%A")
    today = gun_map[today_eng]
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT name, subscription, egg_type, box_size, quantity, delivery_time, delivery_day FROM members")
    deliveries = c.fetchall()
    conn.close()
    return deliveries


def aylik_kazanc_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT m.box_size, m.quantity, e.price, m.subscription
        FROM members m 
        JOIN eggs e ON m.egg_type = e.name
    """)
    data = c.fetchall()
    conn.close()

    kazanc = 0
    for box, qty, price, sub in data:
        toplam = box * qty * price  
        if sub == "Aylık":
            kazanc += toplam
        elif sub == "Haftalık":
            kazanc += toplam * 4  
    return kazanc



def gunluk_kazanc_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT m.box_size, m.quantity, e.price, m.subscription
        FROM members m JOIN eggs e ON m.egg_type = e.name
    """)
    data = c.fetchall()
    conn.close()

    kazanc = 0
    for box, qty, price, sub in data:
        if sub == "Haftalık":
            kazanc += (box * qty * price) / 7
        elif sub == "Aylık":
            kazanc += (box * qty * price) / 30
    return kazanc

init_db()
st.set_page_config(page_title="Gezen Tavuk Yumurtası CRM", layout="wide")
st.title("Gezen Tavuk Yumurtası Satış CRM")

menu = [
    "Ana Sayfa",
    "Üyelik Ekle",
    "Yumurta Türü Ekle",
    "Üyeler",
    "Yumurtalar",
    "Üye Sil/Düzenle",
    "Yumurta Sil/Düzenle"
]
choice = st.sidebar.selectbox("Sayfa Seç", menu)

if choice == "Ana Sayfa":
    st.header("Ana Sayfa")
    st.subheader("Bugünün Teslimatları")
    deliveries = bugunun_teslimatlari_getir()
    df = pd.DataFrame(deliveries, columns=[
        "İsim", "Abonelik", "Yumurta Türü", "Koli Boyu", "Koli Sayısı", "Teslimat Saati", "Teslimat Günü"
    ])
    st.dataframe(df)
    st.subheader("Aylık Kazanç")
    st.write(f"{aylik_kazanc_getir():.2f} TL")
    st.subheader("Günlük Kazanç")
    st.write(f"{gunluk_kazanc_getir():.2f} TL")
    st.subheader("Toplam Üye Sayısı")
    st.write(len(uyeleri_getir()))

elif choice == "Üyelik Ekle":
    st.header("Üyelik Ekle")
    eggs = yumurtalari_getir()
    with st.form("add_member_form"):
        name = st.text_input("Üye İsmi")
        subscription = st.selectbox("Abonelik Türü", ["Haftalık", "Aylık"])
        egg_type = st.selectbox("Yumurta Türü", [egg[1] for egg in eggs])
        box_size = st.selectbox("Koli Boyu", [15, 30])
        quantity = st.number_input("Kaç Koli?", min_value=1, step=1, value=1)
        delivery_day = st.selectbox("Teslimat Günü", ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        delivery_time = st.text_input("Teslimat Saati (örn: 07:45)")
        phone = st.text_input("Telefon Numarası")
        submitted = st.form_submit_button("Ekle")
        if submitted:
            uye_ekle(name, subscription, egg_type, box_size, quantity, delivery_day, delivery_time, phone)
            st.success("Üye eklendi.")

elif choice == "Yumurta Türü Ekle":
    st.header("Yumurta Türü Ekle")
    with st.form("add_egg_form"):
        name = st.text_input("Yumurta İsmi")
        price = st.number_input("Adet Fiyatı", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Ekle")
        if submitted:
            yumurta_ekle(name, price)
            st.success("Yumurta türü eklendi.")

elif choice == "Üyeler":
    st.header("Üyeler")
    members = uyeleri_getir()
    df = pd.DataFrame(members, columns=[
        "ID", "İsim", "Abonelik", "Yumurta Türü", "Koli Boyu", "Koli Sayısı", "Teslimat Günü", "Teslimat Saati", "Telefon"
    ])
    df = df.drop(columns=["ID"])
    st.dataframe(df)
   

elif choice == "Yumurtalar":
    st.header("Yumurtalar")
    eggs = yumurtalari_getir()
    df = pd.DataFrame(eggs, columns=["ID", "İsim", "Fiyat"])
    df = df.drop(columns=["ID"])
    st.dataframe(df)


elif choice == "Üye Sil/Düzenle":
    st.header("Üye Sil ve Düzenle")
    members = uyeleri_getir()
    eggs = yumurtalari_getir()
    egg_names = [egg[1] for egg in eggs]

    for member in members:
        with st.form(key=f"edit_member_{member[0]}"):
            name = st.text_input("İsim", member[1])
            subscription = st.selectbox(
                "Abonelik Türü",
                ["Haftalık", "Aylık"],
                index=0 if member[2] == "Haftalık" else 1
            )
            egg_type = st.selectbox(
                "Yumurta Türü",
                egg_names,
                index=egg_names.index(member[3]) if member[3] in egg_names else 0
            )
            box_size = st.selectbox(
                "Kutu Boyu",
                [15, 30],
                index=[15, 30].index(member[4]) if member[4] in [15, 30] else 0
            )
            quantity = st.number_input("Kutu Sayısı", min_value=1, value=member[5] or 1, step=1)
            delivery_days_list = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            delivery_day = st.selectbox(
                "Teslimat Günü",
                delivery_days_list,
                index=delivery_days_list.index(member[6]) if member[6] in delivery_days_list else 0
            )
            delivery_time = st.text_input("Teslimat Saati", member[7] or "07:00")
            phone = st.text_input("Telefon", member[8] or "")

            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("Kaydet")
            with col2:
                delete_btn = st.form_submit_button("Sil")

            if save_btn:
                if name and subscription and egg_type and delivery_day and delivery_time and phone:
                    uye_guncelle(member[0], name, subscription, egg_type, box_size, quantity, delivery_day, delivery_time, phone)
                    st.success("Üye güncellendi.")
                    st.rerun()
                else:
                    st.error("Lütfen tüm alanları doldurun.")

            if delete_btn:
                uye_sil(member[0])
                st.success("Üye silindi.")
                st.rerun()




elif choice == "Yumurta Sil/Düzenle":
    st.header("Yumurta Sil ve Düzenle")
    eggs = yumurtalari_getir()
    for egg in eggs:
        with st.form(key=f"form_{egg[0]}"):
            name = st.text_input("Yeni İsim", egg[1], key=f"name_{egg[0]}")
            price = st.number_input("Yeni Fiyat", value=egg[2], step=0.1, key=f"price_{egg[0]}")
            delete_button = st.form_submit_button("Sil")
            save_button = st.form_submit_button("Kaydet")
            if delete_button:
                yumurta_sil(egg[0])
                st.success("Yumurta silindi.")
                st.rerun()
            if save_button:
                yumurta_guncelle(egg[0], name, price)
                st.success("Yumurta güncellendi.")
                st.rerun()