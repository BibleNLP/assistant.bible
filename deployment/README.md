## How to deploy

1. Log on to the server machine
	`ssh <username>@<ipaddress>`

2. Clone the repo
	`git clone https://github.com/BibleNLP/assistant.bible.git`

3. Environment Variables
	`cd assistant.bible/deployment`

	`touch .env`

	`nano .env` 

	Add the following environment variables with appropriate values for your deployment

	```
	OPENAI_API_KEY=<sk-..>
	WEBSOCKET_URL=ws://assistant.bible/chat
	DOMAIN=assistant.bible
	POSTGRES_DB_USER=adotbadmin
	POSTGRES_DB_PASSWORD=<a strong password>
	POSTGRES_DB_NAME=adotbcollection
	MAX_COSINE_DISTANCE=0.2

	SUPABASE_URL=<https://<your_supabase_instance>.supabase.co>
	SUPABASE_KEY=<from your account>
	SUPABASE_JWT_SECRET=<from your account>
	```

	These are the minimum set of values to be set. The full list is available in the main [README](../README.md)

4. Setup SSL cerificate
	Follow the instructions [here](https://mindsers.blog/en/post/https-using-nginx-certbot-docker/).

	The services "webserver"(nginx) and "certbot" are already inlcuded in our docker compose, those could be used to perform the steps in the article. Also the nginx configuration file is [here](./nginx/nginx.conf.template), which would need edits during the setting up process.

5. Start the app, with all services
	`docker compose --env-file .env up -d`

## How to update code and redeploy

```
ssh <user>@<ipaddress>
cd assistant.bible
git pull origin <branch-name>
cd deployment
docker compose --env-file .env up --build --force-recreate -d
```


## How to renew the SSL certificate

```
ssh <user>@<ipaddress>
cd assistant.bible/deployment
docker compose run certbot renew
docker compose --env-file .env down
docker compose --env-file .env up -d
```

## How to connect to server database

We use postgres database. On the DBMS app that you use on your computer like PgAdmin, DBeaver etc, give the connection configuration as you have set us the DB here

* host = assistant.bible, dev.assistant.bible,  the ip-address or the domain name you use for the deployment
* post = 5432, the default or the one you have given in ENV variable
* database name = what you have given in the ENV variable
* password = what you have given in the ENV variable

