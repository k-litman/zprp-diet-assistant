import { Route, Routes } from 'react-router-dom';
import Header from '../components/Header';
import MyDietsPlansPage from '@/pages/MyDietsPlansPage';
import ProtectedRoute from '@/components/ProtectedRoute';

const App = () => {
    return (
        <div className="relative min-h-screen">
            <Header />
            <ProtectedRoute>
                <Routes>
                    <Route element={<MyDietsPlansPage />} path="/" />
                </Routes>
            </ProtectedRoute>
        </div>
    );
};

export default App;
