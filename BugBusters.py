import csv
import socket
from datetime import datetime, timedelta, date

HOST = '10.41.80.57'
PORT = 65504    

def gun_farki(tarih1, tarih2):
    try:
        tarih1_obj = datetime.strptime(tarih1, "%Y-%m-%d")
        tarih2_obj = datetime.strptime(tarih2, "%Y-%m-%d")
        fark = abs((tarih2_obj - tarih1_obj).days)
        return fark
    except ValueError:
        return "Geçerli bir tarih formatı kullanın (örn. 'YYYY-AA-GG')."

def send_request(command, host=HOST, port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))
        data = s.recv(1024)
        return data.decode('utf-8')

def servis2(city, hotel, rez_date, holiday_date, nights, room_type, room_number, total_price, last_7, last_3):
    command = f"get_hotel_details, {city}, {hotel}"
    response = send_request(command)
    data = response.split(",")

    listem1 = rez_date.split("-")
    listem2 = holiday_date.split("-")
    baslangic_tarihi = date(int(listem1[0]), int(listem1[1]), int(listem1[2]))  # Başlangıç tarihi
    bitis_tarihi = date(int(listem2[0]), int(listem2[1]), int(listem2[2]))  # Bitiş tarihi
    gunluk_fark = bitis_tarihi - baslangic_tarihi

    money_list = []
    sayac = 0
    for gun in range(gunluk_fark.days):
        gun_tarihi = baslangic_tarihi + timedelta(days=gun)
        sayac += 1
        if sayac <= 13:
            command = f"get_room_price, {data[1]}, {room_type}, {holiday_date}, {str(gun_tarihi)}"
            response = send_request(command)
            money_list.append((int(response) * int(nights) * int(room_number)))
        elif 13 < sayac <= gunluk_fark.days - 7:
            money_list.append(1000000)
        else:
            if (bitis_tarihi - gun_tarihi).days <= 2:
                money_list.append((int(response) * int(nights) * int(room_number)) + int(total_price) * float(last_3))
            elif 2 <= (bitis_tarihi - gun_tarihi).days <= 7:
                money_list.append((int(response) * int(nights) * int(room_number)) + int(total_price) * float(last_7))

    del money_list[0]
    min_fiyat = min(money_list)
    return (min_fiyat, str(baslangic_tarihi + timedelta(days=money_list.index(min_fiyat)+1)))

def csv_to_dict(csv_file, encoding='utf-8'):
    data = []
    with open(csv_file, mode='r', encoding=encoding) as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

csv_file = "reservations.csv"
data_dict = csv_to_dict(csv_file, encoding='utf-8')
sayac = 0

with open("new_reservations2.csv", "w", encoding='utf-8') as dosya3:
    print('date_reservation, date_accommodation_begin, nights7, city, hotel_name, room_type, number_of_rooms, total_price, cancellation7, cancellation2', file=dosya3)
    for i in data_dict:
        sayac += 1
        ucuz = servis2(i[' city'], i[' hotel_name'], i['date_reservation'], i[' date_accommodation_begin'],
                         i[' nights'], i[' room_type'], i[' number_of_rooms'], i[' total_price'], i[' cancellation7'],
                         i[' cancellation2'])

        if ucuz[0] < int(i[' total_price']):
            print(
                f"{ucuz[1]}, {i[' date_accommodation_begin']}, {i[' nights']}, {i[' city']}, {i[' hotel_name']}, {i[' room_type']}, {i[' number_of_rooms']}, {ucuz[0]}, {i[' cancellation7']}, {i[' cancellation2']}",
                file=dosya3)
        else:
            print(
                f"{i['date_reservation']}, {i[' date_accommodation_begin']}, {i[' nights']}, {i[' city']}, {i[' hotel_name']}, {i[' room_type']}, {i[' number_of_rooms']}, {i[' total_price']}, {i[' cancellation7']}, {i[' cancellation2']}",
                file=dosya3)
        if sayac == 4001:
            break
