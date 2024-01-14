import { API_KEYS, client } from '@/api';
import NewDietModal from '@/pages/NewDietModal';
import { useQuery } from 'react-query';
import LoadingPage from '../LoadingPage';
import { useAppSelector } from '@/hooks/useAppSelector';
import ErrorPage from '../ErrorPage';

const fetchDiets = async (token: string) => {
    const { data } = await client.get('/diets/diet-plans/', {
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

    const renderedDiets = diets.results.map((diet) => (
        <div
            key={diet.id}
            className="border-secondary border-solid border-2 rounded mt-3 p-6 w-fit"
        >
            <h3>DIET NAME: {diet.name}</h3>
            {diet.days.map((day) => (
                <div key={day.id}>
                    <h4 className="font-bold">Day {day.day_number}</h4>
                    {day.meals.map((meal) => (
                        <div key={meal.id}>
                            <p>
                                {meal.meal_type}: {meal.meal.name}
                            </p>
                            <p>{meal.meal.description}</p>
                            <p>Calories: {meal.meal.calories}</p>
                        </div>
                    ))}
                </div>
            ))}
        </div>
    ));

    return (
        <>
            <NewDietModal />
            <div className="flex gap-4">{renderedDiets}</div>
        </>
    );
};

export default MyDietsPlansPage;
