import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface AppState {
    isLoggedIn: boolean;
    authToken: string | null;
}

const initialState: AppState = {
    isLoggedIn: localStorage.getItem('authToken') !== null,
    authToken: localStorage.getItem('authToken'),
};

export const appSlice = createSlice({
    name: 'counter',
    initialState,
    reducers: {
        setIsLoggedIn: (
            state,
            action: PayloadAction<AppState['isLoggedIn']>
        ) => {
            state.isLoggedIn = action.payload;
        },

        setAuthToken: (state, action: PayloadAction<AppState['authToken']>) => {
            state.authToken = action.payload;
        },
    },
});

export const { setIsLoggedIn, setAuthToken } = appSlice.actions;

export default appSlice.reducer;
