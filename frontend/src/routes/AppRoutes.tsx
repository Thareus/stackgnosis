import { UserRoutes } from 'features/users/routes';
import { EntryRoutes } from 'features/entries/routes';
import { HomeRoutes } from 'features/home/routes';
import { Routes, Route } from 'react-router-dom';
import NotFound from 'shared/components/NotFound';
  
interface Props {
  isAuthenticated: boolean;
}

const AppRoutes = ({ isAuthenticated }: Props) => (
  <Routes>
    {HomeRoutes()}
    {UserRoutes()}
    {EntryRoutes(isAuthenticated)}
    <Route path="*" element={<NotFound />} />
  </Routes>
);

export default AppRoutes;