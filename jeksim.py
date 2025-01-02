import requests
import time
import os

def color_text(text, color):
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m"  # Untuk mengembalikan warna ke default
    }
    return f"{colors[color]}{text}{colors['reset']}"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_title():
    print(color_text("==========================================", "green"))
    print(color_text("----------- GUNDAR PROJECT -----------", "green"))
    print(color_text("owner: @apengjers", "green"))
    print(color_text("==========================================", "green"))

def get_api_key():
    api_key_file = "apivirtu.txt"

    if os.path.exists(api_key_file):
        with open(api_key_file, "r") as file:
            api_key = file.read().strip()
    else:
        api_key = input(color_text("Masukkan API Key Anda: ", "green")).strip()
        with open(api_key_file, "w") as file:
            file.write(api_key)
        print(color_text("API Key disimpan dalam file.", "green"))

    return api_key

def create_order(api_key, service_id, operator):
    quantity = int(input(color_text("Masukkan jumlah nomor yang ingin dipesan: ", "green")))

    if quantity <= 0:
        print(color_text("Jumlah order harus berupa angka positif.", "red"))
        return

    success_numbers = []

    for _ in range(quantity):
        url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=order&service={service_id}&operator={operator}"
        response = requests.get(url)

        if response.status_code != 200:
            print(color_text(f"Error: {response.text}", "red"))
            continue

        result = response.json()
        if result.get("status"):
            success_numbers.append(result["data"].get("number"))
        else:
            print(color_text(f"Order Gagal: {result['data'].get('msg')}", "red"))

    if success_numbers:
        print(color_text("Order Berhasil:", "green"))
        for number in success_numbers:
            print(color_text(number, "green"))

def get_active_orders(api_key):
    url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=active_order"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(color_text("Gagal mengambil data order aktif.", "red"))
        return []

    result = response.json()
    if result.get("status") and result.get("data"):
        return result["data"]
    else:
        print(color_text("Orderan kosong bro", "red"))
        return []

def resend_order(api_key, order_id):
    """
    Fungsi untuk mengirim ulang order berdasarkan ID order.
    """
    url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=set_status&id={order_id}&status=3"
    response = requests.get(url)
    result = response.json()

    if result.get("status"):
        print(color_text(f"Order {order_id} berhasil diresend.", "green"))
    else:
        print(color_text(f"Gagal resend order {order_id}: {result['data'].get('msg')}", "red"))


def monitor_sms(api_key, interval=5, resend_interval=120):
    """
    Memantau SMS terbaru dan melakukan resend pada order yang sudah menerima SMS setiap 2 menit.
    """
    print(color_text("Memulai pemantauan SMS terbaru...", "green"))
    latest_sms = []
    number_index = {}
    last_resend_time = time.time()

    while True:
        # Ambil order aktif
        orders = get_active_orders(api_key)

        if orders:
            for order in orders:
                # Periksa jika order sudah menerima SMS
                if order.get("status") == "Otp Diterima" and order.get("sms"):
                    # Tampilkan detail SMS baru
                    sms_data = {
                        "number": order.get("number"),
                        "otp": order.get("otp"),
                        "sms": order.get("sms"),
                        "service_name": order.get("service_name")
                    }

                    if sms_data["number"] not in number_index:
                        number_index[sms_data["number"]] = len(number_index) + 1

                    sms_data["order_number"] = number_index[sms_data["number"]]

                    if sms_data not in latest_sms:
                        latest_sms.append(sms_data)
                        latest_sms.sort(key=lambda x: x["order_number"])

                        print(color_text("SMS Baru Diterima:", "green"))
                        print(color_text(f"Nomor Urut: {sms_data['order_number']}", "cyan"))
                        print(color_text(f"Nomor: {sms_data['number']}", "cyan"))
                        print(color_text(f"OTP: {sms_data['otp']}", "green"))
                        print(color_text(f"Service: {sms_data['service_name']}", "green"))
                        print(color_text("------------------------------------", "green"))

                    # Resend order jika waktu resend terpenuhi
                    if time.time() - last_resend_time >= resend_interval:
                        resend_order(api_key, order["id"])

            # Perbarui waktu terakhir melakukan resend
            if time.time() - last_resend_time >= resend_interval:
                last_resend_time = time.time()

        else:
            print(color_text("Tidak ada SMS baru. Memeriksa lagi...", "red"))
            number_index.clear()

        time.sleep(interval)



def cancel_or_resend_order(api_key):
    orders = get_active_orders(api_key)

    if orders:
        print(color_text("Daftar Order Aktif:", "green"))
        for idx, order in enumerate(orders, 1):
            print(color_text(f"{idx}. ID: {order['id']} | Nomor: {order['number']}", "green"))

        choice = input(color_text("Masukkan nomor order untuk Kelola (format: <nomor>): ", "green"))
        action = input(color_text("Ketik 'batal' untuk membatalkan atau 'resend' untuk mengirim ulang: ", "green")).lower()

        try:
            order_idx = int(choice) - 1
            order_id = orders[order_idx]["id"]

            if action == "1":
                url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=set_status&id={order_id}&status=2"
                response = requests.get(url)
                result = response.json()
                if result.get("status"):
                    print(color_text(f"Order {order_id} berhasil dibatalkan.", "green"))
                else:
                    print(color_text(f"Gagal membatalkan order: {result['data'].get('msg')}", "red"))

            elif action == "2":
                url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=set_status&id={order_id}&status=3"
                response = requests.get(url)
                result = response.json()
                if result.get("status"):
                    print(color_text(f"Order {order_id} berhasil diresend.", "green"))
                else:
                    print(color_text(f"Gagal resend order: {result['data'].get('msg')}", "red"))
            else:
                print(color_text("Aksi tidak dikenali.", "red"))

        except (IndexError, ValueError):
            print(color_text("Pilihan tidak valid.", "red"))

def main_menu(api_key, service_id, operator):
    while True:
        # Tampilkan judul saat program dimulai
        clear_screen()
        display_title()
        print(color_text("\nMenu Utama:", "green"))
        print(color_text("1. Pesan Nomor Baru", "green"))
        print(color_text("2. Cek Order Aktif", "green"))
        print(color_text("3. Kelola Order", "green"))
        print(color_text("4. Monitoring SMS Masuk", "green"))
        print(color_text("5. Keluar", "green"))

        choice = input(color_text("Pilih opsi (1-5): ", "green"))

        if choice == "1":
            create_order(api_key, service_id, operator)
            backmenu = input(color_text("Ingin kembali ke menu ? (y/n) : ", "green"))
            if backmenu == "y":
                continue
            else:
                break
        elif choice == "2":
            orders = get_active_orders(api_key)
            for order in orders:
                print(color_text(f"ID: {order['id']} | Nomor: {order['number']} | Status: {order['status']}", "green"))
            backmenu = input(color_text("Ingin kembali ke menu ? (y/n) : ", "green"))
            if backmenu == "y":
                continue
            else:
                break
        elif choice == "3":
            cancel_or_resend_order(api_key)
            backmenu = input(color_text("Ingin kembali ke menu ? (y/n) : ", "green"))
            if backmenu == "y":
                continue
            else:
                break
        elif choice == "4":
            monitor_sms(api_key)
        elif choice == "5":
            print(color_text("cabut lu ngent*.", "yellow"))
            break
        else:
            print(color_text("Pilihan tidak valid. Harap pilih antara 1-5.", "red"))

# Ambil API Key
default_service_id = "305"
default_operator = "any"
api_key = get_api_key()

# Jalankan menu utama
main_menu(api_key, default_service_id, default_operator)
