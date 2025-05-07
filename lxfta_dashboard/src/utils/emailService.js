// src/utils/emailService.js
import emailjs from 'emailjs-com';

const SERVICE_ID = 'service_d791qee';
const TEMPLATE_ID = 'template_r7buu7j';
const PUBLIC_KEY = 'GmS5kc4oWae47rKLs';

export const sendAccountCreatedEmail = (user) => {
    const templateParams = {
        to_name: user.name,
        to_email: user.email,
        role: user.role,
    };

    return emailjs.send(SERVICE_ID, TEMPLATE_ID, templateParams, PUBLIC_KEY);
};
