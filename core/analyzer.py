import json
import sqlite3
import requests
from fuzzywuzzy import process


def analyze(description):
    mark = 0
    try:
        sqlite_connection = sqlite3.connect('core/db/compound_meals.db')
        cursor = sqlite_connection.cursor()
        cursor.execute("SELECT * FROM meals")
        result = cursor.fetchall()
        meals_str = [" ".join(meal[1].split(" ")[0:2]) for meal in result]
        cursor.close()
        lst = description.split(',')
        for j in range(len(lst)):
            if "арома" in lst[j]:
                continue
            meal = process.extractOne(lst[j].replace("натуральный", ""), meals_str)[0]
            i = meals_str.index(meal)
            print(result[i][1])
            print(result[i][3])
            print(result[i][4])
            mark += ((float(result[i][3].replace("%", "")) + float(result[i][4].replace("%", ""))) / 2 / (j + 1))
        print("Степень полезности продукта:")
        print(mark)
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    except Exception as _ex:
        print(_ex)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

    return mark


def analyze_by_barcode(barcode):
    res = requests.get(f'https://m4pbaszg93.execute-api.us-east-2.amazonaws.com/dev/api/v1/products/{barcode}')
    if res.status_code == 404:
        return
    product = json.loads(res.text)

    print(product["title"])
    print(product["description"])
    product["mark"] = analyze(product["description"])
    return product


