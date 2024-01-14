import React from 'react';
import { useMutation } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { client } from '@/api';

interface RegistrationDetails {
    username: string;
    password: string;
    email: string;
}

const register = async (registrationDetails: RegistrationDetails) => {
    const response = await client.post('/users/', registrationDetails);
    return response.data;
};

const RegisterPage = () => {
    const { mutate, isLoading } = useMutation(register);
    const navigate = useNavigate();

    const handleSubmit: React.FormEventHandler<HTMLFormElement> = (event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const registrationDetails = {
            username: formData.get('username') as string,
            password: formData.get('password') as string,
            email: formData.get('email') as string,
        };

        mutate(registrationDetails, {
            onSuccess: () => {
                navigate('/login');
            },
        });
    };

    return (
        <div className="container mx-auto min-h-screen flex">
            <form
                onSubmit={handleSubmit}
                className="form-control w-full max-w-xs m-auto"
            >
                <span className="label">
                    <span className="label-text">Username</span>
                </span>
                <input
                    type="text"
                    placeholder="Username"
                    name="username"
                    className="input input-bordered w-full max-w-xs"
                />

                <span className="label">
                    <span className="label-text">Email</span>
                </span>
                <input
                    type="email"
                    placeholder="Email"
                    name="email"
                    className="input input-bordered w-full max-w-xs"
                />

                <span className="label">
                    <span className="label-text">Password</span>
                </span>
                <input
                    type="password"
                    placeholder="Password"
                    name="password"
                    className="input input-bordered w-full max-w-xs"
                />

                <button
                    type="submit"
                    className={`btn btn-primary mt-4 ${
                        isLoading ? 'loading' : ''
                    }`}
                >
                    Register
                </button>
            </form>
        </div>
    );
};

export default RegisterPage;
