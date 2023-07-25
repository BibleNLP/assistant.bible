# assistant.bible
The codebase for assistant.bible: A Bible assistant.

An intelligent search engine for domain specific data, that not only provides relevant links to resources but also synthesizes and summarizes results to provide a succinct and relevant answer through an interactive interface. It connects to LLMs and other AI models that are trained on the ground truth texts uploaded by the organization. This enables the software to provide highly accurate and relevant responses to user queries, based on the specific context of the organization's data. With the natural language chat interface, users can easily interact with the data and gain insights that would be difficult or time-consuming to obtain otherwise.

[Development Demo URL](#)

## Technologies
* Python 3.10
* FastAPI
* LangChain(?)
* OpenAI APIs
* ChromaDB
* Postgres(?)
* Supabase
* Docker


## Build and Run using Docker

1. `cd docker/`
1. `docker build -t assistant.bible .`
1. 
	```
	docker run \
		-v chroma-db-vol:../chromadb \
		-v ab-logs:../logs \
		-p 8000:8000 \
		-e OPENAI_API_KEY=<sk-...> \
		<imageid>
	```

Environment variables and their default values, 
* `OPENAI_API_KEY`
* `CHROMA_DB_PATH` default '../chormadb', if changing this should be changed in the volume also.
* `CHROMA_DB_COLLECTION` default 'adotbcollection'.
* `POSTGRES_DB_HOST=localhost`
* `POSTGRES_DB_PORT=5432`
* `POSTGRES_DB_NAME=adotbcollection`
* `POSTGRES_DB_USER=admin`
* `POSTGRES_DB_PASSWORD=secret`

If using default values, once started the app should be running at [http://localhost:8000](http://localhost:8000) and dev UI available at [http://localhost:8000/ui](http://localhost:8000/ui) and API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Start the app without docker

1. Create virtual environment
	```
	python3.10 -m venv <ENV>
	source <ENV>/bin/activate
	pip install -r requirements.txt
	```
1. Set Environment variables
	```
	OPENAI_API_KEY=sk-...
	CHROMA_DB_PATH=../chromadb
	CHROMA_DB_COLLECTION=adotbcollection
	```
	These values need to be set and saved in current terminal or in `.bashrc` file in home directory
1. Postgres DB
	Have postgres db running with pgvector extension enabled ([refer](https://github.com/pgvector/pgvector)). And provide the connection details as environment variables.
	```
	POSTGRES_DB_HOST=localhost
	POSTGRES_DB_PORT=5432
	POSTGRES_DB_NAME=adotbcollection
	POSTGRES_DB_USER=postgres
	POSTGRES_DB_PASSWORD=secret
	```
	If you dont want to mess with the locally running postgres version, running it as a docker container is a safer alternative: 
	`docker run -e POSTGRES_PASSWORD=admin -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=adotbcollection -p 5432:5432 ankane/pgvector`

1. Start the app
	```
	cd app
	uvicorn main:app --port 8000
	```
If successfully started, the app should be running at [http://localhost:8000](http://localhost:8000) and dev UI available at [http://localhost:8000/ui](http://localhost:8000/ui) and API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### Run tests

From `app/`, with virtual enviroment and Environment variables all set run

```
python -m pytest
```

### Run linting

After activating the virtual environment, from project root folder (`assistant.bible/`), run 

```
pylint --rcfile=.pylintrc app/*.py app/tests/*.py
```
