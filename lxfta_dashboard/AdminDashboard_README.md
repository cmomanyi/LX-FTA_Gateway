
# 🛠️ Admin Dashboard – User Role Manager (React + Email Notifications)

A simple admin dashboard built with **React** that allows administrators to:

- Add users
- Delete users
- Assign/change roles
- Notify users via **email** when their account is created
- Show in-app toast notifications for all events

---

## 🚀 Features

- Role-based user management
- Live alerts with `react-toastify`
- Email notifications via `EmailJS`
- Styled with Tailwind CSS (optional)

---

## 📁 Folder Structure

```
src/
├── components/
│   ├── AdminDashboard.jsx
│   ├── UserForm.jsx
│   └── UserTable.jsx
├── utils/
│   └── emailService.js
├── data/
│   └── mockUsers.js
├── App.js
└── index.css
```

---

## 🖥️ Frontend Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/admin-dashboard.git
cd admin-dashboard
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run the App

```bash
npm start
```

The app will run on [http://localhost:3000](http://localhost:3000).

---

## 📧 EmailJS Setup

To send emails when a user is added:

### 1. Create a Free EmailJS Account

- Visit [https://www.emailjs.com](https://www.emailjs.com)
- Sign up and log in

### 2. Set Up an Email Service

- Go to **Email Services**
- Add and connect your Gmail or other service provider

### 3. Create an Email Template

- Go to **Email Templates**
- Add a new template with the following variables:
  ```
  {{to_name}}
  {{to_email}}
  {{role}}
  ```

#### Example Template Message

```
Hi {{to_name}}, your account has been created and assigned the role of {{role}}. You can now log in and start using the system.
```

### 4. Get Your IDs

- Copy the **Service ID**, **Template ID**, and **Public Key** from your EmailJS dashboard.

### 5. Update `emailService.js`

```js
// src/utils/emailService.js

const SERVICE_ID = "your_service_id";
const TEMPLATE_ID = "your_template_id";
const PUBLIC_KEY = "your_public_key";
```

---

## 📦 Installed Dependencies

| Package           | Purpose                              |
|------------------|--------------------------------------|
| react-toastify    | In-app toast alerts                  |
| emailjs-com       | Email sending via client-side JS     |
| tailwindcss       | Optional utility-first CSS styling   |

Install Tailwind (optional):

```bash
npm install -D tailwindcss
npx tailwindcss init
```

Update `tailwind.config.js` and include Tailwind in `index.css`.

---

## ✅ Final Notes

- Make sure you do **not** expose sensitive keys in production (EmailJS public key is safe for frontend)
- All events are logged via toasts and also trigger email notifications

---

## 📬 Questions?

Feel free to open an issue or contact the maintainer.
