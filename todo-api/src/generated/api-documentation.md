# API Documentation
## Endpoints
### Create Todo
* `POST /todos`
	+ Request Body: `title` (string)
	+ Response: `201 Created`
### List Todos
* `GET /todos`
	+ Response: `200 OK`
### Update Todo
* `PATCH /todos/{id}`
	+ Path Parameters: `id` (integer)
	+ Request Body: `completed` (boolean)
	+ Response: `200 OK`}