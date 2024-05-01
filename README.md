# WordleND
Wordle-like Django Project for Programming Paradigms - CSE 30332

**Group 15 Members:**
- Nolan Kyhl
- Miles Laning

**Language Support for:**
- English
- Spanish
- German
- French
- Portuguese

** Setup
- pip install requests
- Place a file called config.json within the src/ folder of this Django project. This json file should have the following format:

{ "username": "your-username",
  "password": "your-password",
  "access_token": "your-access_token"
}

- Game uses the US-keyboard and does not allow for special characters. If the random word has a special character, it's just a loss (after inputting 6 attempts). 
