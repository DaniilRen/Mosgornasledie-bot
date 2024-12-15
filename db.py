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
	photo = CharField()
	created_date = DateTimeField(default=datetime.datetime.now)

	class Meta:
		table_name = 'projects'


class Link(BaseModel):
	id = AutoField()  # Auto-incrementing primary key.
	project_id = ForeignKeyField(Project, backref='project_id')
	name = CharField()
	url = CharField()

	class Meta:
		table_name = 'links'


def create_schema() -> None:
	db.create_tables([Project, Link])


def fill_db() -> None:
	errors = list()
	PROJECTS_DATA = os.getenv("PROJECTS_DATA")
	with open(PROJECTS_DATA, encoding='utf-8') as f:
		projects_arr = json.load(f)
		for project in projects_arr:
			resp = add_project(**project)
			if resp["Status"] == "Error":
				errors.append(resp)
	LINKS_DATA = os.getenv("LINKS_DATA")
	with open(LINKS_DATA, encoding='utf-8') as f:
		links_arr = json.load(f)
		for link in links_arr:
			resp = add_link(**link)
			if resp["Status"] == "Error":
				errors.append(resp)

	print("Inserted data to db !")
	print(f"Errors: {len(errors)}")
	if len(errors) != 0:
		for i, err in enumerate(errors):
			print(f"{i}. {err}")


def add_project(**project_data) -> dict:
	error = None
	try:
		photo_path = os.path.join("assets", project_data["photo"])
		project = Project(name=project_data["name"],
											desc=project_data["desc"],
											photo=photo_path)
		project.save()
	except Exception as e:
			error = e
	if not error is None:
		return {"Status": "Error", "Error desc": error, "row": project_data['name']}
	else:
		return {"Status": "Success", "row": project_data['name']}


def add_link(**link_data) -> dict:
	error = None
	try:
		link = Link(url=link_data["url"], 
									project_id=link_data["project_id"],
									name=link_data["name"])
		link.save()
	except Exception as e:
			error = e
	if not error is None:
		return {"Status": "Error", "Error desc": error, "row": link_data['name']}
	else:
		return {"Status": "Success", "row": link_data['name']}


def get_all_projects():
	return Project.select().order_by(Project.created_date)


def get_project_links(project_id: int):
	return Link.select().where(Link.project_id==project_id)


def get_project_by_id(id: int):
	return Project.select().where(Project.id==id)[0]