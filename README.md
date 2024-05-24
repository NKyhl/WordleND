# WordleND
Wordle-like Django Project for Programming Paradigms - CSE 30332

### Group Members
- Nolan Kyhl
- Miles Laning

### Language Support
- English
- Spanish
- German
- French
- Portuguese

### Setup
- pip install requests
- Create a file named config.json within the src/ folder of this Django project.
- This json file should have the following format:
`{"username": "your-username", "password": "your-password", "access_token": "your-access_token"}`
- This configures access to the fake payment api created by the professor. Leave fields blank if you do not have credentials.

**Errata**
- Game uses the US-keyboard and does not allow for special characters. If the word chosen has a special character, it's currently impossible to guess it. 
