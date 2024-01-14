import React, { useState, useRef } from 'react';
import { useQueryClient } from 'react-query';
import { useAppSelector } from '@/hooks/useAppSelector';
import { capitalize } from 'lodash';
import axios from 'axios';
import { client } from '@/api';

interface ErrorResponse {
    code: string;
    detail: {
        [key: string]: string[];
    };
}

const NewDietModal = () => {
    const queryClient = useQueryClient();
    const modalRef = useRef<HTMLDialogElement>(null);

    const [name, setName] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [days, setDays] = useState<number>();
    const [mealsPerDay, setMealsPerDay] = useState<number>();
    const [cuisineType, setCuisineType] = useState<string>('it');
    const [isVegan, setIsVegan] = useState<boolean>();
    const [restrictedIngredients, setRestrictedIngredients] = useState<
        string[]
    >([]);
    const [calories, setCalories] = useState<number>();
    const authToken = useAppSelector((state) => state.app.authToken);

    const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (
        event
    ) => {
        event.preventDefault();
        const newDiet = {
            name,
            days,
            meals_per_day: mealsPerDay,
            cuisine_type: cuisineType,
            veganity: { vegan: isVegan },
            restricted_ingredients: restrictedIngredients,
            calories,
        };

        try {
            if (!modalRef || !modalRef.current) return;

            await client.post('/diets/diet-plans/', newDiet, {
                headers: { Authorization: `Bearer ${authToken}` },
            });
            queryClient.invalidateQueries('diets');
            modalRef.current.close();
        } catch (error) {
            if (
                axios.isAxiosError(error) &&
                error.response &&
                error.response.data
            ) {
                const errorMessage = error.response.data as ErrorResponse;
                const errorKeys = Object.keys(errorMessage.detail);

                if (errorKeys.length === 0)
                    setError('There was an error generating diet!');
                else
                    setError(
                        `${capitalize(errorKeys[0])}: ${errorMessage.detail[errorKeys[0]]}`
                    );
            }
        }
    };

    const openModal = () => {
        if (modalRef.current) {
            modalRef.current.showModal();
        }
    };

    const closeModal = () => {
        if (modalRef.current) {
            modalRef.current.close();
        }
    };

    return (
        <>
            <button onClick={openModal} className="btn btn-primary">
                Add Diet Plan
            </button>

            <dialog ref={modalRef} className="modal" id="new_diet_modal">
                <div className="modal-box">
                    <form onSubmit={handleSubmit}>
                        {error && (
                            <div className="alert alert-error shadow-lg mt-4">
                                <div>
                                    <span>{error}</span>
                                </div>
                            </div>
                        )}
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Diet Plan Name"
                            className="input input-bordered w-full max-w-xs"
                        />
                        <input
                            type="number"
                            value={days}
                            onChange={(e) => setDays(parseInt(e.target.value))}
                            placeholder="Number of Days"
                            className="input input-bordered w-full max-w-xs"
                        />
                        <input
                            type="number"
                            value={mealsPerDay}
                            onChange={(e) =>
                                setMealsPerDay(parseInt(e.target.value))
                            }
                            placeholder="Meals per Day"
                            className="input input-bordered w-full max-w-xs"
                        />
                        <select
                            value={cuisineType}
                            onChange={(e) => setCuisineType(e.target.value)}
                            className="select select-bordered w-full max-w-xs"
                        >
                            <option value="it">Italian</option>
                            <option value="pl">Polish</option>
                            <option value="fr">French</option>
                            <option value="mx">Mexican</option>
                            <option value="as">Asian</option>
                            <option value="sp">Spanish</option>
                            <option value="us">American</option>
                        </select>
                        <label className="label cursor-pointer">
                            <span className="label-text">Is Vegan?</span>
                            <input
                                type="checkbox"
                                checked={isVegan}
                                onChange={(e) => setIsVegan(e.target.checked)}
                                className="checkbox checkbox-primary"
                            />
                        </label>
                        <input
                            type="text"
                            value={restrictedIngredients[0]}
                            onChange={(e) =>
                                setRestrictedIngredients([e.target.value])
                            }
                            placeholder="Restricted Ingredients"
                            className="input input-bordered w-full max-w-xs"
                        />
                        <input
                            type="number"
                            value={calories}
                            onChange={(e) =>
                                setCalories(parseInt(e.target.value))
                            }
                            placeholder="Calories"
                            className="input input-bordered w-full max-w-xs"
                        />
                        <div className="modal-action">
                            <button type="submit" className="btn btn-success">
                                Submit
                            </button>
                            <button
                                type="button"
                                onClick={closeModal}
                                className="btn btn-error"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </dialog>
        </>
    );
};

export default NewDietModal;
