# FitPass Backend Capability & API Guide

This document outlines the capabilities, endpoints, database entities, and validation logic completed in the current version of FitPass.

---

## 1. System Overview

The FitPass backend provides a complete operational workflow for users to discover studio fitness classes, buy credit passes, manage bookings, and leave reviews.

### Core Architecture Components
1. **Flask API Engine**: Handles requests through blueprint modularity (`auth`, `passes`, `bookings`).
2. **SQLAlchemy 2.0 ORM**: Data abstraction layer using `back_populates` for clean bidirectional ORM relationships.
3. **Marshmallow Schemas**: Provides serialization (Python object -> JSON) and input validation before execution.
4. **JWT Security**: Secures endpoints with stateless JSON Web Tokens.

---

## 2. Completed Functionalities

### A. Authentication & Profiles (`/auth`)
- **User Registration**: Creates `User` and `UserProfile` atomically. Ensures email uniqueness and enforces minimum password lengths.
- **Password Security**: Uses Werkzeug salted password hashing (`pbkdf2:sha256`).
- **User Login**: Validates credentials and returns JWT access tokens.
- **Profile Fetching**: Retrieves identity, role (`client`, `trainer`, `admin`), and personal profile details.

### B. Pass & Credit System (`/passes`)
- **Pass Catalog**: Public listing of available pass packages (e.g., 5-class, 10-class, monthly unlimited).
- **Pass Purchase**: Assigns credit balance and dynamically calculates expiration (`current_time + duration_days`).
- **Credit Tracking**: Tracks active credit balances and historical passes for each user.

### C. Booking Engine (`/bookings`)
- **Waiver Guardrail**: Blocks booking requests if the user has not signed the liability waiver (`waiver_signed=False`).
- **Class Capacity Guardrail**: Rejects bookings if the class capacity is full.
- **Automated Credit Deduction**: Automatically picks the user's active pass closest to expiration and deducts 1 credit.
- **Duplicate Prevention**: Prevents a user from booking the same class twice.
- **Cancellation & Refunds**: Allows users to cancel upcoming class bookings and automatically restores their credit.
- **Review System**: Allows users to rate (1–5 stars) and review classes they have attended.

---

## 3. API Reference Endpoint Summary

| Blueprint | Method | Endpoint | Description | Auth Required |
|---|---|---|---|---|
| **Auth** | `POST` | `/auth/register` | Register new user + profile | No |
| **Auth** | `POST` | `/auth/login` | Authenticate and get JWT | No |
| **Auth** | `GET` | `/auth/me` | Fetch authenticated user | Yes |
| **Passes** | `GET` | `/passes` | List available pass packages | No |
| **Passes** | `GET` | `/passes/my-passes` | View user's purchased passes | Yes |
| **Passes** | `POST` | `/passes/purchase/<id>` | Purchase a pass package | Yes |
| **Bookings**| `POST` | `/bookings` | Book a fitness class | Yes |
| **Bookings**| `GET` | `/bookings` | Get user's booked classes | Yes |
| **Bookings**| `DELETE`| `/bookings/<id>` | Cancel booking & restore credit| Yes |
| **Bookings**| `POST` | `/bookings/<id>/review`| Submit post-class rating | Yes |

---

## 4. Global Error Protocol

Validation failures triggered by Marshmallow yield a standard `400 Bad Request` structure:

```json
{
  "error": "Validation failed",
  "messages": {
    "email": ["Email is already registered."],
    "password": ["Shorter than minimum length 6."]
  }
}