# Crossword Crocodile backend

## Description

A custom crossword maker. Enter your word into an elegant and verdant interface, and millions of calculations will check against a word bank of thousands to create complete crossword grids to your specifications.

## Instructions

This backend is live on [Heroku](https://cook-up-a-crossword.herokuapp.com/).
<br/>
The frontend counterpart can be found [here](https://github.com/chicorycolumn/Crossword-Crocodile-FE).
<br/>
The live site is on [Netlify](https://crossword-crocodile.netlify.app/).
<br/>
You can also download this repository and run the project locally by following these steps:

1. Clone this repository with `git clone https://github.com/chicorycolumn/Cook-Up-A-Crossword-BE`
   <br/>
   If you are unsure what this means, instructions can be found [here](https://www.wikihow.com/Clone-a-Repository-on-Github) or [here](https://www.howtogeek.com/451360/how-to-clone-a-github-repository/).

2. Open the project in a code editor, and run `pip install -r requirements.txt` to install necessary packages.

3. Run `python main_with_itertools.py` to run the project.

4. Use an API testing tool like Insomnia to test the endpoints of this project, by sending http requests to [http://localhost:5000](http://localhost:5000).

## Deploy

General instructions for taking a **Python project** and hosting it on **Heroku** for **automatic deployment** are as follows:

0. Ensure the project is initialised in a Git repository. If you are unsure what this means, instructions can be found [here](https://medium.com/@JinnaBalu/initialize-local-git-repository-push-to-the-remote-repository-787f83ff999) and [here](https://www.theserverside.com/video/How-to-create-a-local-repository-with-the-git-init-command).

1. Install the Heroku CLI if not already, with `pip install heroku`.

2. Run these three commands:

- `heroku login`
- `heroku create my-awesome-app --buildpack heroku/python`
- `heroku git:remote -a my-awesome-app`

3. Login to Heroku and enable automatic deploys from Github, and connect the repo.

4. Ensure the _requirements.txt_ file is up to date, with `pip freeze > requirements.txt`.

Now when you commit and push to Github, Heroku will deploy the latest version of the project automatically.

## Built with

- [Python](https://www.python.org/) - The backend coding language
- [PyCharm](https://www.jetbrains.com/pycharm/) - The backend code editor
- [TypeScript](https://www.typescriptlang.org/) - The frontend coding language
- [VisualStudioCode](https://code.visualstudio.com/) - The frontend code editor

- [Heroku](https://www.heroku.com/) - The cloud application platform used for the backend
- [Netlify](https://www.netlify.com/) - The hosting service used for the frontend

- [Eventlet](http://eventlet.net/) - The networking library
- [Flask](https://flask.palletsprojects.com/) - The microframework
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) - The backend realtime librar
- [Gunicorn](https://gunicorn.org/) - The Python server

- [Angular](https://angular.io/) - The frontend framework
- [Socket.IO](https://socket.io/) - The frontend realtime library
