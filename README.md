## Instructions

This application is live on [Heroku](https://cook-up-a-crossword.herokuapp.com/), but you can also download this repository and run the project locally by following these steps:

1. Clone this repository with `git clone https://github.com/chicorycolumn/Cook-Up-A-Crossword-BE`
   <br/>
   If you are unsure what this means, instructions can be found [here](https://www.wikihow.com/Clone-a-Repository-on-Github) or [here](https://www.howtogeek.com/451360/how-to-clone-a-github-repository/).

2. Open the project in a code editor, and run `pip install -r requirements.txt` to install necessary packages.

3. Run `python main_with_itertools.py` to run the project.

4. Use an API tester like Insomnia to test the endpoints of this project, by sending http requests to [http://localhost:5000](http://localhost:5000).

The frontend counterpart to this project can be found [here](https://github.com/chicorycolumn/Crossword-Crocodile-FE).

## Deploy

## Description

A custom crossword creator. After entering your words into an elegant and verdant interface, millions of calculations rearrange your specified words and check against a word bank of thousands to create complete crossword grids to your specifications.

I took this opportunity to learn a new programming language for the backend - Python - and a new framework for the frontend - Angular. I chose Python for being one of the most widely used languages in data science, as well as further diversification of my coding knowledge. Its extensive range of modules and libraries would also come in useful.

## Challenges

The first was the wonderful puzzle of determining the most time-efficient method of crunching the millions of permutations of words that the app has to perform. I experimented with radically different approaches, based around 'for loops', 'recursion', and 'yield'. I finally rewrote the backend from scratch to use a Python module called itertools, and fixed the app to switch between two itertoools methods ('permutations' and 'product'), which my testing revealed to ultimately yield the fastest response times.

A key feature I wanted was for the user to receives the results in real-time, rather than waiting for a set interval and then receiving them all at once. After many setbacks and spikes, it certainly seemed that the easier path was to just accept the less optimal user experience, but through determined research and testing, I succeeded in creating a RESTful backend server delivering real-time results, which I accomplished with Flask (a web framework used by sites such as Pinterest and LinkedIn) and Flask-SocketIO.

## What I learned

It was really interesting to learn Angular, working within a different project structure style to what I was familiar with in React. As a first impression I found it more fiddly in Angular to connect up the Components, Services, and Modules, though I can see how this lends itself to having more expandable modularity with regard to different people working on different sections of the project, suggesting that Angular is better suited to heavyweight applications than are React and Vue.
