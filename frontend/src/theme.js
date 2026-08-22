export function formatFCFA(n) {
  return new Intl.NumberFormat("fr-FR").format(n) + " FCFA";
}

export const CONDITION_LABELS = {
  new_with_tag: "Neuf avec étiquette",
  new_without_tag: "Neuf sans étiquette",
  very_good: "Très bon état",
  good: "Bon état",
  satisfactory: "Satisfaisant",
};

export const ORDER_STATUS_LABELS = {
  pending_payment: "En attente de paiement",
  paid: "Payée",
  seller_confirmation: "Confirmation vendeur",
  ready_for_delivery: "Prête pour livraison",
  shipped: "Expédiée",
  delivered: "Livrée",
  buyer_confirmed: "Réception confirmée",
  completed: "Terminée",
  cancelled: "Annulée",
  disputed: "Litige",
  refunded: "Remboursée",
};

export const DELIVERY_METHOD_LABELS = {
  home_delivery: "Livraison à domicile",
  pickup_point: "Point relais",
  hand_delivery: "Remise en main propre",
};
