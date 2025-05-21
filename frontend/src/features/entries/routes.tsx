import { Route } from 'react-router-dom';
import EntryList from './EntryList';
import EntryPage from './EntryPage';
import EntryNotFound from './EntryNotFound';
import CreateEntry from './CreateEntry';
import LoginRequiredRoute from 'shared/components/LoginRequiredRoute'; 

export const EntryRoutes = (isAuthenticated: boolean) => (
    <>
        <Route 
            key="list"
            path="/entries"
            element={
                <LoginRequiredRoute isAuthenticated={isAuthenticated}>
                    <EntryList />
                </LoginRequiredRoute>
            }
        />
        <Route 
            key="page"
            path="/entries/:slug"
            element={
                <LoginRequiredRoute isAuthenticated={isAuthenticated}>
                    <EntryPage />
                </LoginRequiredRoute>
            }
        />
        <Route 
            key="notfound"
            path="/entries/not-found"
            element={
                <LoginRequiredRoute isAuthenticated={isAuthenticated}>
                    <EntryNotFound />
                </LoginRequiredRoute>
            }
        />
        <Route 
            key="create"
            path="/entries/create"
            element={
                <LoginRequiredRoute isAuthenticated={isAuthenticated}>
                    <CreateEntry />
                </LoginRequiredRoute>
            }
        />
    </>
);