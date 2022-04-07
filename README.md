# dqf

A dirt-simple Dynamic Quality Framework (DQF) server program. Allows uploading batches as TSV files and creates unique keys tied to those batches.

Built with Flask, SQLite, and React.

## Setup

Install the requirements:

```
$ sudo apt install python3 python3-pip sqlite3
$ pip install -r requirements.txt
```

Build the JavaScript file (I use [esbuild](https://esbuild.github.io/), but other builders such as Webpack would also work):

```
$ cd frontend
$ npm install
$ npx esbuild --bundle src/qa.jsx > ../static/qa.js
$ cd ..
```

Initialize the database:

```
$ sqlite3 dqf.db
sqlite> .read schema.sql
```

Run the flask server:

```
$ flask run -p 3000
```
