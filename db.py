from collections.abc import Callable
from dotenv import load_dotenv
import os
import json
from peewee import *
import datetime

load_dotenv()
DB_PATH = os.getenv('DB_PATH')
db = SqliteDatabase(DB_PATH)


""" Базовая таблица """
class BaseModel(Model):
	class Meta:
		database = db


""" Таблица проектов """
class Project(BaseModel):
	id = AutoField()  # Auto-incrementing primary key.
	name = CharField(unique=True)
	desc = CharField()
	photo = CharField()
	created_date = DateTimeField(default=datetime.datetime.now)

	class Meta:
		table_name = 'projects'

	def get_env_data_path() -> str:
		return 'PROJECT_DATA'

	def insert_data(**data) -> dict:
		error = None
		try:
			photo_path = os.path.join("assets", data["photo"])
			row = Project(name=data["name"],
												desc=data["desc"],
												photo=photo_path)
			row.save()
		except Exception as e:
				error = e
		if not error is None:
			return {"Status": "Error", "Error desc": error, "row": data['name']}
		else:
			return {"Status": "Success", "row": data['name']}


""" 
Таблица ссылок в подпунктах проекта 
Связывается с проектом по его id
"""
class Link(BaseModel):
	id = AutoField()  # Auto-incrementing primary key.
	project_id = ForeignKeyField(Project, backref='project_id')
	name = CharField()
	url = CharField()

	class Meta:
		table_name = 'links'
		
	def get_env_data_path() -> str:
		return 'LINK_DATA'
		
	def insert_data(**data) -> dict:
		error = None
		try:
			row = Link(url=data["url"], 
										project_id=data["project_id"],
										name=data["name"])
			row.save()
		except Exception as e:
				error = e
		if not error is None:
			return {"Status": "Error", "Error desc": error, "row": data['name']}
		else:
			return {"Status": "Success", "row": data['name']}


""" 
Таблица фотографий в подпунктах проекта 
Связывается с проектом по его id
"""
class Photo(BaseModel):
	id = AutoField()  # Auto-incrementing primary key.
	project_id = ForeignKeyField(Project, backref='project_id')
	name = CharField()
	text = CharField()
	position = IntegerField()

	class Meta:
		table_name = 'photos'
		
	def get_env_data_path() -> str:
		return 'PHOTO_DATA'

	def insert_data(**data) -> dict:
		error = None
		try:
			row = Photo(text=data["text"], 
										project_id=data["project_id"],
										position=data["position"],
										name=os.path.join("assets", data["name"]))
			row.save()
		except Exception as e:
				error = e
		if not error is None:
			return {"Status": "Error", "Error desc": error, "row": data['name']}
		else:
			return {"Status": "Success", "row": data['name']}


""" Создание таблиц """
def create_schema(fill: bool=False) -> None:
	print("< CREATING TABLES >")
	tables = [Project, Link, Photo]
	print(f"creating tables: {tables}")
	print("database file path:", DB_PATH)
	global db
	db.create_tables(tables)
	if fill:
		fill_tables(tables)


""" Заполнение всех таблиц данными """
def fill_tables(tables: list) -> None:
	errors = list()
	for table in tables:
		resp = insert_json_data(table)
		errors.extend(resp)

	print("< Inserted data to db ! >")
	print("< info: >")
	print(f"Insert errors: {len(errors)}")
	if len(errors) > 0:
		print("---")
		for i, err in enumerate(errors):
			print(f"{i}. {err}")
		print("---")
	print('cache_size:', db.cache_size)
	print('foreign_keys:', db.foreign_keys)
	print('journal_mode:', db.journal_mode)
	print('page_size:', db.page_size)


""" Заполнение таблицы данными из json"""
def insert_json_data(table) -> list:
	errors = list()
	data = os.getenv(table.get_env_data_path())
	with open(data, encoding='utf-8') as f:
		arr = json.load(f)
		for link in arr:
			resp = table.insert_data(**link)
			if resp["Status"] == "Error":
				errors.append(resp)
	return errors


""" Достает проект по id """
def get_project_by_id(id: int):
	return Project.select().where(Project.id==id)[0]


""" Достает все проекты в базе """
def get_all_projects():
	return Project.select().order_by(Project.created_date)


""" Достает все ссылки для конкретного проекта """
def get_project_links(project_id: int):
	return Link.select().where(Link.project_id==project_id)


""" Достает все фото для конкретного проекта """
def get_project_photos(project_id: int):
	return Photo.select().where(Photo.project_id==project_id)
