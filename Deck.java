package org.example;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

public class Deck {
    private ArrayList<String> cards;
    private Set<String> usedCards;
    public Deck() {
        this.cards = new ArrayList<>();
        this.usedCards = new HashSet<>();
        initialize();  // Ensure deck is initialized on creation
    }

    public static void main(String[]args){


    }
    public void setUsedCards(Set<String> usedCards) {
        this.usedCards.clear();
        this.usedCards.addAll(usedCards);
        initialize(); // ✅ Reinitialize the deck, ensuring excluded cards stay removed
    }


    public void initialize() {
        cards.clear(); // ✅ Prevents duplicate cards when re-initializing

        String[] suits = {"spades", "hearts", "diamonds", "clubs"};
        String[] values = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"};

        for (String suit : suits) {
            for (String value : values) {
                String card = formatCard(value, suit);
                if (!usedCards.contains(card.toLowerCase())) { // ✅ Ensure no duplicates
                    cards.add(card);
                }
            }
        }
        shuffle();
    }


    public ArrayList<String> getCards() {
        return new ArrayList<>(cards); // ✅ Returns a copy to prevent external modification
    }

    public void removeCard(String value, String suit) {
        String cardToRemove = formatCard(value, suit); // ✅ Ensures correct format
        cards.remove(cardToRemove);
    }

    public void shuffle() {
        Collections.shuffle(cards);
    }

    public String draw() {
        if (cards.isEmpty()) {
            System.out.println("⚠️ Deck is empty! Reshuffling...");
            initialize(); // ✅ Ensures deck is always properly filtered
        }

        String card;
        do {
            int index = (int) (Math.random() * cards.size());
            card = cards.get(index);
        } while (usedCards.contains(card.toLowerCase())); // ✅ Final check before returning

        cards.remove(card);
        return card;
    }


    public String drawPrecise(String value, String suit) {
        String card = value + " of " + suit.toLowerCase(); // ✅ Ensures consistent format
        cards.remove(card);
        return card;
    }
    public void removeCards() {
        cards.clear();  // ✅ Ensures the deck is properly reset
    }

    private String formatCard(String value, String suit) {
        return value.substring(0, 1).toUpperCase() + value.substring(1).toLowerCase() +
                " of " +
                suit.substring(0, 1).toLowerCase() + suit.substring(1).toLowerCase();
    }

}
