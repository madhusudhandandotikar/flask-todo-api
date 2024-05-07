from flask import Flask
# from flask_smorest import Api, Blueprint, datetime, timezone, MethodView
from flask_smorest import Api, Blueprint
from datetime import datetime, timezone
# from flask.views import MethodView
from flask.views import MethodView
import uuid
from marshmallow import Schema, fields
from enum import Enum
from flask import abort




server = Flask(__name__)

# @server.route("/hello")
# def hello():
#     return "hello"

class APIConfig:
    API_TITLE = "TODO API"
    API_VERSION = "v1"
    OPENAPI_VERSION="3.0.3"
    OPENAPI_URL_PREFIX ="/"
    OPENAPI_SWGGER_UI_PATH ="/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_UI_URL = "https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.75/bundles/redoc.standalone.js"

server.config.from_object(APIConfig)



api = Api(server)

todo = Blueprint("todo", "todo", url_prefix="/todo", description="TODO API")

tasks = [
    {
        "id": uuid.UUID("d4a75bbb-ffc4-4b48-98c0-efeeb63c309d"),
        "created" : datetime.now(timezone.utc),
        "completed" : False,
        "task" : "Created Flask API",
    }
]

class CreateTask(Schema):
    task = fields.String()

class Task(Schema):
    id = fields.UUID()
    created = fields.DateTime()
    



class UpdateTask(CreateTask):
    completed = fields.Bool()
    created = fields.DateTime()


class Task (UpdateTask):
    id = fields.UUID()
    created = fields.DateTime()

class ListTasks(Schema):
    tasks = fields.List(fields.Nested(Task))


class SortByEnum(Enum):
    task = "task"
    created = "created"

class SortDirectionEnum(Enum):
    asc = "asc"
    desc = "desc"



class ListTaskParameters(Schema):
    order_by = fields.Enum(SortByEnum, load_default=SortByEnum.created)
    order = fields.Enum(SortDirectionEnum, load_default=SortDirectionEnum.asc)





@todo.route("/tasks")

class TodoCollection(MethodView):

    @todo.arguments(ListTaskParameters, location="query")

    @todo.response(status_code=200, schema=ListTasks)
    def get (self, parameters):
         return {
             "tasks":sorted(
                 tasks,
                 key=lambda task: task[parameters["order_by"].value],
                 reverse=parameters["order"] == SortDirectionEnum.desc,

             )
         }
    
    @todo.arguments(CreateTask)
    @todo.response(status_code=201, schema=Task)
    def post(self, task):
        task["id"] = uuid.uuid4()
        task["created"] = datetime.now(timezone.utc)
        task["completed"] = False
        tasks.append(task)
        return task
    

# @todo.route("/tasks/<uuid:task_id>")

# class TodoTask(MethodView): 

#     @todo.response(status_code=200, schema=Task)
#     def get (self, task_id):
#         for task in tasks:
#             if task["id"] == task_id:
#                 return task
            
#     abort(404, f"Task with {task_id} not found.")
    

#     @todo.arguments(UpdateTask)
#     @todo.response(status_code=200, Schema=Task)
#     def put (self, task_id, payload):
#         for task in tasks:
#             if task["id"]  == task_id:
#                 task["completed"] == payload["completed"]
#                 task["task"] = payload["task"]
#                 return task
#     abort(404, f"Task with {{task_id}} not found.")
    
    
#     @todo.response(status_code=204)
#     def delete (self, task_id):
#         for index, task in enumerate(tasks):
#             if task["id"] == task_id:
#                 tasks.pop(index)
#                 return 
#     abort(404, f"Task with {{task_id}} not found.")

@todo.route("/tasks/<uuid:task_id>")
class TodoTask(MethodView): 

    @todo.response(status_code=200, schema=Task)
    def get(self, task_id):
        for task in tasks:
            if task["id"] == task_id:
                return task
        abort(404, f"Task with {task_id} not found.")

    @todo.arguments(UpdateTask)
    @todo.response(status_code=200, schema=Task)
    def put(self, task_id, payload):
        for task in tasks:
            if task["id"] == task_id:
                task["completed"] = payload["completed"]
                task["task"] = payload["task"]
                return task
        abort(404, f"Task with {task_id} not found.")

    @todo.response(status_code=204)
    def delete(self, task_id):
        for index, task in enumerate(tasks):
            if task["id"] == task_id:
                tasks.pop(index)
                return 
        abort(404, f"Task with {task_id} not found.")



api.register_blueprint(todo)
