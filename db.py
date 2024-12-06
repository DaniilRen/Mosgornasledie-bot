from dotenv import load_dotenv
import os
import json
from peewee import *
import datetime

load_dotenv()
DB_PATH = os.getenv('DB_PATH')
db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
	class Meta:
		database = db


class Project(BaseModel):
	id = AutoField()  # Auto-incrementing primary key.
	name = CharField(unique=True)
	desc = CharField()
	date = CharField(max_length=300)
	url = CharField()
	photo = CharField()
	created_date = DateTimeField(default=datetime.datetime.now)

	class Meta:
			table_name = 'projects'


def create_schema() -> None:
	db.create_tables([Project])


def fill_db() -> None:
	PROJECTS_DATA = os.getenv("PROJECTS_DATA")
	with open(PROJECTS_DATA, encoding='utf-8') as f:
		projects_arr = json.load(f)
		for pr in projects_arr:
			resp = add_project(**pr)
			print(resp)


def add_project(**project_data) -> dict:
	error = None
	name = project_data["name"]
	try:
		photo_path = os.path.join("assets", project_data["photo"])
		project = Project(name=name, desc=project_data["desc"], date=project_data["date"],
			url=project_data["url"], photo=photo_path)
		project.save()
	except Exception as e:
			error = e
	if not error is None:
		return {f'Error while adding {name}': error}
	return {f'adding {name}': 'success'}


def get_all_projects():
	return Project.select().order_by(Project.created_date.desc())


def get_project_by_id(pid: int):
	return Project.select().where(Project.id==pid)[0]