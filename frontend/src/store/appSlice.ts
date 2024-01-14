import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface AppState {
    isLoggedIn?: boolean;
}

const initialState: AppState = {};

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
    },
});

export const { setIsLoggedIn } = appSlice.actions;

export default appSlice.reducer;
