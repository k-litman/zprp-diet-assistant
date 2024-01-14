import { Route, Routes } from 'react-router-dom';
import MyDietsPlansPage from '@/pages/MyDietsPlansPage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useEffect } from 'react';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { setAuthToken, setIsLoggedIn } from '@/store/appSlice';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';

const App = () => {
    const dispatch = useAppDispatch();

    useEffect(() => {
        const loginToken: string | null = localStorage.getItem('authToken');

        if (loginToken) {
            setAuthToken(loginToken);
            setIsLoggedIn(true);
        } else {
            dispatch(setIsLoggedIn(false));
        }
    }, []);

    return (
        <div className="relative min-h-screen">
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <MyDietsPlansPage />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </div>
    );
};

export default App;
