# Power2Go Backend Test

This project was developed using Python with Django and GraphQL. 

# Running the project

To start the project, run the following command:

```
python manage.py runserver 
```

You can also run the project using ngrok to expose the application to the network:

```
ngrok http http://localhost:8000  
```

To run the queries, pay attention to the correctly declarations, fields and data you want. For example, here's a sample of a query:

```
query getUser($id: ID!) {
	getUser(id: $id) {
		id
		name
		email
	}
}
```

