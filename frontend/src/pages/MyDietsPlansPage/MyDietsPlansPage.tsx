import { API_KEYS } from '@/api';
import NewDietModal from '@/pages/NewDietModal';
import axios from 'axios';
import { useQuery } from 'react-query';
import LoadingPage from '../LoadingPage';
import { useAppSelector } from '@/hooks/useAppSelector';
import ErrorPage from '../ErrorPage';

const fetchDiets = async (token: string) => {
    const { data } = await axios.get('/api/diets/diet-plans/', {
        headers: { Authorization: `Bearer ${token}` },
    });
    return data;
};

const MyDietsPlansPage = () => {
    const authToken = useAppSelector((state) => state.app.authToken);

    if (!authToken) return <ErrorPage title="Access denied" />;

    const { data: diets, isLoading } = useQuery(API_KEYS.DIET_PLANS, () =>
        fetchDiets(authToken)
    );

    if (isLoading) return <LoadingPage title="Loading your diets..." />;

    return (
        <div>
            {/* {diets.map((diet) => (
                <div key={diet.id}>{diet.name}</div>
            ))} */}
            {<NewDietModal />}
        </div>
    );
};

export default MyDietsPlansPage;
