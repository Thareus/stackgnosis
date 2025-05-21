import { Route } from 'react-router-dom';
import HomePage from './HomePage';

export const HomeRoutes = () => (
    <Route key="home" path="/" element={<HomePage />} />
);