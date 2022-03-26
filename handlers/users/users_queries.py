from aiogram.dispatcher.filters import Command
from aiogram.types import Message
import pytesseract
from pyzbar.pyzbar import decode
from PIL import Image
import urllib.request

from config import BOT_TOKEN
from core.analyzer import analyze_by_barcode, analyze
from loader import dp

pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files (x86)\Tesseract-OCR\tesseract.exe"


@dp.message_handler(Command("start"))
async def show_start(message: Message):
    await message.answer(text="Добро пожаловать, гость!\nБот Compozer поможет Вам определить полезность товара."
                              "\nЗагрузите фото штрихкода продукта или фото состава продукта, а также вы можете ввести "
                              "номер штрихкода продукта или соcтав продукта вручную.")


@dp.message_handler(content_types=['photo'])
async def message_photo_handler(message: Message):
    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    urllib.request.urlretrieve(image_url, "file.jpeg")
    image = Image.open("file.jpeg")
    decoded = decode(image)
    if not decoded:
        string = pytesseract.image_to_string(image, lang="rus")  # распознование состава
        await message.reply(string)
        return
    product = analyze_by_barcode(decoded[0].data.decode('utf-8'))
    if product is None:
        await message.answer("К сожалению не удалось найти такого товара в базе, однако Вы можете прислать состав")
        return
    await message.reply(f"Оценка состава товара '{product['title']}': {product['mark']}%")


@dp.message_handler(content_types=['text'])
async def message_text_handler(message: Message):
    text_result = message.text
    if text_result.isdigit():
        await message.reply("Штрихкод получен")
        product = analyze_by_barcode(text_result)
        if product is None:
            await message.answer("К сожалению не удалось найти такого товара в базе, однако Вы можете прислать состав")
            return
        await message.answer(f"Оценка состава товара '{product['title']}': {product['mark']}%")
        return
    await message.reply("Состав получен")
    await message.answer(f"Оценка состава: {analyze(text_result.replace('Состав',''))}%")
