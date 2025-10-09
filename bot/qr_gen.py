import qrcode
from io import BytesIO
from config import PayeeINN, PersonalAcc, CorrespAcc
import re
# Данные фирмы

def create_qr(price_from_solver: int):
    firm = {
        "urname": "Горбенко Станислав Игоревич",
        "rs": PersonalAcc,   # расчётный счёт
        "bank": "Т-Банк",
        "bik": "044525974",
        "ks": CorrespAcc,  # корр. счёт
        "inn": PayeeINN,
        "kpp": "771301001"
    }

    purpose = "Оплата заказа "
    service_id = 1

    # Формируем строку QR
    qr_str = (
        f"ST00012|Name={firm['urname']}"
        f"|PersonalAcc={firm['rs']}|BankName={firm['bank']}"
        f"|BIC={firm['bik']}|CorrespAcc={firm['ks']}"
        f"|PayeeINN={firm['inn']}"
        f"|Sum={price_from_solver}|Purpose={purpose}|Contract={service_id}"
    )

    # Генерация QR-кода
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(qr_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# Показать прямо в Jupyter
def parse_amount_to_kopecks(text: str) -> int | None:
    """
    Принимает строки вида "1000", "1 000", "1000.50", "1000,50"
    Возвращает целое количество копеек (int) или None при ошибке.
    """
    if not text:
        return None
    # удалить пробелы
    s = text.strip().replace(" ", "")
    # заменить запятую на точку
    s = s.replace(",", ".")
    # разрешим только цифры и одна точка
    if not re.match(r'^\d+(\.\d{1,2})?$', s):
        return None
    # перевести в копейки
    if "." in s:
        rub, kop = s.split(".")
        kop = (kop + "00")[:2]  # дополним до 2 знаков
    else:
        rub = s
        kop = "00"
    try:
        total = int(rub) * 100 + int(kop)
        return total
    except Exception:
        return None