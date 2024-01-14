import React, { useEffect } from 'react';
import { useMutation } from 'react-query';
import axios from 'axios';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { setAuthToken, setIsLoggedIn } from '@/store/appSlice';
import { Link, useNavigate } from 'react-router-dom';

interface UserDetails {
    username: string;
    password: string;
}

interface LoginResponse {
    token: string;
}

const login = async (userDetails: UserDetails) => {
    const { data } = await axios.post<LoginResponse>(
        '/api/users/login/',
        userDetails
    );

    return data;
};

const LoginPage = () => {
    const { mutate, isLoading, data } = useMutation(login);
    const dispatch = useAppDispatch();
    const navigate = useNavigate();

    const handleSubmit: React.FormEventHandler<HTMLFormElement> = (event) => {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const userDetails = {
            username: formData.get('username') as string,
            password: formData.get('password') as string,
        };

        mutate(userDetails);
    };

    useEffect(() => {
        if (!data) return;

        localStorage.setItem('authToken', data.token);
        dispatch(setAuthToken(data.token));
        dispatch(setIsLoggedIn(true));
        navigate('/');
    }, [data]);

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
                    Login
                </button>
                <p className="mt-4 text-center">
                    Dont have an account?{' '}
                    <Link to="/register" className="link link-primary">
                        Sign up
                    </Link>
                </p>
            </form>
        </div>
    );
};

export default LoginPage;
