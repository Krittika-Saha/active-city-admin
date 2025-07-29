# Active City Administration
 test project for school practice

## Tech Stack

---
### Frontend
- [ ] React.js (With bootstrap)

### Backend
- [x] Python with Flask
- [ ] Google Maps API integration

### Database
- [x] MongoDB

## Instructions for Dev

---
### For Backend database
- Clone repository
- Install MongoDB from `https://www.mongodb.com/try/download/community` (along with the GUI)
- Install all requirments using `pip install -r requirements.txt`

## To run project

- Clone repository or download as zip file
![how to download zip file](https://i.ibb.co/n8cX3FrD/Screenshot-2025-07-29-093912.png "How to download zip file")
- Initialise a venv or configure python interpreter path
- Install all requirments using `pip install -r requirements.txt`
- Run `python3 back.py` to start backend server.
- [optional] Install mongoDB and MongoDB compass to visualise database.

### Creating Initial Users

The application requires at least one "mayor" and one "official" user to test all features.
1. Run the application (`python back.py`).
2. Navigate to `http://127.0.0.1:5000/register`.
3. Create a user with the role `mayor`.
4. Create another user with the role `official` and select a department (e.g., "Water").
