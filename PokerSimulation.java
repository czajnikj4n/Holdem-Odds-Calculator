package org.example;

import java.util.*;

public class PokerSimulation {
    public static ArrayList<String> usedCards = new ArrayList<>();


    /**
     * The main method within this class is mostly used for debugs & pre-gui checks. For full experience run
     * Poker GUI main.
     */

    public static void main(String[] args) {
        usedCards.clear();
        Scanner scanner = new Scanner(System.in);

        // Ask for number of players
        System.out.println("Enter number of players:");
        int numPlayers = scanner.nextInt();
        scanner.nextLine();


        List<String> allPlayerCards = new ArrayList<>();
        for (int i = 0; i < numPlayers; i++) {
            System.out.println("Enter hole cards for Player " + (i + 1) + " (or press Enter to randomize):");
            String input = scanner.nextLine();
            usedCards.add(input.trim());

            if (!input.isEmpty()) {
                String[] cards = input.trim().split(", ");
                usedCards.addAll(Arrays.asList(cards));
            }
        }

        // Optional community cards
        System.out.println("Enter flop cards (or press enter to randomize):");
        String flopInput = scanner.nextLine();

        System.out.println("Enter turn card (or press enter to randomize):");
        String turnInput = scanner.nextLine();

        // Number of simulations
        System.out.println("Enter number of simulations:");
        int simulations = scanner.nextInt();

        String result = runSimulations(allPlayerCards, flopInput, turnInput, simulations);
        System.out.println(result);

    }

    /**
     This Method handles the main Simulation mechanism, it takes pre-set cards as inputs,
     alongside the number of simulations. The default GUI setting is n = 10000 which is enough for convergence.
     */

    public static String runSimulations(List<String> playerCardInputs, String flopInput, String turnInput, int n) {
        PokerSimulation.usedCards.clear();

        int numPlayers = playerCardInputs.size();
        double[] pointsPerPlayer = new double[numPlayers];

        StringBuilder resultText = new StringBuilder();

        for (int i = 0; i < n; i++) {
            Ranking ranking = new Ranking();
            List<ArrayList<String>> allPlayersHands = new ArrayList<>();

            // Initialize player hands
            for (int p = 0; p < numPlayers; p++) {
                String input = playerCardInputs.get(p);
                ArrayList<String> hand = new ArrayList<>();



                while (hand.size() < 2) {
                    hand.add(ranking.deck.draw());
                }

                allPlayersHands.add(hand);
            }

            // Set fixed community cards if specified
            ArrayList<String> communityCards = new ArrayList<>();

            if (!flopInput.isEmpty()) {
                String[] flopCards = flopInput.split(", ");
                for (String card : flopCards) {
                    communityCards.add(card);
                    String[] parts = card.split(" ");
                    ranking.deck.removeCard(parts[0], parts[2]);
                }
            }

            if (!turnInput.isEmpty()) {
                communityCards.add(turnInput);
                String[] parts = turnInput.split(" ");
                ranking.deck.removeCard(parts[0], parts[2]);
            }

            for (String card : usedCards){
                String[] parts = card.split(" ");
                ranking.deck.removeCard(parts[0], parts[2]);

            }

            // Generate remaining community cards
            ranking.generateCommunityCards(flopInput, turnInput, usedCards);

            communityCards = ranking.communityCards;
            ranking.setCommunityCards(communityCards);


            // Evaluate all players
            List<Ranking.HandResult> results = new ArrayList<>();
            List<Integer> scores = new ArrayList<>();

            for (ArrayList<String> hand : allPlayersHands) {
                ArrayList<String> fullHand = new ArrayList<>(hand);
                fullHand.addAll(communityCards);

                Ranking.HandResult result = ranking.findBestFiveCardHand(fullHand);
                results.add(result);
                scores.add(ranking.evaluateHand(result.bestHand));
            }

            // Find winners
            int maxScore = Collections.max(scores);
            List<Integer> winners = new ArrayList<>();
            for (int p = 0; p < numPlayers; p++) {
                if (scores.get(p) == maxScore) {
                    winners.add(p);
                }
            }

            // Assign points (split in case of ties)
            double pointPerWinner = 1.0 / winners.size();
            for (int idx : winners) {
                pointsPerPlayer[idx] += pointPerWinner;
            }

            //For detailed debug
            boolean enableDebugOutput = true; //False for no soutout's

            if (enableDebugOutput) {
                System.out.println("🧪 DEBUG ROUND " + (i + 1));
                System.out.println("Community Cards this round: " + communityCards);
                System.out.printf("%-35s | %-7s | %-16s | %-60s%n", "Hole Cards", "Score", "Hand Type", "Best 5-Card Hand");
                System.out.println("---------------------------------------------------------------------------------------------------------------");

                List<String> debugLines = new ArrayList<>();
                for (int p = 0; p < numPlayers; p++) {
                    Ranking.HandResult res = results.get(p);
                    int score = scores.get(p);
                    String handName = res.handName.toLowerCase();

                    String holeCardsStr = String.join(", ", allPlayersHands.get(p).subList(0, 2));
                    String bestHandStr = String.join(", ", res.bestHand);

                    // Use fixed-width formatting
                    String line = String.format("%-35s | %-7d | %-16s | %-60s",
                            holeCardsStr, score, handName, bestHandStr);
                    debugLines.add(line);
                }

                // Sort by score descending
                debugLines.sort((a, b) -> {
                    int scoreA = Integer.parseInt(a.split("\\|")[1].trim());
                    int scoreB = Integer.parseInt(b.split("\\|")[1].trim());
                    return Integer.compare(scoreB, scoreA);
                });

                for (String line : debugLines) {
                    System.out.println(line);
                }

                // Winner(s) line
                System.out.print("Winner(s) this round: ");
                for (int w : winners) {
                    String holeCardsStr = String.join(", ", allPlayersHands.get(w).subList(0, 2));
                    System.out.print(holeCardsStr + " | ");
                }
                System.out.println("\n---------------------------------------------------------------------------------------------------------------");
            }
        }

        // Compile final summary
        resultText.append("✅ Simulation Complete!\n")
                .append("Total Simulations: ").append(n).append("\n\n");

        double maxPoints = -1;
        List<Integer> overallWinners = new ArrayList<>();

        for (int i = 0; i < numPlayers; i++) {
            resultText.append("Player ").append(i + 1)
                    .append(" Win Rate: ")
                    .append(String.format("%.2f", (pointsPerPlayer[i] / n) * 100))
                    .append("%\n");

            if (pointsPerPlayer[i] > maxPoints) {
                maxPoints = pointsPerPlayer[i];
                overallWinners.clear();
                overallWinners.add(i);
            } else if (pointsPerPlayer[i] == maxPoints) {
                overallWinners.add(i);
            }


        }

        // Declare winner(s)
        if (overallWinners.size() == 1) {
            resultText.append("\n🏆 Player ").append(overallWinners.get(0) + 1).append(" is the overall winner!");
        } else {
            resultText.append("\n🤝 It's a draw between players: ");
            for (int idx : overallWinners) {
                resultText.append((idx + 1)).append(" ");
            }
        }
        return resultText.toString();
    }

}


