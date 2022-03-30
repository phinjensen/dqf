# dqf

A dirt-simple Dynamic Quality Framework (DQF) server program. Allows uploading batches as TSV files and creates unique keys tied to those batches.

Built with Flask, SQLite, and React.

## Setup

Install the requirements:

```
pip install -r requirements.txt
```

Build the JavaScript file (I use [esbuild](https://esbuild.github.io/), but other builders such as Webpack would also work):

```
cd frontend
npx esbuild --bundle src/qa.jsx > ../static/qa.js
cd ..
```

Run the flask server:

```
flask run -p 3000
```
