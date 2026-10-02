# HelpDesk Telegram Bot

A Telegram-based help desk system for creating, managing, and tracking support tickets.

The bot has two user roles: **admin** and **user**, each with their own permissions and restrictions.

It can be used by companies to manage internal IT support requests. A user can create a ticket describing their problem and optionally attach a photo. An admin can take responsibility for the ticket, work on the issue, and complete it.

All ticket activity is displayed in a dedicated Telegram group, allowing the support team to keep track of incoming requests and their current status.

The concept is simple: **a user reports a problem → an admin takes the ticket → the problem gets resolved → the ticket is completed.**

Built with **Python, aiogram, SQLAlchemy, and SQLite**.


![Python](https://img.shields.io/badge/Python-3.17-3776AB?style=flat&logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3-2CA5E0?style=flat&logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2-red?style=flat&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)

## ✨ Features

- 👤 User and admin roles
- 🎫 Create and manage support tickets
- 📋 View user's tickets
- 🔄 Ticket status management
- 📄 Ticket pagination
- 🔐 Role-based access control
- 📸 Attach photos to tickets
- 🔔 Notifications
- 🗄️ Database persistence with SQLAlchemy

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/stanczyk224/HelpDeskTgBot
cd HelpDeskTgBot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows 🪟
.venv\Scripts\activate

# Linux 🐧/ macOS 🍎
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_bot_token
GROUP_CHAT_ID=your_chat_id
```

Replace the values with your Tg Bot Token and notification group Chat ID (-123456789).

### 5. Run the bot

```bash
python main.py
```

## 🌳 Project Structure

```text
## 🌳 Project Structure

```text
HelpDeskTgBot/
├── Enums/              # Application enums
├── Exceptions/         # Custom exceptions
├── Handlers/           # Telegram update handlers
├── Jobs/               # Background jobs
├── Keyboards/          # Telegram keyboards
├── Middlewares/        # Telegram middlewares
├── Models/             # SQLAlchemy models
├── Repositories/       # Database access layer
├── Service/            # Business logic
├── States/             # FSM states
├── Utils/              # Utility functions
│
├── db.py               # Database configuration
├── main.py             # Application entry point
├── requirements.txt    # Project dependencies
└── README.md
```
### Architecture

The project follows a layered structure:

- **Handlers** — handle Telegram updates and user interactions
- **Services** — contain business logic
- **Repositories** — handle database operations
- **Models** — define database entities
- **Middlewares** — provide user context and access control