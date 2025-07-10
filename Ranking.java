package org.example;

import java.util.*;
import java.util.stream.Collectors;

public class Ranking {
    public Deck deck;
    public ArrayList<String> bestHandPlayer;
    public ArrayList<String> bestHandVillain;
    public ArrayList<String> communityCards;
    public Set<String> usedCards;
    private int points;

    public static void main(String[] args) {
        Ranking ranking = new Ranking(); // Create ranking instance
        Scanner scanner = new Scanner(System.in);

        // Get player and villain hands
        System.out.println("What cards do you have?");
        String cardsHero = scanner.nextLine();
        System.out.println("What cards does your opponent have?");
        String cardsVillain = scanner.nextLine();

        // Deal hole cards
        System.out.println("\nYour hand: " + ranking.handPlayer(cardsHero));
        System.out.println("Opponent's hand: " + ranking.handVillain(cardsVillain));

        // Generate and display community cards
        ArrayList<String> communityCards = ranking.communityCards(ranking);
        System.out.println("\nCommunity Cards: " + communityCards);

        // Update best hands for both players
        ranking.updateBestHand(ranking.bestHandPlayer, ranking.bestHandPlayer);
        ranking.updateBestHand(ranking.bestHandVillain, ranking.bestHandVillain);

        // Determine best hand combinations
        HandResult playerResult = ranking.findBestFiveCardHand(ranking.bestHandPlayer);
        HandResult villainResult = ranking.findBestFiveCardHand(ranking.bestHandVillain);

        // Display best 5-card hands
        System.out.println("\n✅ Player's Best Hand: " + playerResult.bestHand);
        System.out.println("🏆 Player's Hand Type: " + playerResult.handName);
        System.out.println("\n✅ Villain's Best Hand: " + villainResult.bestHand);
        System.out.println("🏆 Villain's Hand Type: " + villainResult.handName);

        // Compare scores
        int playerScore = ranking.evaluateHand(playerResult.bestHand);
        int villainScore = ranking.evaluateHand(villainResult.bestHand);
        System.out.println("\n🔢 Player's Hand Score: " + playerScore);
        System.out.println("🔢 Villain's Hand Score: " + villainScore);

        // Determine winner
        if (playerScore > villainScore) {
            System.out.println("\n🎉 Player Wins with " + playerResult.handName + "!");
        } else if (playerScore < villainScore) {
            System.out.println("\n👑 Villain Wins with " + villainResult.handName + "!");
        } else {
            System.out.println("\n🤝 It's a Draw! Both players have " + playerResult.handName + ".");
        }
    }


    public Ranking() {
        this.deck = new Deck(); // ✅ Create a NEW deck object every time
        this.deck.removeCards(); // ✅ Ensure any leftover cards are cleared (Extra safety)
        this.deck.initialize(); // ✅ Completely reinitialize the deck with all 52 cards
        this.deck.shuffle(); // ✅ Shuffle so the order is randomized
        this.bestHandPlayer = new ArrayList<>();
        this.bestHandVillain = new ArrayList<>();
        this.usedCards = new HashSet<>();
    }





    public ArrayList<String> handPlayer(String cardsHero) {
        ArrayList<String> cardsPlayer = new ArrayList<>();

        if (cardsHero != null && !cardsHero.isEmpty()) {
            // ✅ Split input into cards
            String[] cardParts = cardsHero.split(", ");

            if (cardParts.length == 1) { // ✅ One card provided → Use it & draw one more
                String[] firstCard = cardParts[0].split(" ");
                if (firstCard.length < 3) {
                    System.out.println("Invalid card format.");
                    return new ArrayList<>();
                }

                String value1 = firstCard[0];
                String suit1 = firstCard[2].toLowerCase();

                // ✅ Add specified card and draw one random card
                String drawnCard1 = deck.drawPrecise(value1, suit1);
                String drawnCard2 = deck.draw(); // Draw the second card randomly

                if (drawnCard1 != null) cardsPlayer.add(drawnCard1);
                if (drawnCard2 != null) cardsPlayer.add(drawnCard2);
            } else if (cardParts.length == 2) { // ✅ Two cards provided → Use both
                String[] firstCard = cardParts[0].split(" ");
                String[] secondCard = cardParts[1].split(" ");

                if (firstCard.length < 3 || secondCard.length < 3) {
                    System.out.println("Invalid card format.");
                    return new ArrayList<>();
                }

                String value1 = firstCard[0];
                String suit1 = firstCard[2].toLowerCase();
                String value2 = secondCard[0];
                String suit2 = secondCard[2].toLowerCase();

                // ✅ Add both specified cards
                String drawnCard1 = deck.drawPrecise(value1, suit1);
                String drawnCard2 = deck.drawPrecise(value2, suit2);

                if (drawnCard1 != null) cardsPlayer.add(drawnCard1);
                if (drawnCard2 != null) cardsPlayer.add(drawnCard2);
            }
        }

        // ✅ If no cards were provided → Draw two random cards
        while (cardsPlayer.size() < 2) {
            String drawnCard = deck.draw(); // Ensure draw() actually removes from deck
            if (drawnCard != null) {
                cardsPlayer.add(drawnCard);
            } else {
                System.out.println("Error: Deck is empty or draw() returned null.");
            }
        }

        bestHandPlayer.addAll(cardsPlayer);
        return cardsPlayer;
    }



    public ArrayList<String> handVillain(String cardsVillain) {
        ArrayList<String> cardsOp = new ArrayList<>();

        if (cardsVillain != null && !cardsVillain.isEmpty()) {
            // ✅ Split input into cards
            String[] cardParts = cardsVillain.split(", ");

            if (cardParts.length == 1) { // ✅ One card provided → Use it & draw one more
                String[] firstCard = cardParts[0].split(" ");
                if (firstCard.length < 3) {
                    System.out.println("Invalid card format.");
                    return new ArrayList<>();
                }

                String value1 = firstCard[0];
                String suit1 = firstCard[2].toLowerCase();

                // ✅ Add specified card and draw one random card
                String drawnCard1 = deck.drawPrecise(value1, suit1);
                String drawnCard2 = deck.draw(); // Draw the second card randomly

                if (drawnCard1 != null) cardsOp.add(drawnCard1);
                if (drawnCard2 != null) cardsOp.add(drawnCard2);
            } else if (cardParts.length == 2) { // ✅ Two cards provided → Use both
                String[] firstCard = cardParts[0].split(" ");
                String[] secondCard = cardParts[1].split(" ");

                if (firstCard.length < 3 || secondCard.length < 3) {
                    System.out.println("Invalid card format.");
                    return new ArrayList<>();
                }

                String value1 = firstCard[0];
                String suit1 = firstCard[2].toLowerCase();
                String value2 = secondCard[0];
                String suit2 = secondCard[2].toLowerCase();

                // ✅ Add both specified cards
                String drawnCard1 = deck.drawPrecise(value1, suit1);
                String drawnCard2 = deck.drawPrecise(value2, suit2);

                if (drawnCard1 != null) cardsOp.add(drawnCard1);
                if (drawnCard2 != null) cardsOp.add(drawnCard2);
            }
        }

        // ✅ If no cards were provided → Draw two random cards
        while (cardsOp.size() < 2) {
            String drawnCard = deck.draw(); // Ensure draw() actually removes from deck
            if (drawnCard != null) {
                cardsOp.add(drawnCard);
            } else {
                System.out.println("Error: Deck is empty or draw() returned null.");
            }
        }

        bestHandVillain.addAll(cardsOp);
        return cardsOp;
    }






    public void generateCommunityCards(String flopInput, String turnInput, ArrayList<String> usedCards) {
        this.communityCards = new ArrayList<>();

        // 🧹 Normalize used cards and remove from deck
        for (String card : usedCards) {
            String[] parts = card.split(" ");
            if (parts.length >= 3) {
                deck.removeCard(parts[0], parts[2].toLowerCase());
            }
        }

        // 🔁 Add fixed flop cards
        if (!flopInput.isEmpty()) {
            for (String card : flopInput.split(", ")) {
                if (!usedCards.contains(card)) {
                    communityCards.add(card);
                    usedCards.add(card);
                    String[] parts = card.split(" ");
                    deck.removeCard(parts[0], parts[2].toLowerCase());
                }
            }
        }

        // 🔁 Add fixed turn card
        if (!turnInput.isEmpty() && !usedCards.contains(turnInput)) {
            communityCards.add(turnInput);
            usedCards.add(turnInput);
            String[] parts = turnInput.split(" ");
            deck.removeCard(parts[0], parts[2].toLowerCase());
        }

        // 🃏 Draw remaining community cards
        while (communityCards.size() < 5) {
            String drawn = deck.draw();
            if (drawn != null && !usedCards.contains(drawn)) {
                communityCards.add(drawn);
                usedCards.add(drawn);
            }
        }

        PokerSimulation.usedCards.clear();
    }





    public double getWinProbability(ArrayList<String> playerHand, ArrayList<String> villainHand, ArrayList<String> communityCards) {
        int playerWins = 0;
        int totalSimulations = 1000; // Run 1000 mini-simulations

        for (int i = 0; i < totalSimulations; i++) {
            ArrayList<String> simulatedCommunityCards = new ArrayList<>(communityCards);
            for (String card : communityCards) {
                simulatedCommunityCards.add(card.toLowerCase()); // ✅ Normalize suits
            }
            // Fill missing community cards
            while (simulatedCommunityCards.size() < 5) {
                String drawnCard;
                do {
                    drawnCard = deck.draw();
                } while (simulatedCommunityCards.contains(drawnCard)); // Avoid duplicates
                simulatedCommunityCards.add(drawnCard);
            }

            // Evaluate hands
            HandResult playerResult = findBestFiveCardHand(playerHand);
            HandResult villainResult = findBestFiveCardHand(villainHand);

            int playerScore = evaluateHand(playerResult.bestHand);
            int villainScore = evaluateHand(villainResult.bestHand);

            if (playerScore > villainScore) {
                playerWins++;
            }
        }

        return (double) playerWins / totalSimulations; // Return win probability
    }

    public ArrayList<String> flop() {
        ArrayList<String> flopCards = new ArrayList<>();
        flopCards.add(deck.draw());
        flopCards.add(deck.draw());
        flopCards.add(deck.draw());
        return flopCards;
    }

    public ArrayList<String> turn() {
        ArrayList<String> turnCard = new ArrayList<>();
        turnCard.add(deck.draw());
        return turnCard;
    }

    public ArrayList<String> river() {
        ArrayList<String> riverCard = new ArrayList<>();
        riverCard.add(deck.draw());
        return riverCard;
    }

    public ArrayList<String> communityCards(Ranking ranking) {
        if (this.communityCards == null) {
            this.communityCards = new ArrayList<>();
        }

        for (String card : ranking.flop()) {
            if (!this.communityCards.contains(card)) this.communityCards.add(card);
        }
        for (String card : ranking.turn()) {
            if (!this.communityCards.contains(card)) this.communityCards.add(card);
        }
        for (String card : ranking.river()) {
            if (!this.communityCards.contains(card)) this.communityCards.add(card);
        }

        return this.communityCards; // ✅ Use class-level variable
    }


    public void setCommunityCards(ArrayList<String> presetCards) {
        this.communityCards = new ArrayList<>(presetCards);
    }


    private String getSuit(String card) {
        return card.split(" ")[2].toLowerCase(); // ✅ Normalize suits to lowercase
    }



    public void updateBestHand(ArrayList<String> holeCards, ArrayList<String> bestHand) {
        List<String> allCards = new ArrayList<>(holeCards);
        allCards.addAll(this.communityCards); // ✅ Ensure it uses the stored board

        bestHand.clear();

        if (allCards.size() > 5) {
            HandResult result = findBestFiveCardHand(allCards);
            bestHand.addAll(result.bestHand);
        } else {
            bestHand.addAll(allCards);
        }
    }




    private List<List<String>> generateCombinations(List<String> cards, int k) {
        List<List<String>> combinations = new ArrayList<>();
        generateCombinationsHelper(cards, k, 0, new ArrayList<>(), combinations);
        return combinations;
    }

    private void generateCombinationsHelper(List<String> cards, int k, int start, List<String> temp, List<List<String>> result) {
        if (temp.size() == k) {
            result.add(new ArrayList<>(temp));
            return;
        }
        for (int i = start; i < cards.size(); i++) {
            temp.add(cards.get(i));
            generateCombinationsHelper(cards, k, i + 1, temp, result);
            temp.remove(temp.size() - 1);
        }
    }
    private List<Integer> getSortedCardValues(List<String> hand) {
        List<Integer> values = new ArrayList<>();
        for (String card : hand) {
            values.add(cardValue(card));
        }
        values.sort(Collections.reverseOrder()); // Sort highest to lowest
        return values;
    }



    public int cardValue(String card) {
        String[] parts = card.split(" of "); // Ensure format is "Value of Suit"
        String value = parts[0]; // Extract "Ace", "10", etc.

        value = value.substring(0, 1).toUpperCase() + value.substring(1).toLowerCase(); // Normalize capitalization

        switch (value) {
            case "Ace":
                return 14;
            case "King":
                return 13;
            case "Queen":
                return 12;
            case "Jack":
                return 11;
            default:
                try {
                    return Integer.parseInt(value); // Convert "10" to 10, etc.
                } catch (NumberFormatException e) {
                    throw new IllegalArgumentException("Invalid card value: " + value);
                }
        }
    }



    public class HandResult {
        ArrayList<String> bestHand;
        String handName;

        HandResult(ArrayList<String> bestHand, String handName) {
            this.bestHand = bestHand;
            this.handName = handName;
        }
    }

    public HandResult findBestFiveCardHand(List<String> allCards) {
        if (allCards == null || allCards.size() < 5) {
            System.out.println("⚠️ Error: Not enough cards to form a valid hand.");
            return new HandResult(new ArrayList<>(allCards), "Invalid Hand");
        }

        allCards.sort(Comparator.comparingInt(this::cardValue).reversed());

        ArrayList<String> best = new ArrayList<>();
        String bestHandName = "High Card";
        int bestScore = 0;
// Count suits
        Map<String, Integer> suitCount = new HashMap<>();
        for (String card : allCards) {
            String[] parts = card.split(" ");
            String suit = getSuit(card).toLowerCase(); // Ensure always lowercase
            suitCount.put(suit, suitCount.getOrDefault(suit, 0) + 1);
        }



        // Generate all 5-card combinations
        List<List<String>> combinations = generateCombinations(allCards, 5);

        for (List<String> combo : combinations) {
            int score = evaluateHand(combo);
            String handName = determineHandName(combo);

            if (score> bestScore) {
                bestScore = score;
                best = new ArrayList<>(combo);
                bestHandName = handName;
            }
        }

        if (best.isEmpty()) {
            System.out.println("⚠️ Error: No valid 5-card hand found.");
            return new HandResult(new ArrayList<>(allCards.subList(0, Math.min(5, allCards.size()))), "High Card");
        }

        return new HandResult(best, bestHandName);
    }


    public int evaluateHand(List<String> hand) {
        hand.sort(Comparator.comparingInt(this::cardValue).reversed());



        boolean isFlush = isFlush(hand);
        Map.Entry<Boolean, Integer> straightResult = isStraight(hand);
        boolean isStraight = straightResult.getKey();
        int straightKicker = straightResult.getValue(); // Get highest card in the straight

        Map<Integer, Integer> rankCount = countRanks(hand);

        int score = 0; // ✅ Ensure score is not accumulating across evaluations

        if (isFlush && isStraight && cardValue(hand.get(0)) == 14) {
            score = 100000; // Royal Flush
        } else if (isFlush && isStraight) {
            score = 90000 + cardValue(hand.get(0)); // Straight Flush
        } else if (hasNOfAKind(rankCount, 4)) {
            score = 80000 + getHighestOfAKind(rankCount, 4) * 100 + getHighestKicker(rankCount, hand, 1);
        } else if (hasFullHouse(rankCount)) {
            score = 70000 + getHighestOfAKind(rankCount, 3) * 10 + getHighestOfAKind(rankCount, 2);
        } else if (isFlush) {
            if (score < 60000) {  // ✅ Prevent adding flush score multiple times
                score = 60000 + 100 * cardValue(hand.get(0)) + 50 * cardValue(hand.get(1)) + 20 * cardValue(hand.get(2)) + 10 * cardValue(hand.get(3)) + 5 * cardValue(hand.get(4));
            }
        } else if (isStraight) {
            score = 50000 + straightKicker;
        }

        else if (hasNOfAKind(rankCount, 3)) {
            int triplet = getHighestOfAKind(rankCount, 3);
            int kickerScore = getHighestKicker(rankCount, hand, 2); // top 2 kickers

            // Stronger weighting on triplet to prevent kicker override
            score = 40000 + (triplet * 100) + kickerScore;
        }

        else if (hasTwoPairs(rankCount)) {
            int highestPair = getHighestPair(rankCount);
            int secondPair = getSecondHighestPair(rankCount);
            int kicker = getHighestKicker(rankCount, hand, 1);
            score = 30000 + highestPair * 100 + secondPair * 10 + kicker;
        }
        else if (hasNOfAKind(rankCount, 2)) {
            int highestPair = getHighestOfAKind(rankCount, 2);
            int kickerScore = getHighestKicker(rankCount, hand, 3); // Ensure correct ranking
            score = 20000 + highestPair * 100 + kickerScore;
        }
        else {
            score = 10000 + cardValue(hand.get(0)); // ✅ FIXED: Only use the highest card, not `getHighCardStrength`
        }

        return score; // ✅ Ensures only ONE score is assigned, no accumulation!
    }


    private int getSecondHighestPair(Map<Integer, Integer> rankCount) {
        List<Integer> pairs = new ArrayList<>();

        // Find all ranks that appear exactly twice (pairs)
        for (Map.Entry<Integer, Integer> entry : rankCount.entrySet()) {
            if (entry.getValue() == 2) {
                pairs.add(entry.getKey());
            }
        }

        // Sort pairs in descending order
        pairs.sort(Collections.reverseOrder());

        // Ensure there are at least two pairs
        if (pairs.size() < 2) {
            throw new IllegalStateException("Less than two pairs found in the hand.");
        }

        // Return the second highest pair
        return pairs.get(1);
    }





    private int getHighCardStrength(List<String> hand) {
        List<Integer> values = getSortedCardValues(hand);
        int score = 0, multiplier = 10000;

        for (int i = 0; i < Math.min(values.size(), 5); i++) {
            score += values.get(i) * multiplier;
            multiplier /= 10; // Weighting factor ensures strongest high cards count more
        }
        return score;
    }




    private int getHighestKicker(Map<Integer, Integer> rankCount, List<String> hand, int needed) {
        List<Integer> kickers = getSortedCardValues(hand);
        List<Integer> availableKickers = new ArrayList<>();

        for (int value : kickers) {
            if (!rankCount.containsKey(value) || rankCount.get(value) == 1) {
                availableKickers.add(value);
            }
        }

        int score = 0, multiplier = 10;
        for (int i = 0; i < Math.min(needed, availableKickers.size()); i++) {
            score += availableKickers.get(i) * multiplier;
            multiplier /= 10;
        }

        return score;
    }




    private int getHighCardScore(List<String> hand) {
        List<Integer> values = getSortedCardValues(hand);
        int score = 0, multiplier = 1;

        for (int i = values.size() - 1; i >= 0; i--) {
            score += values.get(i) * multiplier;
            multiplier *= 10; // Weighting factor ensures strongest high cards count more
        }
        return score;
    }



    private String determineHandName(List<String> hand) {
        boolean isFlush = isFlush(hand);
        Map.Entry<Boolean, Integer> straightResult = isStraight(hand);
        boolean isStraight = straightResult.getKey();
        int straightKicker = straightResult.getValue(); // Get highest card in the straight

        Map<Integer, Integer> rankCount = countRanks(hand);

        if (isFlush && isStraight && cardValue(hand.get(0)) == 14) return "Royal Flush";
        if (isFlush && isStraight) return "Straight Flush";
        if (hasNOfAKind(rankCount, 4)) return "Four of a Kind";
        if (hasFullHouse(rankCount)) return "Full House";
        if (isFlush) return "Flush";
        if (isStraight) return "Straight";
        if (hasNOfAKind(rankCount, 3)) return "Three of a Kind";
        if (hasTwoPairs(rankCount)) return "Two Pair";
        if (hasNOfAKind(rankCount, 2)) return "One Pair";

        return "High Card";
    }


    private boolean isFlush(List<String> hand) {
        Map<String, List<Integer>> suitGroups = new HashMap<>();

        for (String card : hand) {
            String suit = getSuit(card).toLowerCase();
            int value = cardValue(card);

            suitGroups.putIfAbsent(suit, new ArrayList<>());
            suitGroups.get(suit).add(value);
        }

        for (String card : hand) {
            String suit = getSuit(card);

        }

        // Find the flush suit with at least 5 cards
        for (List<Integer> values : suitGroups.values()) {
            if (values.size() >= 5) {
                values.sort(Collections.reverseOrder()); // Sort high to low
                return true;
            }
        }
        return false;
    }



    private Map.Entry<Boolean, Integer> isStraight(List<String> hand) {
        List<Integer> values = getSortedCardValues(hand);
        Collections.sort(values);
        values = values.stream().distinct().collect(Collectors.toList());

        // Ace-low straight check
        if (values.contains(14) && values.contains(2) && values.contains(3) && values.contains(4) && values.contains(5)) {
            return Map.entry(true, 5);  // Kicker is 5
        }

        // Normal straight check
        for (int i = 0; i <= values.size() - 5; i++) {
            if (values.get(i) + 1 == values.get(i + 1) &&
                    values.get(i + 1) + 1 == values.get(i + 2) &&
                    values.get(i + 2) + 1 == values.get(i + 3) &&
                    values.get(i + 3) + 1 == values.get(i + 4)) {
                return Map.entry(true, values.get(i + 4));  // ✅ Highest card in straight
            }
        }

        return Map.entry(false, 0);  // ❌ No straight
    }






    private Map<Integer, Integer> countRanks(List<String> hand) {
        Map<Integer, Integer> rankCount = new HashMap<>();
        for (String card : hand) {
            int value = cardValue(card);
            rankCount.put(value, rankCount.getOrDefault(value, 0) + 1);
        }
        return rankCount;
    }

    private boolean hasNOfAKind(Map<Integer, Integer> rankCount, int n) {
        return rankCount.values().contains(n);
    }

    private boolean hasFullHouse(Map<Integer, Integer> rankCount) {
        return rankCount.values().contains(3) && rankCount.values().contains(2);
    }

    private boolean hasTwoPairs(Map<Integer, Integer> rankCount) {
        return rankCount.values().stream().filter(v -> v == 2).count() == 2;
    }

    private int getHighestOfAKind(Map<Integer, Integer> rankCount, int n) {
        return rankCount.entrySet().stream()
                .filter(entry -> entry.getValue() == n)
                .map(Map.Entry::getKey)
                .max(Integer::compareTo)
                .orElse(0);
    }

    private int getHighestPair(Map<Integer, Integer> rankCount) {
        return rankCount.entrySet().stream()
                .filter(entry -> entry.getValue() == 2)
                .map(Map.Entry::getKey)
                .max(Integer::compareTo)
                .orElse(0);
    }

}