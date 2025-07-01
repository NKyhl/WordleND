# WordleND

> Final Project for Programming Paradigms - CSE 30332

![Home page preview](/assets/readme/preview.jpeg)

**WordleND** is a remake of the popular game Wordle, developed using the Django framework in Python.

Our spin on the classic game includes language support for English, Spanish, German, French, and Portuguese users.

## Project Structure
```
wordlend/
├── src/
│ ├── webapp/           # Django project package
│ ├── wordleND/         # Django app module
│ │ ├── languages/          # Word Banks
│ │ ├── static/             # Static Assets
│ │ ├── templates/          # HTML Templates
│ │ ├── urls.py             # URL Routes
│ │ └── views.py            # Views
│ ├── db.sqlite3        # Local SQLite Database
│ └── manage.py         # Django Entry Point (CLI tool)
├── CONTRIBUTIONS.md
├── README.md
└── requirements.txt
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run project locally
python3 src/manage.py runserver
```

## Fake Payment API
For class, we integrated with a payment api created by our professor. Other viewers may disregard.

To use, create a file called `config.json` within the src/ folder of this Django project. This json file should have the following format:

```
{ 
    "username": "your-username",
    "password": "your-password",
    "access_token": "your-access_token"
}
```

## Notes

As of now, WordleND uses the US-keyboard and does not allow for special characters, though target words in languages other than english may include accents. This is an area for further development.

## Further Development
- Foreign alphabet keyboards
- Refactor Django template extension
- Share game results 🟩🟨⬛
- Add flip animation from left to right

