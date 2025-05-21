import { Route } from 'react-router-dom';
import RegistrationPage from './registration/RegistrationPage';
import LoginPage from './login/LoginPage';
import UserProfile from './profile/UserProfile';
import BookmarkPage from './bookmarks/BookmarkPage';

export const UserRoutes = () => (
    <>
    <Route key="registration" path="/registration" element={<RegistrationPage/>} />
    <Route key="login" path="/login" element={<LoginPage/>} />
    <Route key="profile" path="/users/:slug/profile" element={<UserProfile />} />
    <Route key="bookmarks" path="/users/:slug/bookmarks" element={<BookmarkPage />} />
    </>
);
