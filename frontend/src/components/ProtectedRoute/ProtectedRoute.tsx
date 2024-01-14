import { useAppSelector } from '@/hooks/useAppSelector';
import ErrorPage from '@/pages/ErrorPage';
import LoadingPage from '@/pages/LoadingPage';

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
                <ErrorPage title="No MetaMask detected" />
            ) : (
                children
            )}
        </>
    );
};
export default ProtectedRoute;
