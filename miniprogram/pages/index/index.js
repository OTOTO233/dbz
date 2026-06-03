const bazaar = require("../../data/bazaarData");

function includesText(value, keyword) {
  return String(value || "").toLowerCase().includes(keyword);
}

function enrichCard(card) {
  const metaParts = [card.hero, card.tier];
  if (card.size) {
    metaParts.push(card.size);
  }
  return {
    ...card,
    initial: card.name.slice(0, 1),
    meta: metaParts.join(" · "),
  };
}

const cards = bazaar.cards.map(enrichCard);

Page({
  data: {
    patch: bazaar.patch,
    categories: [],
    heroes: bazaar.heroes,
    tiers: bazaar.tiers,
    sizes: bazaar.sizes,
    tags: bazaar.tags,
    cards,
    filteredCards: [],
    activeCategory: "all",
    activeHero: "",
    activeTier: "",
    activeSize: "",
    activeTag: "",
    keyword: "",
    selectedCard: null,
    filterOpen: false,
  },

  onLoad() {
    this.refreshCategories();
    this.applyFilters();
  },

  refreshCategories() {
    const categories = bazaar.categories.map((category) => {
      if (category.id === "all") {
        return {
          ...category,
        count: cards.length,
        };
      }
      const localCount = cards.filter((card) => card.category === category.id).length;
      return {
        ...category,
        localCount,
      };
    });
    this.setData({ categories });
  },

  switchCategory(event) {
    this.setData({
      activeCategory: event.currentTarget.dataset.id,
    });
    this.applyFilters();
  },

  onSearchInput(event) {
    this.setData({
      keyword: event.detail.value,
    });
    this.applyFilters();
  },

  toggleFilterPanel() {
    this.setData({
      filterOpen: !this.data.filterOpen,
    });
  },

  selectHero(event) {
    const value = event.currentTarget.dataset.value;
    this.setData({
      activeHero: this.data.activeHero === value ? "" : value,
    });
    this.applyFilters();
  },

  selectTier(event) {
    const value = event.currentTarget.dataset.value;
    this.setData({
      activeTier: this.data.activeTier === value ? "" : value,
    });
    this.applyFilters();
  },

  selectSize(event) {
    const value = event.currentTarget.dataset.value;
    this.setData({
      activeSize: this.data.activeSize === value ? "" : value,
    });
    this.applyFilters();
  },

  selectTag(event) {
    const value = event.currentTarget.dataset.value;
    this.setData({
      activeTag: this.data.activeTag === value ? "" : value,
    });
    this.applyFilters();
  },

  clearFilters() {
    this.setData({
      activeCategory: "all",
      activeHero: "",
      activeTier: "",
      activeSize: "",
      activeTag: "",
      keyword: "",
    });
    this.applyFilters();
  },

  applyFilters() {
    const keyword = this.data.keyword.trim().toLowerCase();
    const filteredCards = cards.filter((card) => {
      const matchCategory = this.data.activeCategory === "all" || card.category === this.data.activeCategory;
      const matchHero = !this.data.activeHero || card.hero === this.data.activeHero;
      const matchTier = !this.data.activeTier || card.tier === this.data.activeTier;
      const matchSize = !this.data.activeSize || card.size === this.data.activeSize;
      const matchTag = !this.data.activeTag || card.tags.includes(this.data.activeTag);
      const matchKeyword =
        !keyword ||
        includesText(card.name, keyword) ||
        includesText(card.hero, keyword) ||
        includesText(card.tier, keyword) ||
        includesText(card.effect, keyword) ||
        card.tags.some((tag) => includesText(tag, keyword));

      return matchCategory && matchHero && matchTier && matchSize && matchTag && matchKeyword;
    });

    this.setData({ filteredCards });
  },

  openCard(event) {
    const id = event.currentTarget.dataset.id;
    const selectedCard = cards.find((card) => card.id === id);
    this.setData({ selectedCard });
  },

  closeCard() {
    this.setData({ selectedCard: null });
  },

  noop() {},
});
