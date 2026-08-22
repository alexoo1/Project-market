export const COLORS = {
  lagoon: "#0E3B36",
  lagoonSoft: "#164F48",
  coral: "#EF5A3C",
  sand: "#F6F1E7",
  sandDeep: "#EDE4D3",
  ink: "#161512",
  inkSoft: "#6B655A",
  danger: "#C0392B",
};

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
