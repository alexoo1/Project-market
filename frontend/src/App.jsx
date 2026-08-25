import { Routes, Route, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import CategoryDetailPage from "./pages/CategoryDetailPage";
import SellPage from "./pages/SellPage";
import MessagesPage from "./pages/MessagesPage";
import ChatPage from "./pages/ChatPage";
import ProfilePage from "./pages/ProfilePage";
import ListingDetailPage from "./pages/ListingDetailPage";
import UserProfilePage from "./pages/UserProfilePage";
import NotificationsPage from "./pages/NotificationsPage";
import EditProfilePage from "./pages/EditProfilePage";
import OrderDetailPage from "./pages/OrderDetailPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import BottomNav from "./components/BottomNav";
import Navbar from "./components/ui/Navbar";
import styles from "./App.module.css";

export default function App() {
  const location = useLocation();
  const hideNav = location.pathname.startsWith("/messages/") || location.pathname === "/login" || location.pathname === "/register";

  return (
    <div className={styles.app}>
      {!hideNav && <Navbar />}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/categories/:id" element={<CategoryDetailPage />} />
        <Route path="/sell" element={<SellPage />} />
        <Route path="/sell/:id" element={<SellPage />} />
        <Route path="/messages" element={<MessagesPage />} />
        <Route path="/messages/:id" element={<ChatPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/listings/:id" element={<ListingDetailPage />} />
        <Route path="/users/:id" element={<UserProfilePage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/profile/edit" element={<EditProfilePage />} />
        <Route path="/orders/:id" element={<OrderDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
      {!hideNav && <BottomNav />}
    </div>
  );
}
