""" Скрипт создания (заполнение) базы данных """

from db import create_schema

if __name__ == "__main__":
	create_schema(fill=True)