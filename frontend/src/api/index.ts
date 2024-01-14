import axios from 'axios';

export const API_KEYS = {
    DIET_PLANS: 'DIET_PLANS',
};

export const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});
