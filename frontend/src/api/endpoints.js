import { api, setTokens, clearTokens } from "./client";

// --- Auth ---
export async function register(payload) {
  const data = await api.post("/auth/register", payload, { auth: false });
  setTokens(data);
  return data;
}

export async function login(identifier, password) {
  const data = await api.post("/auth/login", { identifier, password }, { auth: false });
  setTokens(data);
  return data;
}

export function logout() {
  clearTokens();
}

export function getMe() {
  return api.get("/auth/me");
}

// --- Taxonomy ---
export function getCategories() {
  return api.get("/categories", { auth: false });
}
export function getBrands() {
  return api.get("/brands", { auth: false });
}

// --- Uploads ---
export function uploadImages(files) {
  return api.upload("/uploads/images", files);
}

// --- Listings ---
export function searchListings(params = {}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  ).toString();
  return api.get(`/listings${query ? `?${query}` : ""}`, { auth: false });
}
export function getListing(id) {
  return api.get(`/listings/${id}`, { auth: false });
}
export function createListing(payload) {
  return api.post("/listings", payload);
}
export function updateListing(id, payload) {
  return api.patch(`/listings/${id}`, payload);
}
export function deleteListing(id) {
  return api.delete(`/listings/${id}`);
}
export function getMyListings() {
  return api.get("/listings/mine");
}

// --- Favorites ---
export function getFavorites() {
  return api.get("/favorites");
}
export function addFavorite(listingId) {
  return api.put(`/favorites/${listingId}`);
}
export function removeFavorite(listingId) {
  return api.delete(`/favorites/${listingId}`);
}

// --- Offers ---
export function createOffer(listingId, amount) {
  return api.post(`/listings/${listingId}/offers`, { amount });
}
export function acceptOffer(offerId) {
  return api.patch(`/offers/${offerId}/accept`);
}
export function rejectOffer(offerId) {
  return api.patch(`/offers/${offerId}/reject`);
}
export function counterOffer(offerId, amount) {
  return api.post(`/offers/${offerId}/counter`, { amount });
}
export function getMyOffers() {
  return api.get("/offers/mine");
}

// --- Conversations ---
export function startConversation(listingId) {
  return api.post("/conversations", { listing_id: listingId });
}
export function getConversations() {
  return api.get("/conversations");
}
export function getConversation(id) {
  return api.get(`/conversations/${id}`);
}
export function getMessages(conversationId) {
  return api.get(`/conversations/${conversationId}/messages`);
}
export function sendMessage(conversationId, content) {
  return api.post(`/conversations/${conversationId}/messages`, { content });
}

// --- Orders ---
export function purchaseListing(listingId, payload) {
  return api.post(`/listings/${listingId}/purchase`, payload);
}
export function purchaseFromOffer(offerId, payload) {
  return api.post(`/offers/${offerId}/purchase`, payload);
}
export function getOrder(orderId) {
  return api.get(`/orders/${orderId}`);
}
export function payOrder(orderId) {
  return api.post(`/orders/${orderId}/pay`);
}
export function shipOrder(orderId) {
  return api.post(`/orders/${orderId}/ship`);
}
export function confirmReceipt(orderId) {
  return api.post(`/orders/${orderId}/confirm-receipt`);
}
export function cancelOrder(orderId) {
  return api.post(`/orders/${orderId}/cancel`);
}
export function getMyPurchases() {
  return api.get("/orders/mine/purchases");
}
export function getMySales() {
  return api.get("/orders/mine/sales");
}

// --- Reviews ---
export function createReview(orderId, rating, comment) {
  return api.post(`/orders/${orderId}/reviews`, { rating, comment });
}
export function getUserReviews(userId) {
  return api.get(`/users/${userId}/reviews`, { auth: false });
}

// --- Follows ---
export function followUser(userId) {
  return api.put(`/users/${userId}/follow`);
}
export function unfollowUser(userId) {
  return api.delete(`/users/${userId}/follow`);
}
export function getFollowStatus(userId) {
  return api.get(`/users/${userId}/follow-status`);
}

// --- Notifications ---
export function getNotifications() {
  return api.get("/notifications");
}
export function getUnreadCount() {
  return api.get("/notifications/unread-count");
}
export function markAllRead() {
  return api.post("/notifications/read-all");
}
