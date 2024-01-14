import { useAppSelector } from '@/hooks/useAppSelector';
import LoadingPage from '@/pages/LoadingPage';
import LoginPage from '@/pages/LoginPage';

type Props = {
    children: React.ReactNode;
};

const ProtectedRoute = ({ children }: Props) => {
    const isLoggedIn = useAppSelector((state) => state.app.isLoggedIn);

    return (
        <>
            {isLoggedIn === undefined ? (
                <LoadingPage
                    title="Loading page..."
                    description="Stay patient! If it takes too long, refresh the page."
                />
            ) : isLoggedIn === false ? (
                <LoginPage />
            ) : (
                children
            )}
        </>
    );
};
export default ProtectedRoute;
