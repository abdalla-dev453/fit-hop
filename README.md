# FitPass Backend Service

FitPass is a multi-studio fitness membership and class reservation system built with Python, Flask, SQLAlchemy, Marshmallow, and JWT.

## Features Built

- **Authentication & Authorization**: User registration, login, JWT token issuance, and role management.
- **Pass & Credit System**: Browse available membership passes, purchase credits, track expiration dates, and automatically deduct credits on booking.
- **Class Booking Engine**: Real-time capacity checking, waiver checks, credit deduction, booking cancellations with credit refunds, and post-class reviews.
- **Database Architecture**: Fully linked relational models built with modern SQLAlchemy 2.0 (`back_populates`).
- **Validation & Serialization**: Marshmallow schemas enforcing strict request payload validation and unified error responses.

---

## Tech Stack

- **Framework**: Flask 3.0+
- **Database**: PostgreSQL / SQLite (via Flask-SQLAlchemy)
- **Migrations**: Flask-Migrate (Alembic)
- **Validation & Serialization**: Marshmallow & Flask-Marshmallow
- **Auth**: Flask-JWT-Extended
- **Testing**: Pytest & pytest-flask

---

## Getting Started

### 1. Clone & Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt